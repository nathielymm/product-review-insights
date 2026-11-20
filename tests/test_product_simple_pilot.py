"""Compact source references must display system-owned text, never model quotations."""
import importlib.util
import json
from pathlib import Path
import pytest


def load_module(monkeypatch):
    scripts=Path(__file__).resolve().parents[1]/'scripts';monkeypatch.syspath_prepend(str(scripts))
    spec=importlib.util.spec_from_file_location('simple_product_pilot',scripts/'run_product_simple_pilot.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


def fixture(m):
    spec=json.loads((Path(__file__).resolve().parents[1]/'configs/curly-product-pilot.v3-simple.json').read_text())
    sources=[{'citation_id':'E1','product_id':'product','review_id':'review','text':'Original English text, unchanged.'}]
    data={'achados':[{'fonte':'E1','relato':'A pessoa descreve uma dificuldade.','melhoria':'','validacao':''}], 'limites':'Relato individual.'}
    return spec,sources,data


def test_original_sources_are_attached_without_model_copy_and_deduplicated(monkeypatch):
    m=load_module(monkeypatch);spec,sources,data=fixture(m)
    accepted=m.validate_simple(json.dumps(data),sources,spec['questions'][0],spec['generation'])
    accepted['achados'].append(dict(accepted['achados'][0]))
    result=m.materialize_sources(accepted,sources)
    assert result==[{'evidence_id':'E1','product_id':'product','review_id':'review','text':'Original English text, unchanged.'}]
    assert 'fonte' in m.simple_schema(sources,spec['questions'][0],spec['generation'])['properties']['achados']['items']['properties']
    assert 'quote' not in m.simple_schema(sources,spec['questions'][0],spec['generation'])['properties']['achados']['items']['properties']


def test_unknown_source_and_model_supplied_excerpt_are_rejected(monkeypatch):
    m=load_module(monkeypatch);spec,sources,data=fixture(m)
    data['achados'][0]['fonte']='E9'
    with pytest.raises(ValueError):m.validate_simple(json.dumps(data),sources,spec['questions'][0],spec['generation'])
    data['achados'][0]['fonte']='E1';data['achados'][0]['trecho']='invented source'
    with pytest.raises(ValueError,match='Campos'):m.validate_simple(json.dumps(data),sources,spec['questions'][0],spec['generation'])


def test_improvement_contract_is_question_specific(monkeypatch):
    m=load_module(monkeypatch);spec,sources,data=fixture(m)
    data['achados'][0]['melhoria']='Investigar uma alteração.'
    with pytest.raises(ValueError):m.validate_simple(json.dumps(data),sources,spec['questions'][0],spec['generation'])
    assert m.validate_simple(json.dumps(data),sources,spec['questions'][1],spec['generation'])==data


def test_round_three_never_overwrites_prior_results(tmp_path,monkeypatch):
    m=load_module(monkeypatch);p=tmp_path/'old';p.mkdir();(p/'runs.private.jsonl').write_text('preserve')
    monkeypatch.setattr(m,'api',lambda *a,**kw:pytest.fail('No API before preservation guard'))
    with pytest.raises(FileExistsError):m.run({'results':str(p)},'unused')
    assert (p/'runs.private.jsonl').read_text()=='preserve'


def test_report_detects_tampered_source_text_without_claiming_entailment(monkeypatch):
    scripts=Path(__file__).resolve().parents[1]/'scripts';monkeypatch.syspath_prepend(str(scripts))
    spec=importlib.util.spec_from_file_location('simple_product_report',scripts/'report_product_simple_pilot.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    row={'format_valid':True,'evidence':[{'citation_id':'E1','product_id':'p','review_id':'r','text':'original'}],
         'structured':{'achados':[{'fonte':'E1','relato':'This interpretation might be wrong.'}]},
         'source_material':[{'evidence_id':'E1','product_id':'p','review_id':'r','text':'original'}]}
    assert m.source_identity_check(row) is True
    row['source_material'][0]['text']='rewritten'
    assert m.source_identity_check(row) is False
    row['format_valid']=False
    assert m.source_identity_check(row) is None
