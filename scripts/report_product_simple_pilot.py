"""Aggregate round-three source-identity checks; never export individual review text."""
import argparse
import hashlib
import json
from pathlib import Path


def source_identity_check(row):
    if not row['format_valid']:return None
    by_id={h['citation_id']:h for h in row['evidence']}
    cited={f['fonte'] for f in row['structured']['achados']}
    material=row['source_material']
    return (len(material)==len(cited) and {m['evidence_id'] for m in material}==cited
        and all(m=={'evidence_id':alias,'product_id':by_id[alias]['product_id'],
                    'review_id':by_id[alias]['review_id'],'text':by_id[alias]['text']}
                for m in material for alias in [m['evidence_id']]))


def report(spec_path):
    spec=json.loads(Path(spec_path).read_text());root=Path(spec['results']);base=Path(spec['baseline_results'])
    state=json.loads((root/'status.private.json').read_text())
    if state['status']!='complete':raise ValueError('Incomplete generation')
    rows=[json.loads(l) for l in (root/'runs.private.jsonl').read_text().splitlines()]
    baseline=[json.loads(l) for l in (base/'runs.private.jsonl').read_text().splitlines()]
    expected={(q['id'],m) for q in spec['questions'] for m in ['traditional','thematic']}
    if len(rows)!=4 or len(baseline)!=4 or {(r['question_id'],r['method']) for r in rows}!=expected:raise ValueError('Incomplete grid')
    prior={(r['question_id'],r['method']):r for r in baseline}
    if set(prior)!=expected:raise ValueError('Incomplete baseline')
    outcomes=[]
    for row in rows:
        old=prior[(row['question_id'],row['method'])]
        if row['candidate_pool_sha256']!=old['candidate_pool_sha256'] or [(h['id'],h['text']) for h in row['evidence']]!=[(h['id'],h['text']) for h in old['evidence']]:raise ValueError('Retrieval/context changed')
        if any(h['product_id']!=spec['product_id'] for h in row['evidence']):raise ValueError('Foreign product')
        identity=source_identity_check(row)
        if identity is False:raise ValueError('Original source material changed')
        data=row['structured'];cited={f['fonte'] for f in data['achados']} if data else set()
        outcomes.append({'question_id':row['question_id'],'method':row['method'],'included_reviews':len({h['review_id'] for h in row['evidence']}),
            'findings':len(data['achados']) if data else None,
            'cited_reviews':len({h['review_id'] for h in row['evidence'] if h['citation_id'] in cited}) if data else None,
            'format_valid':row['format_valid'],'generation_error':bool(row['generation_error']),
            'cut':row['ollama'].get('done_reason')=='length','original_sources_identical':identity,
            'context_matches_round_2':True,'total_seconds':row['total_seconds'],'retrieval_seconds':row['retrieval_seconds'],
            'prompt_tokens':row['ollama'].get('prompt_eval_count'),'output_tokens':row['ollama'].get('eval_count')})
    p=json.loads((root/'provenance.private.json').read_text());p2=json.loads((base/'provenance.private.json').read_text())
    assert p['model_digest']==p2['model_digest'] and p['index_metadata_sha256']==p2['index_metadata_sha256']
    assert p['baseline_runs_sha256']==hashlib.sha256((base/'runs.private.jsonl').read_bytes()).hexdigest()
    return {'schema':'product_simple_pilot_aggregates_v3','role':'development_only_not_final_evaluation','product_id':spec['product_id'],
        'reviews':spec['expected_reviews'],'attempts':4,'repetitions_per_combination':1,
        'spec_sha256':hashlib.sha256(Path(spec_path).read_bytes()).hexdigest(),
        'runs_sha256':hashlib.sha256((root/'runs.private.jsonl').read_bytes()).hexdigest(),'baseline_runs_sha256':p['baseline_runs_sha256'],
        'model_digest':p['model_digest'],'index_metadata_sha256':p['index_metadata_sha256'],'runtime':p['runtime_version'],
        'outcomes':outcomes,'interpretation':'Source text identity and JSON validity do not establish semantic support, Portuguese language or depth. Qualitative language/meaning review is separate; no independent scoring or winner. One attempt, fixed order, no warmup/retry/translation/repair.',
        'changes':spec['changes'],'resources':'wall times and Ollama tokens only; no process/memory monitoring','frozen_experiments_changed':False}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--spec',default='configs/curly-product-pilot.v3-simple.json');p.add_argument('--output',required=True);a=p.parse_args()
    dest=Path(a.output)
    if dest.exists():raise FileExistsError('Use a new report destination')
    dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(report(a.spec),ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':main()
