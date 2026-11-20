"""Isolated development pilot: local topics and paired RAGs within one product."""
import argparse
import json
from pathlib import Path
import time
from product_review_insights.data import digest_file, read_corpus
from product_review_insights.retrieval import build, Retriever
from product_review_insights.generation import api, pack_context, response_schema, validate_and_render_structured, citation_check
from serve_demo import DEMO_SYSTEM

SYSTEM = DEMO_SYSTEM + '\nEach finding must express one specific aspect. Preserve which experience and usage condition each citation supports. Do not infer a cause for contrasting results. Do not repeat the same observation. Proposals are hypotheses, not established solutions.'


def load_spec(path):
    spec=json.loads(Path(path).read_text());rows=read_corpus(spec['corpus'])
    if digest_file(spec['corpus'])!=spec['corpus_sha256']:raise ValueError('Corpus hash differs')
    if len(rows)!=spec['expected_reviews'] or any(r['product_id']!=spec['product_id'] for r in rows):raise ValueError('Foreign product or count mismatch')
    return spec


def run(spec, spec_path):
    folder=Path(spec['results'])
    if folder.exists():raise FileExistsError('Preserve previous runs; use a new result destination')
    retriever=Retriever(spec['index']);config=spec['config']
    if retriever.metadata['corpus_sha256']!=spec['corpus_sha256'] or retriever.config!=config:raise ValueError('Index differs from pilot specification')
    version=api('/api/version',timeout=10)
    model=next(x for x in api('/api/tags',timeout=10)['models'] if x['name']==config['ollama_model'])
    folder.mkdir(parents=True)
    provenance={'spec_sha256':digest_file(spec_path),'pilot_script_sha256':digest_file(__file__),
        'index_metadata_sha256':digest_file(Path(spec['index'])/'metadata.json'),
        'runtime_version':version,'model_digest':model['digest'],'system_prompt':SYSTEM,
        'role':spec['role'],'order':'P01 traditional/thematic then P02 traditional/thematic; no warmup or retries',
        'resources':'wall times and Ollama tokens only; no process/memory monitoring'}
    (folder/'provenance.private.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n')
    rows=[]
    for question in spec['questions']:
        for method in ['traditional','thematic']:
            started=time.perf_counter();hits=retriever.search(question['retrieval_query'],thematic=method=='thematic')
            context,included=pack_context(hits,config['context_chars']);retrieval_seconds=time.perf_counter()-started
            assert included and all(h['product_id']==spec['product_id'] for h in included)
            payload={'model':config['ollama_model'],'stream':False,'keep_alive':'10m',
                'messages':[{'role':'system','content':SYSTEM},{'role':'user','content':json.dumps({'question':question['question'],'evidence_jsonl':context,'response_language':'pt-BR'},ensure_ascii=False)}],
                'format':response_schema(included),'options':{k:config[k] for k in ['temperature','seed','num_ctx','num_predict']}}
            row={'question_id':question['id'],'question':question['question'],'retrieval_query':question['retrieval_query'],'method':method,
                'retrieved':hits,'evidence':included,'retrieval_seconds':retrieval_seconds,'payload':payload,
                'generation_error':None,'raw_model_output':None,'structured':None,'format_valid':False}
            try:
                response=api('/api/chat',payload,timeout=180);raw=response['message']['content'];row['raw_model_output']=raw
                row['ollama']={k:response.get(k) for k in ['model','prompt_eval_count','eval_count','total_duration','load_duration','done_reason']}
                try:
                    answer,structured=validate_and_render_structured(raw,included)
                    row.update(answer=answer,structured=structured,format_valid=True)
                except (ValueError,KeyError,TypeError) as e:row.update(answer=raw,format_error=str(e))
                row['citations']=citation_check(row['answer'],{h['citation_id'] for h in included})
            except Exception as e:row.update(generation_error=type(e).__name__+': '+str(e),answer='',ollama={})
            row['total_seconds']=time.perf_counter()-started
            with (folder/'runs.private.jsonl').open('a') as f:f.write(json.dumps(row,ensure_ascii=False)+'\n')
            rows.append(row)
            print(json.dumps({'question':question['id'],'method':method,'included':len(included),'format_valid':row['format_valid'],'error':row['generation_error'],'cut':row['ollama'].get('done_reason')=='length'}),flush=True)
    (folder/'status.private.json').write_text(json.dumps({'status':'complete','attempts':len(rows),'comparative_semantic_review':'pending'},indent=2)+'\n')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--spec',default='configs/curly-product-pilot.v1.json');p.add_argument('--prepare',action='store_true');p.add_argument('--run',action='store_true');a=p.parse_args()
    if a.prepare==a.run:p.error('Choose exactly one of --prepare or --run')
    spec=load_spec(a.spec)
    if a.prepare:
        if Path(spec['index']).exists():raise FileExistsError('Use new index destination')
        metadata=build(spec['corpus'],spec['index'],spec['config'])
        print(json.dumps({'reviews':spec['expected_reviews'],'chunks':metadata['chunks'],'cluster_counts':metadata['cluster_counts']}))
    else:run(spec,a.spec)

if __name__=='__main__':main()
