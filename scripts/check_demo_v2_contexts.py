"""Compare all predefined demo contexts with the recorded primary run; no LLM calls."""
import argparse
import json
from pathlib import Path

from product_review_insights.data import digest_file
from product_review_insights.demo_v2 import Demo
from product_review_insights.evaluation_v2 import prepare_attempt


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runs',default='results/product-evaluation-v2/final-run')
    args=parser.parse_args();root=Path(args.runs)
    status=json.loads((root/'status.private.json').read_text())
    if status['status']!='complete' or digest_file(root/'runs.private.jsonl')!=status['runs_sha256']:
        raise ValueError('Run incomplete or changed')
    rows=[json.loads(l) for l in (root/'runs.private.jsonl').read_text().splitlines()]
    primary=[r for r in rows if r['phase']=='primary'];demo=Demo()
    expected={(pid,f'Q{i}',method) for pid in demo.products for i in range(1,7) for method in ['traditional','thematic']}
    if len(primary)!=36 or {(r['product_id'],r['question_id'],r['method']) for r in primary}!=expected:
        raise ValueError('Incomplete primary grid')
    keys=['id','review_id','product_id','citation_id','group_alias','functional_class','text']
    count=0
    for pid in demo.products:
        retriever=demo.retriever(pid)
        for row in [r for r in primary if r['product_id']==pid]:
            q,_,evidence,meta=prepare_attempt(demo.config,demo.questions,row,retriever)
            if [[e.get(k) for k in keys] for e in evidence]!=[[e.get(k) for k in keys] for e in row['evidence']]:
                raise ValueError('Context differs: '+row['attempt_id'])
            if q['generation_question_en']!=row['question_en'] or meta['candidate_pool_sha256']!=row['candidate_pool_sha256']:
                raise ValueError('Question or candidate pool differs: '+row['attempt_id'])
            count+=1
    print(json.dumps({'predefined_contexts_matching_frozen':count,'generator_calls':0}))

if __name__=='__main__':main()
