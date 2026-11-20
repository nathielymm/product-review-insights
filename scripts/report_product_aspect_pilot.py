"""Compare pilot aggregates without publishing individual evidence or repairing outputs."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from run_product_aspect_pilot import atomic_schema


def summarize(row, round_name, question=None, limits=None):
    evidence=row['evidence'];by_id={h['citation_id']:h for h in evidence}
    result={'round':round_name,'question_id':row['question_id'],'method':row['method'],
        'included_reviews':len({h['review_id'] for h in evidence}),
        'clusters_in_context':dict(Counter(h['cluster'] for h in evidence)),
        'total_seconds':row['total_seconds'],'prompt_tokens':row['ollama'].get('prompt_eval_count'),
        'output_tokens':row['ollama'].get('eval_count'),'cut':row['ollama'].get('done_reason')=='length',
        'generation_error':bool(row['generation_error']),'contract_valid':row['format_valid']}
    if round_name=='v1':
        findings=[f for group in (row['structured'] or {}).get('groups',{}).values() for f in group]
        citations={c for f in findings for c in f['citations']}
        result.update(findings=len(findings),declared_cited_reviews=len({h['review_id'] for h in evidence if h['citation_id'] in citations}))
    else:
        result.update(candidate_count=row['candidate_count'],candidate_cluster_counts=row['candidate_cluster_counts'],candidate_pool_sha256=row['candidate_pool_sha256'],
                      contract_error=row.get('format_error'))
        # Parse for diagnosis only: invalid responses remain invalid, not repaired.
        try:data=json.loads(row['raw_model_output'])
        except (ValueError,TypeError):result.update(json_parseable=False,declared_findings=None);return result
        result['json_parseable']=True
        findings=data.get('findings',[]) if isinstance(data,dict) else []
        if not isinstance(findings,list):result['declared_findings']=None;return result
        ids={f.get('evidence_id') for f in findings if isinstance(f,dict)}
        literal=sum(isinstance(f,dict) and isinstance(f.get('quote'),str) and bool(f['quote']) and f.get('evidence_id') in by_id and f['quote'] in by_id[f['evidence_id']]['text'] for f in findings)
        result.update(declared_findings=len(findings),literal_quotes=literal,nonliteral_quotes=len(findings)-literal,
            declared_cited_reviews=len({h['review_id'] for h in evidence if h['citation_id'] in ids}),
            labels_are_model_generated_not_ground_truth=True)
    return result


def report(spec_path):
    spec=json.loads(Path(spec_path).read_text());root=Path(spec['results']);baseline=Path(spec['baseline_results'])
    rows=[json.loads(l) for l in (root/'runs.private.jsonl').read_text().splitlines()]
    old=[json.loads(l) for l in (baseline/'runs.private.jsonl').read_text().splitlines()]
    expected={(q,m) for q in ['P01','P02'] for m in ['traditional','thematic']}
    assert len(rows)==len(old)==4
    assert {(r['question_id'],r['method']) for r in rows}=={(r['question_id'],r['method']) for r in old}==expected
    assert json.loads((root/'status.private.json').read_text())['status']=='complete'
    provenance=json.loads((root/'provenance.private.json').read_text());oldprov=json.loads((baseline/'provenance.private.json').read_text())
    assert provenance['baseline_runs_sha256']==hashlib.sha256((baseline/'runs.private.jsonl').read_bytes()).hexdigest()
    assert provenance['index_metadata_sha256']==oldprov['index_metadata_sha256'] and provenance['model_digest']==oldprov['model_digest']
    questions={q['id']:q for q in spec['questions']};outcomes=[]
    for r in old:outcomes.append(summarize(r,'v1'))
    for r in rows:
        assert all(h['product_id']==spec['product_id'] for h in r['evidence'])
        outcomes.append(summarize(r,'v2',questions[r['question_id']],spec['generation']))
    pairs=[]
    for q in questions:
        a,b=[r for r in rows if r['question_id']==q]
        assert a['candidate_pool_sha256']==b['candidate_pool_sha256']
        pairs.append({'question_id':q,'candidate_pool_sha256':a['candidate_pool_sha256'],'candidate_count':a['candidate_count'],
            'candidate_cluster_counts':a['candidate_cluster_counts'],
            'shared_context_passages':len({h['id'] for h in a['evidence']}&{h['id'] for h in b['evidence']})})
    return {'schema':'product_aspect_pilot_comparison_v2','role':'development_only_not_final_metrics','product_id':spec['product_id'],
        'reviews':spec['expected_reviews'],'new_attempts':4,'baseline_attempts':4,'repetitions_per_combination':1,
        'spec_sha256':hashlib.sha256(Path(spec_path).read_bytes()).hexdigest(),
        'baseline_runs_sha256':provenance['baseline_runs_sha256'],'new_runs_sha256':hashlib.sha256((root/'runs.private.jsonl').read_bytes()).hexdigest(),
        'index_metadata_sha256':provenance['index_metadata_sha256'],'model_digest':provenance['model_digest'],
        'outcomes':outcomes,'new_retrieval_pairs':pairs,'changes':spec['changes'],
        'interpretation':'Literal quote check is not entailment. Declared fields of rejected responses are diagnostic only. Limits/schema differ between rounds. No numerical faithfulness/depth score, independent human scoring, winner or isolated causal attribution. Prior artifacts preserved.'}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--spec',default='configs/curly-product-pilot.v2-aspects.json');p.add_argument('--output',required=True);a=p.parse_args()
    dest=Path(a.output)
    if dest.exists():raise FileExistsError('Use a new output path')
    dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(report(a.spec),ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':main()
