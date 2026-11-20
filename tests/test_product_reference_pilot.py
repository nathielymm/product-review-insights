"""Source mapping audits are non-destructive labels, never proof of entailment."""
import importlib.util
import json
from pathlib import Path
import pytest


def load_module(monkeypatch):
    scripts=Path(__file__).resolve().parents[1]/'scripts';monkeypatch.syspath_prepend(str(scripts))
    spec=importlib.util.spec_from_file_location('reference_pilot',scripts/'run_product_reference_pilot.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


def test_units_and_claims_are_exact_spans_not_model_quotes(monkeypatch):
    m=load_module(monkeypatch);source={'citation_id':'E1','review_id':'r','product_id':'p','text':'It fit. It broke after 2.5 months.'}
    units=m.source_units([source]);assert len(units)==2
    assert all(u['text']==source['text'][u['start']:u['end']] for u in units)
    data={'groups':{'G1':[{'citations':['E1'],'observation':'It fit. It broke.','proposal':'None','uncertainty':''}]},'limits':'One review.'}
    blocks=m.statement_blocks(data);assert len(blocks)==2 and len(blocks[0]['statements'])==2
    assert blocks[0]['statements'][0]['text']=='It fit.'
    assert all(s['role']!='proposal' for b in blocks for s in b['statements'])


def test_audit_cannot_invent_source_unit_or_omit_claim(monkeypatch):
    m=load_module(monkeypatch);block={'statements':[{'id':'S001','role':'observation','text':'Claim.'}]};units=[{'id':'U001'}]
    data={'S001':{'status':'supported','source_units':['U001'],'reason':'none'}}
    assert m.validate_audit(json.dumps(data),block,units)==data
    data['S001']['source_units']=['U999']
    with pytest.raises(ValueError):m.validate_audit(json.dumps(data),block,units)
    with pytest.raises(ValueError):m.validate_audit('{}',block,units)


def test_uncertain_alignment_cannot_be_accepted_without_support(monkeypatch):
    m=load_module(monkeypatch);block={'statements':[{'id':'S001','role':'observation','text':'Claim.'}]};units=[{'id':'U001'}]
    data={'S001':{'status':'supported','source_units':[],'reason':'none'}}
    with pytest.raises(ValueError):m.validate_audit(json.dumps(data),block,units)
    data['S001']={'status':'needs_review','source_units':['U001'],'reason':'different_person_or_review'}
    assert m.validate_audit(json.dumps(data),block,units)==data
    data['S001']={'status':'grounded_hypothesis','source_units':['U001'],'reason':'none'}
    with pytest.raises(ValueError):m.validate_audit(json.dumps(data),block,units)


def test_reference_round_never_overwrites_previous_results(tmp_path,monkeypatch):
    m=load_module(monkeypatch);root=tmp_path/'old';root.mkdir();(root/'runs.private.jsonl').write_text('preserve')
    monkeypatch.setattr(m.original,'run',lambda *a,**kw:pytest.fail('No generation before overwrite guard'))
    with pytest.raises(FileExistsError):m.run({'results':str(root)},'unused')
    assert (root/'runs.private.jsonl').read_text()=='preserve'


def test_supported_label_with_error_reason_is_rejected(monkeypatch):
    m=load_module(monkeypatch)
    block={'statements':[{'id':'S001','role':'observation','text':'Claim.'}]}
    data={'S001':{'status':'supported','source_units':['U001'],'reason':'unsupported_generalization'}}
    with pytest.raises(ValueError):
        m.validate_audit(json.dumps(data),block,[{'id':'U001'}])


def test_similarity_candidates_preserve_claims_and_do_not_certify_support(monkeypatch):
    import numpy as np
    scripts=Path(__file__).resolve().parents[1]/'scripts';monkeypatch.syspath_prepend(str(scripts))
    from rank_product_reference_spans import rank_candidates
    statements=[{'id':'S001','text':'It is glued.','role':'observation','original_citations':['E1']}]
    units=[{'id':'U1','evidence_id':'E2','review_id':'r2','text':'It seems glued.'},
           {'id':'U2','evidence_id':'E2','review_id':'r2','text':'More from same review.'},
           {'id':'U3','evidence_id':'E1','review_id':'r1','text':'It is not glued.'}]
    result=rank_candidates(statements,units,np.array([[1.,0.]]),np.array([[1.,0.],[.99,0.],[.9,0.]]))
    assert statements[0]['original_citations']==['E1']
    assert [h['source_unit_id'] for h in result[0]['candidate_spans']]==['U1','U3']
    assert result[0]['candidate_spans'][0]['in_original_citations'] is False
    assert result[0]['possible_qualification_loss_not_verified'] is True
    assert 'supported' not in result[0]
