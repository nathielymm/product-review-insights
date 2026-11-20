"""Original English generation stays unchanged; only display text is translated."""
import copy
import importlib.util
import json
from pathlib import Path
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


def test_original_round_preserves_existing_results_before_model_calls(tmp_path,monkeypatch):
    m=load_module(monkeypatch);p=tmp_path/'old';p.mkdir();(p/'runs.private.jsonl').write_text('preserve')
    monkeypatch.setattr(m.generation,'api',lambda *a,**kw:pytest.fail('No API before overwrite guard'))
    with pytest.raises(FileExistsError):m.run({'results':str(p)},'unused')
    assert (p/'runs.private.jsonl').read_text()=='preserve'


def test_translation_structure_check_is_not_a_semantic_certificate(monkeypatch):
    scripts=Path(__file__).resolve().parents[1]/'scripts';monkeypatch.syspath_prepend(str(scripts))
    spec=importlib.util.spec_from_file_location('original_product_report',scripts/'report_product_original_pilot.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    original=fixture();translated=copy.deepcopy(original)
    translated['groups']['G1'][0]['observation']='Tradução de sentido incorreto, mas mesma estrutura.'
    assert m.check_translation_structure(original,translated) is True
    translated['groups']['G1'][0]['citations']=['E9']
    assert m.check_translation_structure(original,translated) is False
