"""Small local development probe; never calls evaluation questions or corpora."""
import argparse
import json
import platform
import random
import time
from pathlib import Path
from product_review_insights.data import digest_file
from product_review_insights.generation import api,generate,SYSTEM,STRUCTURED_SYSTEM
from product_review_insights.study import validate_index_scope


def mechanical_check(result,query_id,num_ctx,expected_hits):
    info=result['ollama']; citations=result['citations']
    factual_task=query_id in {'DS01','DS05'}
    token_counts=[info.get('prompt_eval_count'),info.get('eval_count')]
    tokens_known=all(isinstance(n,int) for n in token_counts)
    return {'nonempty_answer':bool(result['answer'].strip()),
            'not_output_truncated':info.get('done_reason')=='stop',
            'no_invalid_citation_ids':not citations['invalid_citations'],
            'factual_task_has_citation':bool(citations['has_valid_citations']) if factual_task else None,
            'all_hits_in_context':len(result['evidence'])==expected_hits,
            'token_counts_within_window':sum(token_counts)<=num_ctx if tokens_known else False,
            'structured_contract_valid':result.get('structured_validation',{}).get('valid') if result.get('structured_validation',{}).get('requested') else None,
            'semantic_faithfulness_judged':False}


def probe(index_path,output,plan_path):
    index_path,output=Path(index_path),Path(output)
    if output.exists(): raise FileExistsError('Use a new development probe destination')
    plan=json.loads(Path(plan_path).read_text()); meta=json.loads((index_path/'metadata.json').read_text())
    validate_index_scope(meta,plan['allowed_cohort'],requires_scope=True)
    if meta['study']['split']!=plan['allowed_split']: raise ValueError('Only development split is eligible')
    if meta['development_selection_plan_sha256']!=digest_file(plan_path): raise ValueError('Selection plan changed')
    config=meta['config']; tags=api('/api/tags',timeout=10)
    model=next(m for m in tags['models'] if m['name']==config['ollama_model'])
    version=api('/api/version',timeout=10)
    from product_review_insights.retrieval import Retriever
    retriever=Retriever(index_path)
    output.mkdir(parents=True)
    metadata={'status':'running','phase':'development_only','config':config,'corpus_sha256':meta['corpus_sha256'],
              'index_metadata_sha256':digest_file(index_path/'metadata.json'),'plan_sha256':digest_file(plan_path),
              'probe_code_sha256':digest_file(__file__),'generation_code_sha256':digest_file('src/product_review_insights/generation.py'),
              'system_prompt':STRUCTURED_SYSTEM if config.get('structured_output') else SYSTEM,
              'source_snapshots':{'probe':Path(__file__).read_text(),'generation':Path('src/product_review_insights/generation.py').read_text()},'ollama_version':version,'model_digest':model['digest'],'platform':platform.platform(),
              'generation_metrics_are_not_final_experiment_results':True}
    (output/'metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')
    warm=generate('Reply with ready.',[{'id':'warmup','text':'System ready.'}],config)
    print(json.dumps({'event':'warmup_complete','done_reason':warm['ollama'].get('done_reason')}),flush=True)
    questions=[q for q in plan['queries'] if q['id'] in plan['generation_probe_query_ids']]
    rng=random.Random(plan['selection_seed']); rng.shuffle(questions)
    records=[]
    with (output/'runs.private.jsonl').open('w') as stream:
        for q in questions:
            methods=['traditional','thematic']; rng.shuffle(methods)
            for method in methods:
                start=time.perf_counter(); hits=retriever.search(q['question'],thematic=method=='thematic')
                result=generate(q['question'],hits,config)
                check=mechanical_check(result,q['id'],config['num_ctx'],config['top_k'])
                record={'query_id':q['id'],'question':q['question'],'method':method,'seconds':time.perf_counter()-start,
                        **result,'checks':check}
                stream.write(json.dumps(record,ensure_ascii=False)+'\n'); stream.flush(); records.append(record)
                print(json.dumps({'event':'response_complete','query_id':q['id'],'method':method,'seconds':round(record['seconds'],2),
                                  'done_reason':result['ollama'].get('done_reason'),'output_tokens':result['ollama'].get('eval_count'),'checks':check}),flush=True)
    after=next(m for m in api('/api/tags',timeout=10)['models'] if m['name']==config['ollama_model'])
    if after['digest']!=model['digest']: raise ValueError('Model changed during development probe')
    issues=[{'query_id':r['query_id'],'method':r['method'],'failed_checks':[k for k,v in r['checks'].items() if k!='semantic_faithfulness_judged' and v is False]} for r in records]
    passed=all(not r['failed_checks'] for r in issues)
    summary={'status':'mechanical_probe_passed_semantic_review_pending' if passed else 'development_revision_needed',
             'development_reviews':meta['corpus_manifest']['reviews'],'queries':len(questions),'responses':len(records),
             'config':config,'model_digest':model['digest'],'ollama_version':version,
             'mechanical_checks':issues,'rows':[{'query_id':r['query_id'],'method':r['method'],'seconds':r['seconds'],
                                               'prompt_tokens':r['ollama'].get('prompt_eval_count'),'output_tokens':r['ollama'].get('eval_count'),
                                               'done_reason':r['ollama'].get('done_reason')} for r in records],
             'evaluation_corpora_used':False,'final_rag_quality_metrics_computed':False,
             'semantic_review_complete':False,'input_fingerprints':{k:v for k,v in metadata.items() if k.endswith('sha256')}}
    metadata['status']=summary['status']; (output/'metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')
    (output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    Path('docs/development-generation-probe-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({'event':'probe_complete','status':summary['status'],'responses':len(records)}),flush=True)
    return summary

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--index',default='artifacts/development-selection/v1'); p.add_argument('--output',default='results/development-generation/v1'); p.add_argument('--plan',default='configs/development-selection-plan.json'); a=p.parse_args(); probe(a.index,a.output,a.plan)
