"""v2 demo boundaries: synthetic sources and model replies, no private artifacts or network."""
import copy
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
from product_review_insights import demo_v2 as ui, generation


@pytest.fixture
def demo(monkeypatch):
    config=json.loads((ui.ROOT/'configs/product-evaluation.v2.approved-not-frozen.json').read_text())
    questions=json.loads((ui.ROOT/config['questions']['path']).read_text())
    d=ui.Demo(config=config,questions=questions)
    queries=[];calls=[];pid=config['products'][0]['product_id']
    docs=[{'id':f'r{i}:0','review_id':f'r{i}','product_id':pid,'text':f'Synthetic source {i}'} for i in range(3)]
    docs.append({**docs[0],'id':'r0:1','text':'Second chunk of same synthetic review'})
    class Model:
        def encode(self,texts,**kwargs):
            queries.append(texts)
            return np.ones((len(texts),2),dtype='float32')
    class Index:
        ntotal=4
        def search(self,vectors,k):
            return np.ones((len(vectors),k)),np.tile(np.arange(k),(len(vectors),1))
    retriever=SimpleNamespace(model=Model(),index=Index(),documents=docs,clusters=np.array([0,1,1,0]))
    monkeypatch.setattr(d,'retriever',lambda selected: retriever)
    monkeypatch.setattr(ui,'verify_runtime',lambda config: calls.append('runtime'))
    structured={'groups':{'G1':[{'citations':['E1'],'observation':'A reviewer reports a problem.','proposal':'Investigate the design.','uncertainty':'Cause unknown.'}]},'limits':'Limited evidence.'}
    def api(path,payload=None,**kwargs):
        calls.append(copy.deepcopy(payload))
        if payload['options']['num_predict']==1:
            return {'prompt_eval_count':128,'eval_count':1}
        system=payload['messages'][0]['content']
        if system==ui.PLANNER_SYSTEM:
            raw=json.dumps({'question_en':'What design issues are reported?', 'aspects':[f'English design aspect {i}' for i in range(5)]})
        elif system==generation.STRUCTURED_SYSTEM:
            raw=json.dumps(structured)
        else:
            texts=json.loads(payload['messages'][1]['content'])['textos']
            raw=json.dumps({k:'Tradução '+str(i) for i,k in enumerate(texts)})
        return {'message':{'content':raw},'prompt_eval_count':128,'eval_count':30,'done_reason':'stop'}
    monkeypatch.setattr(generation,'api',api)
    request={'product_id':pid,'method':'traditional','question_id':'Q1','question':questions['products'][0]['questions'][0]['question_pt']}
    return d,request,queries,calls,structured,retriever


def test_catalog_contains_only_three_v2_products(demo):
    d,*_=demo
    assert len(d.options()['products'])==3
    assert {p['id'] for p in d.options()['products']}=={'B00R1TAN7I','B012Q9NGE4','B01557EHW4'}
    assert all(len(p['questions'])==6 for p in d.options()['products'])
    assert 'cohorts' not in d.options()


@pytest.mark.parametrize('method',['traditional','thematic'])
def test_predefined_uses_exact_aspects_english_generation_then_translation(demo,method):
    d,request,queries,calls,structured,_=demo;request['method']=method;before=copy.deepcopy(structured)
    result=d.answer(request)
    saved=d.qmap[request['product_id']][0]
    assert queries==[[a['retrieval_query'] for a in saved['aspects']]]
    actual=[p for p in calls if isinstance(p,dict) and p['options']['num_predict']!=1]
    assert len(actual)==2 and actual[0]['messages'][0]['content']==generation.STRUCTURED_SYSTEM
    assert json.loads(actual[0]['messages'][1]['content'])['question']==saved['generation_question_en']
    assert 'Traduza os textos' in actual[1]['messages'][0]['content']
    assert structured==before
    assert result['query_mode']=='predefined' and result['presentation_language']=='pt-BR'
    assert 'A reviewer reports a problem.' in result['english_answer']
    assert result['products'][0]['findings'][0]['citations']==['E1']
    assert result['evidence'][0]['text'].startswith('Synthetic source')
    assert result['cited_scope']=={'reviews':1,'products':1}
    assert len(result['evidence'])==3 # Same-review chunks deduplicated before generation.
    assert not d.lock.locked()


def test_free_question_plans_five_aspects_without_using_benchmark_question(demo):
    d,r,queries,calls,*_=demo;r.update(question_id='',question='Como melhorar o desenho?')
    result=d.answer(r)
    assert result['query_mode']=='free'
    assert queries==[[f'English design aspect {i}' for i in range(5)]]
    actual=[p for p in calls if isinstance(p,dict) and p['options']['num_predict']!=1]
    assert len(actual)==3 and actual[0]['messages'][0]['content']==ui.PLANNER_SYSTEM
    assert json.loads(actual[1]['messages'][1]['content'])['question']=='What design issues are reported?'


@pytest.mark.parametrize('patch',[{'product_id':'foreign'},{'question':' '},{'question_id':'Q9'},{'question':'Edited preset'},{'method':'invalid'}])
def test_rejects_bad_input_before_model_calls(demo,patch):
    d,r,_,calls,*_=demo;r.update(patch)
    with pytest.raises(ValueError):d.answer(r)
    assert not calls and not d.lock.locked()


def test_rejects_foreign_product_context(demo):
    d,r,_,calls,_,retriever=demo;retriever.documents[0]['product_id']='foreign'
    with pytest.raises(ValueError):d.answer(r)
    assert calls==['runtime'] and not d.lock.locked()


