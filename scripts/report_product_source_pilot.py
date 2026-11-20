"""Aggregate isolated-source round and compare resource cost with round three."""
import argparse
import hashlib
import json
from pathlib import Path


def check_source_binding(row):
    by_id={h['citation_id']:h for h in row['evidence']};calls=row['source_calls']
    if len(calls)!=len(by_id) or {c['source_id'] for c in calls}!=set(by_id):return False
    expected=[]
    for call in calls:
        alias=call['source_id'];source=by_id[alias]
        request=json.loads(call['payload']['messages'][1]['content'])
        if set(request)!={'idioma_resposta','pergunta','permitir_melhorias','unica_avaliacao'}:return False
        if request['unica_avaliacao']!=source['text']:return False
        if call['format_valid'] and call['structured']['relato']:expected.append({**call['structured'],'fonte':alias})
    if row['structured']['achados']!=expected:return False
    cited={f['fonte'] for f in expected};material=row['source_material']
    return len(material)==len(cited) and {m['evidence_id'] for m in material}==cited and all(
        m=={'evidence_id':m['evidence_id'],'product_id':by_id[m['evidence_id']]['product_id'],
            'review_id':by_id[m['evidence_id']]['review_id'],'text':by_id[m['evidence_id']]['text']} for m in material)


def report(spec_path):
    spec=json.loads(Path(spec_path).read_text());root=Path(spec['results']);base=Path(spec['baseline_results'])
    if json.loads((root/'status.private.json').read_text())['status']!='complete':raise ValueError('Incomplete run')
    rows=[json.loads(l) for l in (root/'runs.private.jsonl').read_text().splitlines()]
    old=[json.loads(l) for l in (base/'runs.private.jsonl').read_text().splitlines()]
    expected={(q['id'],m) for q in spec['questions'] for m in ['traditional','thematic']}
    if len(rows)!=4 or len(old)!=4 or {(r['question_id'],r['method']) for r in rows}!=expected or {(r['question_id'],r['method']) for r in old}!=expected:raise ValueError('Incomplete grid')
    prior={(r['question_id'],r['method']):r for r in old};outcomes=[]
    for row in rows:
        previous=prior[(row['question_id'],row['method'])]
        if row['candidate_pool_sha256']!=previous['candidate_pool_sha256'] or [(h['id'],h['text']) for h in row['evidence']]!=[(h['id'],h['text']) for h in previous['evidence']]:raise ValueError('Context changed')
        if any(h['product_id']!=spec['product_id'] for h in row['evidence']):raise ValueError('Foreign product')
        if not check_source_binding(row):raise ValueError('Source binding failed')
        calls=row['source_calls'];findings=row['structured']['achados'];cited={f['fonte'] for f in findings}
        caps=[c['output_token_cap'] for c in calls]
        if sum(caps)!=spec['config']['num_predict']:raise ValueError('Shared output cap changed')
        outcomes.append({'question_id':row['question_id'],'method':row['method'],'included_reviews':len({h['review_id'] for h in row['evidence']}),
           'new_findings':len(findings),'cited_unique_reviews':len({h['review_id'] for h in row['evidence'] if h['citation_id'] in cited}),
           'source_calls':len(calls),'valid_source_calls':sum(c['format_valid'] for c in calls),
           'empty_source_calls':sum(c['format_valid'] and not c['structured']['relato'] for c in calls),
           'cut_source_calls':row['cut_source_calls'],'error_source_calls':sum(bool(c['generation_error']) for c in calls),
           'answer_contract_valid':row['format_valid'],'source_binding_verified':True,'context_matches_round_3':True,
           'planned_answer_output_token_cap':sum(caps),'source_output_token_caps':caps,
           'new_total_seconds':row['total_seconds'],'previous_total_seconds':previous['total_seconds'],
           'new_prompt_tokens':row['ollama']['prompt_eval_count'],'previous_prompt_tokens':previous['ollama'].get('prompt_eval_count'),
           'new_output_tokens':row['ollama']['eval_count'],'previous_output_tokens':previous['ollama'].get('eval_count'),
           'previous_findings':len(previous['structured']['achados']) if previous['structured'] else None,
           'nonempty_suspicion_fields_not_validated':sum(bool(f['suspeita']) for f in findings),
           'resources_missing':{key:sum(c['ollama'].get(key) is None for c in calls) for key in ['prompt_eval_count','eval_count']}})
    shared=[]
    for q in spec['questions']:
        a,b=[r for r in rows if r['question_id']==q['id']]
        def mapped(row):
            by_id={h['citation_id']:h['review_id'] for h in row['evidence']}
            return {by_id[c['source_id']]:c['raw_model_output'] for c in row['source_calls']}
        aa,bb=mapped(a),mapped(b);common=set(aa)&set(bb)
        shared.append({'question_id':q['id'],'common_reviews':len(common),'identical_raw_outputs_for_common_reviews':sum(aa[i]==bb[i] for i in common)})
    provenance=json.loads((root/'provenance.private.json').read_text());p3=json.loads((base/'provenance.private.json').read_text())
    assert provenance['model_digest']==p3['model_digest'] and provenance['index_metadata_sha256']==p3['index_metadata_sha256']
    assert provenance['baseline_runs_sha256']==hashlib.sha256((base/'runs.private.jsonl').read_bytes()).hexdigest()
    return {'schema':'source_isolated_product_pilot_v4_aggregates','role':'development_only','product_id':spec['product_id'],
        'answers':4,'source_calls':sum(o['source_calls'] for o in outcomes),'repetitions_per_combination':1,
        'spec_sha256':hashlib.sha256(Path(spec_path).read_bytes()).hexdigest(),'runs_sha256':hashlib.sha256((root/'runs.private.jsonl').read_bytes()).hexdigest(),
        'baseline_runs_sha256':provenance['baseline_runs_sha256'],'model_digest':provenance['model_digest'],
        'index_metadata_sha256':provenance['index_metadata_sha256'],'outcomes':outcomes,'common_review_output_comparison':shared,
        'interpretation':'Mechanical source isolation/binding is not entailment. One model call per source changes input cost, latency and synthesis; findings cap 8 vs prior 6. Same total planned output cap, not same workload. No independent semantic score, causal attribution or winner.'}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--spec',default='configs/curly-product-pilot.v4-source-isolated.json');p.add_argument('--output',required=True);a=p.parse_args()
    output=Path(a.output)
    if output.exists():raise FileExistsError('Preserve report; use new output')
    data=report(a.spec);output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':main()
