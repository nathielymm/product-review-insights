"""Source isolation enforces IDs and shared token budget, not semantic truth."""
import importlib.util
import json
from pathlib import Path
import pytest


def load_module(monkeypatch):
    scripts=Path(__file__).resolve().parents[1]/'scripts';monkeypatch.syspath_prepend(str(scripts))
    spec=importlib.util.spec_from_file_location('source_product_pilot',scripts/'run_product_source_pilot.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


def test_budget_is_split_without_expanding_answer_output_cap(monkeypatch):
    m=load_module(monkeypatch)
    assert m.token_budgets(1536,8)==[192]*8
    assert sum(m.token_budgets(1536,7))==1536
    with pytest.raises(ValueError):m.token_budgets(1,2)


def test_source_id_is_assigned_by_system_and_model_cannot_add_it(monkeypatch):
    m=load_module(monkeypatch);s=json.loads((Path(__file__).resolve().parents[1]/'configs/curly-product-pilot.v4-source-isolated.json').read_text())
    data={'relato':'A pessoa relata quebra.','suspeita':'','melhoria':'','validacao':''}
    assert m.validate_source(json.dumps(data),s['questions'][0],s['generation'])==data
    assert m.bind_finding({**data,'fonte':'E999'},{'citation_id':'E2'})['fonte']=='E2'
    with pytest.raises(ValueError,match='Campos'):
        m.validate_source(json.dumps({**data,'fonte':'E999'}),s['questions'][0],s['generation'])


def test_suspicion_is_separate_and_empty_report_cannot_carry_proposal(monkeypatch):
    m=load_module(monkeypatch);s=json.loads((Path(__file__).resolve().parents[1]/'configs/curly-product-pilot.v4-source-isolated.json').read_text())
    data={'relato':'A pessoa relata quebra em dois meses.','suspeita':'A pessoa suspeita da fixação.','melhoria':'Investigar a fixação.','validacao':'Testar resistência.'}
    assert m.validate_source(json.dumps(data),s['questions'][1],s['generation'])==data
    with pytest.raises(ValueError):m.validate_source(json.dumps(data),s['questions'][0],s['generation'])
    data['relato']=''
    with pytest.raises(ValueError,match='sem relato'):m.validate_source(json.dumps(data),s['questions'][1],s['generation'])


def test_prior_source_isolated_runs_are_not_overwritten(tmp_path,monkeypatch):
    m=load_module(monkeypatch);p=tmp_path/'old';p.mkdir();(p/'runs.private.jsonl').write_text('preserve')
    monkeypatch.setattr(m,'api',lambda *a,**kw:pytest.fail('No API before preservation guard'))
    with pytest.raises(FileExistsError):m.run({'results':str(p)},'unused')
    assert (p/'runs.private.jsonl').read_text()=='preserve'


def test_report_checks_each_model_call_had_only_its_bound_source(monkeypatch):
    import copy
    scripts=Path(__file__).resolve().parents[1]/'scripts';monkeypatch.syspath_prepend(str(scripts))
    spec=importlib.util.spec_from_file_location('source_product_report',scripts/'report_product_source_pilot.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    data={'relato':'A pessoa relata algo.','suspeita':'','melhoria':'','validacao':''}
    source={'citation_id':'E1','review_id':'r','product_id':'p','text':'source one'}
    request={'idioma_resposta':'português brasileiro','pergunta':'q','permitir_melhorias':False,'unica_avaliacao':'source one'}
    call={'source_id':'E1','payload':{'messages':[{'content':'system'},{'content':json.dumps(request)}]},'format_valid':True,'structured':data}
    row={'evidence':[source],'source_calls':[call],'structured':{'achados':[{**data,'fonte':'E1'}]},
         'source_material':[{'evidence_id':'E1','review_id':'r','product_id':'p','text':'source one'}]}
    assert m.check_source_binding(row)
    original=copy.deepcopy(row)
    request['unica_avaliacao']='another source';call['payload']['messages'][1]['content']=json.dumps(request)
    assert not m.check_source_binding(row)
    row=original;row['structured']['achados'][0]['fonte']='E9'
    assert not m.check_source_binding(row)