def test_translation_failure_keeps_original_and_releases_lock(demo,monkeypatch):
    d,r,*_=demo;base=generation.api
    def broken(path,payload=None,**kw):
        if payload and 'Traduza os textos' in payload['messages'][0]['content'] and payload['options']['num_predict']!=1:
            raise RuntimeError('Translation unavailable')
        return base(path,payload,**kw)
    monkeypatch.setattr(generation,'api',broken)
    result=d.answer(r)
    assert result['translation_failed'] and result['presentation_language']=='en'
    assert result['answer']==result['english_answer']
    assert result['products'][0]['findings'][0]['observation']=='A reviewer reports a problem.'
    assert generation.api is broken and not d.lock.locked()


def test_invalid_english_is_visible_without_translation(demo,monkeypatch):
    d,r,_,calls,*_=demo;base=generation.api
    def malformed(path,payload=None,**kw):
        out=base(path,payload,**kw)
        if payload['options']['num_predict']!=1:out['message']['content']='Malformed original'
        return out
    monkeypatch.setattr(generation,'api',malformed)
    result=d.answer(r)
    assert not result['format_valid'] and result['answer']=='Malformed original'
    assert not result['products'] and result['cited_scope'] is None
    assert len([p for p in calls if isinstance(p,dict) and p['options']['num_predict']!=1])==1


def test_busy_request_does_not_release_another_requests_lock(demo):
    d,r,*_=demo;assert d.lock.acquire(False)
    try:
        with pytest.raises(ValueError,match='andamento'):d.answer(r)
        assert d.lock.locked()
    finally:d.lock.release()


def test_model_failure_restores_transport_and_lock(demo,monkeypatch):
    d,r,*_=demo
    def broken(*a,**k):raise RuntimeError('offline')
    monkeypatch.setattr(generation,'api',broken)
    with pytest.raises(RuntimeError):d.answer(r)
    assert generation.api is broken and not d.lock.locked()


def test_model_budget_is_checked_before_full_generation(demo,monkeypatch):
    d,r,*_=demo
    def too_big(*a,**kw):return {'prompt_eval_count':10000,'eval_count':1}
    monkeypatch.setattr(generation,'api',too_big)
    with pytest.raises(ValueError,match='exceeds context'):d.answer(r)
    assert not d.lock.locked()


def test_scope_counts_reviews_not_chunks():
    structured={'groups':{'G1':[{'citations':['E1','E2']}]}}
    evidence=[{'citation_id':f'E{i}','review_id':'same','product_id':'one'} for i in [1,2]]
    assert ui.cited_scope(structured,evidence)=={'reviews':1,'products':1}
    assert ui.cited_scope(None,evidence) is None


def test_free_planner_rejects_duplicate_aspects(demo,monkeypatch):
    d,r,*_=demo;r.update(question_id='',question='Outra pergunta')
    base=generation.api
    def duplicated(path,payload=None,**kw):
        out=base(path,payload,**kw)
        if payload['options']['num_predict']!=1 and payload['messages'][0]['content']==ui.PLANNER_SYSTEM:
            out['message']['content']=json.dumps({'question_en':'Question?', 'aspects':['same']*5})
        return out
    monkeypatch.setattr(generation,'api',duplicated)
    with pytest.raises(ValueError,match='repetidas'):d.answer(r)
    assert not d.lock.locked()


def test_configuration_tamper_is_rejected_before_artifact_loading(tmp_path):
    folder=tmp_path/'configs';folder.mkdir();(folder/'settings.json').write_text('{}')
    (folder/'evaluation-freeze.v2.json').write_text(json.dumps({'status':'frozen_user_authorized','configuration':'configs/settings.json','configuration_sha256':'incorrect'}))
    with pytest.raises(ValueError,match='diferente'):ui.load_demo_configuration(tmp_path)


def test_legacy_prompt_export_keeps_archived_pilots_reproducible():
    import hashlib
    ui.helpers() # Adds the scripts path, without model calls.
    import serve_demo
    assert hashlib.sha256(serve_demo.DEMO_SYSTEM.encode()).hexdigest()=='b5304c6ce2a7d9660ae0a383eaf8803ab833938c8a41d2da14c7c49a70963f5a'


def test_runtime_identity_failure_releases_lock(demo,monkeypatch):
    d,r,*_=demo
    def mismatch(*args):raise ValueError('Active runtime/model differs')
    monkeypatch.setattr(ui,'verify_runtime',mismatch)
    with pytest.raises(ValueError,match='differs'):d.answer(r)
    assert not d.lock.locked()


@pytest.mark.parametrize('error,status',[(ui.DemoInputError('Escolha um produto.'),400),(ValueError('runtime mismatch'),503),(RuntimeError('offline'),503)])
def test_http_separates_user_errors_from_backend_failures(error,status):
    import io
    ui.helpers()
    from serve_demo import make_handler
    def answer(request):raise error
    handler=make_handler(SimpleNamespace(answer=answer))
    replies=[];body=b'{"question":"test"}'
    request=SimpleNamespace(path='/api/ask',headers={'Host':'127.0.0.1:8501','Content-Length':str(len(body))},
        server=SimpleNamespace(server_port=8501),rfile=io.BytesIO(body),reply=lambda code,data:replies.append((code,data)))
    handler.do_POST(request)
    assert replies[0][0]==status
    if status==503:assert 'runtime mismatch' not in replies[0][1]['error']


def test_http_rejects_foreign_origin_without_model_calls():
    ui.helpers()
    from serve_demo import make_handler
    replies=[]
    request=SimpleNamespace(path='/api/ask',headers={'Host':'127.0.0.1:8501','Origin':'https://foreign.example'},
        server=SimpleNamespace(server_port=8501),reply=lambda code,data:replies.append(code))
    make_handler(SimpleNamespace()).do_POST(request)
    assert replies==[403]
