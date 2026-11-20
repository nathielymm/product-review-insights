"""Aggregate fallible reference alignment without changing original RAG outputs."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from product_review_insights import generation
from report_product_original_pilot import check_translation_structure
from run_product_reference_pilot import source_units, statement_blocks, validate_audit


def report(spec_path):
    spec=json.loads(Path(spec_path).read_text());root=Path(spec['results']);base=Path(spec['baseline_results'])
    if json.loads((root/'reference-audit-status.private.json').read_text())['status']!='complete':raise ValueError('Incomplete source audit')
    rows=[json.loads(l) for l in (root/'runs.private.jsonl').read_text().splitlines()];audits=[json.loads(l) for l in (root/'reference-audits.private.jsonl').read_text().splitlines()]
    old=[json.loads(l) for l in (base/'runs.private.jsonl').read_text().splitlines()]
    expected={(q['id'],m) for q in spec['questions'] for m in ['traditional','thematic']}
    if any(len(x)!=4 or {(r['question_id'],r['method']) for r in x}!=expected for x in [rows,audits,old]):raise ValueError('Incomplete grid')
    before={(r['question_id'],r['method']):r for r in old};by_audit={(r['question_id'],r['method']):r for r in audits};outcomes=[]
    for row in rows:
        key=(row['question_id'],row['method']);previous=before[key];audit=by_audit[key]
        if row['candidate_pool_sha256']!=previous['candidate_pool_sha256'] or [(h['id'],h['text']) for h in row['evidence']]!=[(h['id'],h['text']) for h in previous['evidence']]:raise ValueError('Retrieval changed')
        english=row['english'];translated=row['translation'];data=(english or {}).get('structured_output')
        if english and english['generation_contract']['system_prompt']!=generation.STRUCTURED_SYSTEM:raise ValueError('Original prompt changed')
        if translated and translated.get('valid') and not check_translation_structure(data,translated['structured_pt']):raise ValueError('Translation changed structure/citations')
        units=source_units(row['evidence'])
        if units!=audit['source_units']:raise ValueError('Original source unit text changed')
        blocks=statement_blocks(data) if data else []
        if [c['block'] for c in audit['calls']]!=blocks:raise ValueError('Generated statements changed')
        unitmap={u['id']:u for u in units};statuses=Counter();reasons=Counter();changed=0;outside=0;valid=0;statements=0
        for call in audit['calls']:
            statements+=len(call['block']['statements'])
            if not call['valid']:continue
            labels=validate_audit(call['raw_model_output'],call['block'],units)
            if labels!=call['labels']:raise ValueError('Audit labels changed')
            valid+=len(labels)
            for item in labels.values():
                statuses[item['status']]+=1;reasons[item['reason']]+=1
                proposed={unitmap[u]['evidence_id'] for u in item['source_units']};original=set(call['block']['original_citations'])
                changed+=bool(proposed!=original);outside+=bool(proposed-original)
        calls=audit['calls'];penglish=previous['english']
        outcomes.append({'question_id':row['question_id'],'method':row['method'],'context_matches_round_6':True,
          'english_raw_identical_to_round_6':bool(english and penglish and english['raw_model_output']==penglish['raw_model_output']),
          'english_valid':(english or {}).get('structured_validation',{}).get('valid'),'english_cut':(english or {}).get('ollama',{}).get('done_reason')=='length',
          'translation_valid':(translated or {}).get('valid',False),'translation_cut':(translated or {}).get('ollama',{}).get('done_reason')=='length',
          'audit_calls':len(calls),'valid_audit_calls':sum(c['valid'] for c in calls),'cut_audit_calls':sum(c['ollama'].get('done_reason')=='length' for c in calls),
          'error_audit_calls':sum(bool(c['generation_error']) for c in calls),'statements_presented_for_audit':statements,'statements_with_parseable_labels':valid,
          'automatic_status_counts_not_semantic_truth':dict(statuses),'automatic_reason_counts_not_semantic_truth':dict(reasons),
          'proposed_source_sets_different_from_original':changed,'proposed_sources_outside_original_citations':outside,
          'generation_seconds':row['generation_seconds'],'translation_seconds':(translated or {}).get('total_seconds',0),'audit_seconds':audit['total_seconds'],
          'generation_and_translation_seconds':row['total_seconds'],'audit_tokens':{k:sum(c['ollama'][k] for c in calls if c['ollama'].get(k) is not None) for k in ['prompt_eval_count','eval_count']},
          'audit_token_missing':{k:sum(c['ollama'].get(k) is None for c in calls) for k in ['prompt_eval_count','eval_count']},
          'original_english_and_citations_replaced':False})
    provenance=json.loads((root/'reference-audit-provenance.private.json').read_text())
    if provenance['original_runs_sha256']!=hashlib.sha256((root/'runs.private.jsonl').read_bytes()).hexdigest():raise ValueError('Original run was rewritten')
    return {'schema':'product_reference_audit_pilot_v7_aggregates','role':'development_only','product_id':spec['product_id'],
       'answers':4,'generation_calls':4,'translation_calls':sum(bool((r['translation'] or {}).get('attempted')) for r in rows),
       'audit_calls':sum(o['audit_calls'] for o in outcomes),'outcomes':outcomes,
       'spec_sha256':hashlib.sha256(Path(spec_path).read_bytes()).hexdigest(),'original_runs_sha256':provenance['original_runs_sha256'],
       'audit_runs_sha256':hashlib.sha256((root/'reference-audits.private.jsonl').read_bytes()).hexdigest(),
       'interpretation':'Same-model automatic source-unit alignment is fallible, not independent evaluation or proof. Original sentences and citations are unchanged; proposed links and alerts are separate. Counts are not fidelity/depth scores or corrected-source claims. Manual review of errors required.',
       'resources':'Audit adds separate wall time/tokens; original generation and presentation remain distinct. No process/memory monitoring.'}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--spec',default='configs/curly-product-pilot.v7-reference-audit.json');p.add_argument('--output',required=True);a=p.parse_args()
    output=Path(a.output)
    if output.exists():raise FileExistsError('Preserve prior report; use new destination')
    data=report(a.spec);output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':main()
