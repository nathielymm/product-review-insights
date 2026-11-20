"""Round-five attribution labels guide generation but cannot certify semantics."""
import importlib.util
import json
from pathlib import Path
import pytest


def load_module(monkeypatch):
    scripts=Path(__file__).resolve().parents[1]/'scripts';monkeypatch.syspath_prepend(str(scripts))
    spec=importlib.util.spec_from_file_location('attribution_pilot',scripts/'run_product_attribution_pilot.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


def test_longer_complete_report_passes_without_slicing_or_rebinding(monkeypatch):
    m=load_module(monkeypatch);spec=json.loads((Path(__file__).resolve().parents[1]/'configs/curly-product-pilot.v5-attribution.json').read_text())
    text='A pessoa relata que o difusor atual encaixa no secador e substitui o acessório anterior, que havia quebrado; essa falha pertence ao produto antigo, sem demonstrar defeito no atual.'
    assert len(text)>160
    data={'referente':'comparacao_com_anterior','relato':text,'suspeita':'','melhoria':'','validacao':''}
    accepted=m.validate_source(json.dumps(data),spec['questions'][0],spec['generation'])
    assert accepted['relato']==text
    assert m.bind_finding(accepted,{'citation_id':'E8'})['fonte']=='E8'
    data['relato']='x'*(spec['generation']['max_report_chars']+1)
    with pytest.raises(ValueError):m.validate_source(json.dumps(data),spec['questions'][0],spec['generation'])


def test_unidentified_product_does_not_allow_corrective_proposal(monkeypatch):
    m=load_module(monkeypatch);s=json.loads((Path(__file__).resolve().parents[1]/'configs/curly-product-pilot.v5-attribution.json').read_text())
    data={'referente':'nao_identificado','relato':'O referente é incerto.','suspeita':'','melhoria':'Mudar peças.','validacao':''}
    with pytest.raises(ValueError,match='sem produto identificado'):m.validate_source(json.dumps(data),s['questions'][1],s['generation'])
    data['melhoria']=''
    assert m.validate_source(json.dumps(data),s['questions'][1],s['generation'])==data
    assert m.token_budgets(s['config']['num_predict'],8)==[192]*8
