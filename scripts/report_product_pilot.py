"""Reproduce aggregate-only pilot diagnostics; private responses never exported."""
import argparse
import json
import hashlib
import collections
from pathlib import Path
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--spec',default='configs/curly-product-pilot.v1.json')
parser.add_argument('--output',required=True)
args=parser.parse_args()
if Path(args.output).exists():raise FileExistsError('Preserve prior report; use a new destination')
spec=json.loads(Path(args.spec).read_text());root=Path(spec['results']);rows=[json.loads(l) for l in (root/'runs.private.jsonl').read_text().splitlines()];diagnostics=json.loads((root/'retrieval-diagnostics.private.json').read_text());metadata=json.loads((Path(spec['index'])/'metadata.json').read_text());provenance=json.loads((root/'provenance.private.json').read_text())
assert len(rows)==4 and {(r['question_id'],r['method']) for r in rows}=={(q,m) for q in ['P01','P02'] for m in ['traditional','thematic']}
aggregates=[]
for r in rows:
 assert all(h['product_id']==spec['product_id'] for h in r['evidence'])
 ids={c for fs in (r['structured'] or {}).get('groups',{}).values() for f in fs for c in f['citations']}
 aggregates.append({'question_id':r['question_id'],'method':r['method'],'included_reviews':len({h['review_id'] for h in r['evidence']}),
 'cited_reviews':len({h['review_id'] for h in r['evidence'] if h['citation_id'] in ids}),
 'clusters_in_context':dict(collections.Counter(h['cluster'] for h in r['evidence'])),
 'findings':sum(len(fs) for fs in (r['structured'] or {}).get('groups',{}).values()),
 'format_valid':r['format_valid'],'generation_error':bool(r['generation_error']),'cut':r['ollama'].get('done_reason')=='length',
 'total_seconds':r['total_seconds'],'retrieval_seconds':r['retrieval_seconds'],'prompt_tokens':r['ollama'].get('prompt_eval_count'),'output_tokens':r['ollama'].get('eval_count')})
report={'schema':'individual_product_pilot_aggregates_v1','role':'development_not_final_evaluation','product_id':spec['product_id'],'reviews':804,'chunks':metadata['chunks'],
'cluster_counts':metadata['cluster_counts'],'clusters_exploratory_not_validated':True,'attempts':4,'repetitions':1,'questions':spec['questions'],
'spec_sha256':hashlib.sha256(Path(args.spec).read_bytes()).hexdigest(),'corpus_sha256':spec['corpus_sha256'],
'index_metadata_sha256':provenance['index_metadata_sha256'],'runs_sha256':hashlib.sha256((root/'runs.private.jsonl').read_bytes()).hexdigest(),
'model_digest':provenance['model_digest'],'runtime':provenance['runtime_version'],'retrieval_diagnostics':diagnostics,'outcomes':aggregates,
'quality_review':'Assistant qualitative source check after method labels were visible. No independent human scoring, exhaustive reference, depth rate or superiority test.',
'resource_policy':'Wall time and Ollama tokens only; first call includes model loading; fixed order; no process/memory monitoring.',
'frozen_experiments_changed':False}
Path(args.output).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
