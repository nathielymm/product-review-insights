"""Source selection and presentation translation reused by the current v2 pipeline."""
import copy
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
import pytest


def load_module(monkeypatch):
    scripts=Path(__file__).resolve().parents[1]/'scripts';monkeypatch.syspath_prepend(str(scripts))
    spec=importlib.util.spec_from_file_location('original_product_pilot',scripts/'run_product_original_pilot.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def fixture():
    return {'groups':{'G1':[{'citations':['E1'],'observation':'The old diffuser broke; this one fits.','proposal':'','uncertainty':'Unknown cause.'}]},'limits':'One report.'}

def test_translation_is_text_only_and_preserves_english_and_citations(monkeypatch):
    m=load_module(monkeypatch);english=fixture();original=copy.deepcopy(english);texts,paths=m.translation_fields(english)
    assert list(texts)==['T001','T002','T003'] and 'E1' not in json.dumps(texts)
    result=m.apply_translations(english,texts,paths,json.dumps({'T001':'O difusor antigo quebrou; este encaixa.','T002':'Causa desconhecida.','T003':'Um relato.'}))
    assert english==original and result['groups']['G1'][0]['citations']==['E1']
    assert result['groups']['G1'][0]['proposal']==''
    assert 'antigo' in result['groups']['G1'][0]['observation']

def test_translation_rejects_missing_fields_and_invented_citation(monkeypatch):
    m=load_module(monkeypatch);english=fixture();texts,paths=m.translation_fields(english)
    with pytest.raises(ValueError):m.apply_translations(english,texts,paths,'{}')
    translated={key:'texto' for key in texts};translated['T001']='Texto [E999]'
    with pytest.raises(ValueError):m.apply_translations(english,texts,paths,json.dumps(translated))

def test_translation_payload_never_contains_original_source_panel(monkeypatch):
    m=load_module(monkeypatch);english=fixture()
    source={'citation_id':'E1','group_alias':'G1','product_id':'p','review_id':'r','text':'ORIGINAL SOURCE NOT TO TRANSLATE'}
    def api(path,payload,**kw):
        assert 'ORIGINAL SOURCE NOT TO TRANSLATE' not in json.dumps(payload)
        return {'message':{'content':json.dumps({'T001':'O difusor antigo quebrou; este encaixa.','T002':'Causa desconhecida.','T003':'Um relato.'})},'done_reason':'stop'}
    monkeypatch.setattr(m.generation,'api',api)
    result=m.translate_presentation(english,[source],{'model':'gemma3:4b','temperature':0,'seed':42,'num_ctx':8192,'num_predict':1536})
    assert result['valid'] and '[E1]' in result['answer_pt']
    assert m.sources_for(english,[source])[0]['text']==source['text']

def test_original_generator_is_used_without_replacing_its_prompt(monkeypatch):
    m=load_module(monkeypatch)
    from product_review_insights.generation import generate, STRUCTURED_SYSTEM
    assert m.generation.generate is generate
    assert 'Use concise English sentences.' in STRUCTURED_SYSTEM

def load_aspect_module(monkeypatch):
    scripts=Path(__file__).resolve().parents[1]/'scripts';monkeypatch.syspath_prepend(str(scripts))
    spec=importlib.util.spec_from_file_location('aspect_pilot',scripts/'run_product_aspect_pilot.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def test_aspect_union_retains_specialist_results_and_deduplicates_reviews(monkeypatch):
    import numpy as np
    m=load_aspect_module(monkeypatch)
    class Index:
        ntotal=4
        def search(self,vectors,k):
            assert len(vectors)==2 and k==2
            return np.zeros((2,2)),np.array([[0,1],[2,3]])
    r=SimpleNamespace(index=Index(),model=SimpleNamespace(encode=lambda *a,**kw:np.zeros((2,2))),
       documents=[{'product_id':'p','review_id':v} for v in ['repeat','repeat','special-a','special-b']])
    question={'aspects':[{'id':'a','retrieval_query':'q1'},{'id':'b','retrieval_query':'q2'}]}
    settings={'per_aspect_candidates':2,'rrf_constant':60,'max_total_candidates':80}
    ranked,_,matches,queries=m.candidates_for(r,question,settings)
    assert ranked==[0,2,3] and matches[2]==['b'] and len(queries)==2
    assert m.candidates_for(r,question,settings)[0]==ranked
