"""Aspect pool and source-bound output contracts, without private corpora/models."""
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
import pytest


def load_module(monkeypatch):
    scripts=Path(__file__).resolve().parents[1]/'scripts';monkeypatch.syspath_prepend(str(scripts))
    spec=importlib.util.spec_from_file_location('aspect_pilot',scripts/'run_product_aspect_pilot.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


def test_aspect_union_retains_specialist_results_and_deduplicates_reviews(monkeypatch):
    import numpy as np
    m=load_module(monkeypatch)
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


def test_atomic_contract_requires_literal_own_source_and_short_fields(monkeypatch):
    m=load_module(monkeypatch);spec=json.loads((m.Path(__file__).resolve().parents[1]/'configs/curly-product-pilot.v2-aspects.json').read_text())
    q=spec['questions'][0];limits=spec['generation'];evidence=[{'citation_id':'E1','text':'it collapses during use'},{'citation_id':'E2','text':'fits well'}]
    finding={'id':'F1','aspect':'collapse','kind':'problem','evidence_id':'E1','quote':'collapses during use','observation':'A pessoa relata colapso durante o uso.','condition':'','proposal':'','verification':''}
    data={'findings':[finding],'limits':''}
    assert m.validate_atomic(json.dumps(data),evidence,q,limits)==data
    finding['evidence_id']='E2'
    with pytest.raises(ValueError,match='literal'):m.validate_atomic(json.dumps(data),evidence,q,limits)
    finding['evidence_id']='E1';finding['proposal']='Mudar o produto.'
    with pytest.raises(ValueError):m.validate_atomic(json.dumps(data),evidence,q,limits)
    finding['proposal']='';finding['observation']='x'*(limits['max_observation_chars']+1)
    with pytest.raises(ValueError,match='length'):m.validate_atomic(json.dumps(data),evidence,q,limits)


def test_praise_cannot_be_relabelled_as_corrective_proposal(monkeypatch):
    m=load_module(monkeypatch);spec=json.loads((Path(__file__).resolve().parents[1]/'configs/curly-product-pilot.v2-aspects.json').read_text())
    finding={'id':'F1','aspect':'fit','kind':'valued_quality','evidence_id':'E1','quote':'fits well','observation':'Encaixe valorizado.','condition':'','proposal':'Corrigir o encaixe.','verification':''}
    with pytest.raises(ValueError,match='without problem'):
        m.validate_atomic(json.dumps({'findings':[finding],'limits':''}),[{'citation_id':'E1','text':'fits well'}],spec['questions'][1],spec['generation'])


def test_prior_aspect_runs_are_preserved_before_any_api_call(tmp_path,monkeypatch):
    m=load_module(monkeypatch);p=tmp_path/'old';p.mkdir();(p/'runs.private.jsonl').write_text('preserve')
    monkeypatch.setattr(m,'api',lambda *a,**kw:pytest.fail('No API before preservation guard'))
    with pytest.raises(FileExistsError):m.run({'results':str(p)},'unused')
    assert (p/'runs.private.jsonl').read_text()=='preserve'


def test_rejected_output_diagnostics_never_turn_into_accepted_findings(monkeypatch):
    import copy
    scripts=Path(__file__).resolve().parents[1]/'scripts';monkeypatch.syspath_prepend(str(scripts))
    spec=importlib.util.spec_from_file_location('aspect_report',scripts/'report_product_aspect_pilot.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    row={'question_id':'P01','method':'traditional','evidence':[{'citation_id':'E1','review_id':'r','cluster':1,'text':'exact source'}],
         'total_seconds':1.,'ollama':{},'generation_error':None,'format_valid':False,'format_error':'Quote not literal in cited source',
         'candidate_count':1,'candidate_cluster_counts':{1:1},'candidate_pool_sha256':'same',
         'raw_model_output':json.dumps({'findings':[{'evidence_id':'E1','quote':'exact source'},{'evidence_id':'E1','quote':'invented quote'}]})}
    original=copy.deepcopy(row);result=m.summarize(row,'v2')
    assert result['contract_valid'] is False and result['literal_quotes']==1 and result['nonliteral_quotes']==1
    assert result['declared_cited_reviews']==1 and result['declared_findings']==2
    assert row==original
