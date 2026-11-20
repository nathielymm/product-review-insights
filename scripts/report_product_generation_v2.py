from pathlib import Path
from collections import Counter
import json
import argparse
from product_review_insights.data import digest_file
from product_review_insights.evaluation_v2 import fingerprint
from product_review_insights.scoring_v2 import stability_summary,resource_summary,technical_resource_summary
def main():
    parser=argparse.ArgumentParser(description='Verify and report completed v2 generation; no semantic scoring or new model calls.')
    parser.add_argument('--runs',default='results/product-evaluation-v2/final-run')
    parser.add_argument('--freeze',default='configs/evaluation-freeze.v2.json')
    parser.add_argument('--output',required=True)
    parser.add_argument('--answers-output',required=True,help='Local private Markdown with unblinded answers and sources; do not publish before sample review.')
    args=parser.parse_args()
    root=Path(args.runs);status=json.loads((root/'status.private.json').read_text());assert status['status']=='complete','Do not report unfinished run'
    rows=[json.loads(l) for l in (root/'runs.private.jsonl').read_text().splitlines()];translations=[json.loads(l) for l in (root/'translations.private.jsonl').read_text().splitlines()]
    assert len(rows)==60 and len(translations)==36
    assert digest_file(root/'runs.private.jsonl')==status['runs_sha256'] and digest_file(root/'translations.private.jsonl')==status['translations_sha256']
    byid={r['attempt_id']:r for r in rows};trmap={t['attempt_id']:t for t in translations}
    for t in translations:assert t['english_sha256']==fingerprint(byid[t['attempt_id']]['english'])
    probes_path=root/'technical-probes.private.jsonl';probes=[json.loads(l) for l in probes_path.read_text().splitlines()] if probes_path.exists() else []
    assert (digest_file(probes_path) if probes_path.exists() else None)==status['technical_probes_sha256']
    prior=json.loads(Path('results/product-evaluation-v2/freeze-v1/prior-preservation.private.json').read_text());assert all(digest_file(p)==h for p,h in prior.items())
    freeze=json.loads(Path(args.freeze).read_text());assert all(digest_file(p)==h for p,h in freeze['file_hashes'].items())
    config=json.loads(Path(freeze['configuration']).read_text());names={p['product_id']:p['label'] for p in config['products']}
    main=[r for r in rows if r['phase']=='primary'];groups=[]
    for pid in names:
     for method in ['traditional','thematic']:
      rs=[r for r in main if r['product_id']==pid and r['method']==method];ts=[trmap[r['attempt_id']]['translation'] for r in rs]
      groups.append({'product_id':pid,'label':names[pid],'method':method,'scheduled_primary':len(rs),
       'english_format_valid':sum((r.get('english') or {}).get('structured_validation',{}).get('valid',False) for r in rs),
       'retrieval_errors':sum(bool(r['retrieval_error']) for r in rs),'generation_errors':sum(bool(r['generation_error']) for r in rs),
       'english_cut':sum((r.get('english') or {}).get('ollama',{}).get('done_reason')=='length' for r in rs),
       'translation_attempted':sum(t.get('attempted',False) for t in ts),'translation_valid':sum(t.get('valid',False) for t in ts),
       'translation_cut':sum(t.get('ollama',{}).get('done_reason')=='length' for t in ts)})
    summary={'schema':'product_evaluation_v2_generation_summary','status':'frozen_generation_complete_semantic_annotation_pending',
    'freeze_sha256':digest_file(args.freeze),'configuration_sha256':digest_file(freeze['configuration']),
    'english_records':len(rows),'primary_English':len(main),'diagnostic_English':len(rows)-len(main),'presentation_records':len(translations),
    'primary_groups':groups,'all_English_format_valid':sum((r.get('english') or {}).get('structured_validation',{}).get('valid',False) for r in rows),
    'all_English_cut':sum((r.get('english') or {}).get('ollama',{}).get('done_reason')=='length' for r in rows),
    'all_English_execution_errors':sum(bool(r['retrieval_error'] or r['generation_error']) for r in rows),
    'presentation_valid':sum(t['translation'].get('valid',False) for t in translations),
    'presentation_execution_errors':sum(bool(t['translation'].get('generation_error')) for t in translations),
    'presentation_cut':sum(t['translation'].get('ollama',{}).get('done_reason')=='length' for t in translations),
    'English_preserved_after_presentation':True,'previous_files_preserved':len(prior),'frozen_inputs_verified':len(freeze['file_hashes']),
    'output_hashes':{'English':status['runs_sha256'],'presentation':status['translations_sha256'],'technical_probes':status['technical_probes_sha256']},
    'resources':resource_summary(rows,translations),'technical_probes':technical_resource_summary(probes),
    'stability':stability_summary(rows),'semantic_scores_calculated':False,
    'limitations':'Format/cut/execution checks and identical output counts are not fidelity, depth or improvement-effectiveness results. All attempts preserved; no retries/repair or choosing the best response.'}
    public_path=Path(args.output);assert not public_path.exists();public_path.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    # Human-readable local answers: untouched automatic presentation plus original English and evidence.
    output=Path(args.answers_output);assert not output.exists()
    qdoc=json.loads(Path(config['questions']['path']).read_text());qmap={(p['product_id'],q['id']):q for p in qdoc['products'] for q in p['questions']}
    lines=['# Respostas principais — avaliação v2 congelada','','36 respostas principais dos dois RAGs. Inglês original e tradução automática de apresentação preservados. Tradução e validade de formato não certificam fidelidade. IDs E são locais a cada resposta. Os trechos abaixo são exatamente os enviados ao modelo após a segmentação/normalização do encoder, não reprodução literal do Parquet.','','As 24 execuções diagnósticas ficam nos arquivos privados e no relatório agregado de estabilidade; não substituem estas respostas principais.','']
    def quote(text):return '\n'.join('> '+line for line in str(text).splitlines())
    for pid,label in names.items():
     lines+=['## '+label,'']
     for qid in [f'Q{i}' for i in range(1,7)]:
      lines+=['### '+qid,'',qmap[(pid,qid)]['question_pt'],'']
      for method,display in [('traditional','RAG tradicional'),('thematic','RAG temático')]:
       row=next(r for r in main if r['product_id']==pid and r['question_id']==qid and r['method']==method);english=row.get('english') or {};tr=trmap[row['attempt_id']]['translation']
       lines+=['#### '+display,'','Apresentação em português:','']
       if tr.get('valid'):lines += [quote(tr.get('answer_pt','')),'']
       else:lines += ['Tradução indisponível ou inválida; preservada sem reparo. Consulte o inglês abaixo.','']
       lines+=['Original inglês:','',quote(english.get('answer') or english.get('raw_model_output') or row['generation_error'] or row['retrieval_error'] or 'Sem resposta.'),'']
       lines+=['Fontes incluídas no contexto:','']
       for e in row['evidence']:lines+=[f"{e['citation_id']} — avaliação local {e['review_id'][:12]}",'',quote(e['text']),'']
    output.write_text('\n'.join(lines)+'\n')
    print(json.dumps({k:summary[k] for k in ['status','english_records','primary_English','diagnostic_English','all_English_format_valid','all_English_cut','all_English_execution_errors','presentation_valid','presentation_execution_errors','presentation_cut','previous_files_preserved']},ensure_ascii=False))

if __name__=='__main__':main()
