import json
import pytest

from product_review_insights import generation


def test_context_budget_does_not_truncate_or_fabricate_evidence():
    hits = [{"id": "a", "text": "x" * 200}, {"id": "b", "text": "small"}]
    context, included = generation.pack_context(hits, 80)
    assert len(context) <= 80
    assert [h["id"] for h in included] == ["b"]
    assert included[0]["citation_id"] == "E1"
    assert json.loads(context)["text"] == "small"


def test_generation_uses_local_api_and_same_options(monkeypatch):
    captured = {}
    def fake_api(path, payload):
        captured.update(payload)
        assert path == "/api/chat"
        return {"message": {"content": "Good scent [E1]. Invented [missing]."}, "eval_count": 10}
    monkeypatch.setattr(generation, "api", fake_api)
    config = {"context_chars": 200, "ollama_model": "gemma3:4b", "temperature": 0,
              "seed": 42, "num_ctx": 8192, "num_predict": 100}
    result = generation.generate("What is praised?", [{"id": "a", "text": "Good scent"}], config)
    assert result["citations"]["invalid_citations"] == ["missing"]
    assert result["citations"]["citation_id_precision"] == 0.5
    assert captured["options"]["seed"] == 42
    assert captured["stream"] is False


def test_no_evidence_abstains_without_calling_model(monkeypatch):
    monkeypatch.setattr(generation, "api", lambda *a: (_ for _ in ()).throw(AssertionError()))
    assert generation.generate("Question", [], {"context_chars": 100})["evidence"] == []


def test_cloud_model_rejected():
    with pytest.raises(ValueError, match="Cloud models"):
        generation.generate("Question", [], {"ollama_model": "some-model:cloud"})


def test_evidence_keeps_family_identity_without_inheriting_catalog_claims():
    text, included = generation.pack_context([{"id": "r", "text": "Reported experience", "product_id": "family",
        "functional_class": "mascara", "official_title": "Unverified waterproof version"}], 500)
    block = json.loads(text)
    assert block["product_group"] == "family" and block["functional_class"] == "mascara"
    assert "waterproof" not in text


def test_short_group_aliases_distinguish_products_with_the_same_function():
    context, included = generation.pack_context([
        {'id':'a','text':'First experience','product_id':'deodorant-a','functional_class':'deodorant'},
        {'id':'b','text':'Second experience','product_id':'deodorant-b','functional_class':'deodorant'},
        {'id':'c','text':'Another first-product experience','product_id':'deodorant-a','functional_class':'deodorant'}],2000)
    blocks=[json.loads(line) for line in context.splitlines()]
    assert [b['group_alias'] for b in blocks]==['G1','G2','G1']
    assert [h['group_alias'] for h in included]==['G1','G2','G1']
    assert [b['evidence_id'] for b in blocks]==['E1','E2','E3']
    assert len({b['product_group'] for b in blocks})==2


def test_structured_validation_rejects_cross_family_citations_without_repair():
    included=[{'citation_id':'E1','group_alias':'G1','product_id':'a'},
              {'citation_id':'E2','group_alias':'G2','product_id':'b'}]
    data={'groups':{'G1':[{'observation':'Reported problem','proposal':'Investigate','uncertainty':'Unverified',
                        'citations':['E1','E2']}],'G2':[]},'limits':''}
    with pytest.raises(ValueError,match='different groups'):
        generation.validate_and_render_structured(json.dumps(data),included)
    data['groups']['G1'][0]['citations']=['E1']
    rendered,original=generation.validate_and_render_structured(json.dumps(data),included)
    assert 'G1 (a): Reported problem [E1]' in rendered and original==data
    assert generation.response_schema(included)['properties']['groups']['properties']['G1']['items']['properties']['citations']['items']['enum']==['E1']


def test_structured_generation_keeps_invalid_raw_output_and_marks_failure(monkeypatch):
    raw='{"findings": ['
    monkeypatch.setattr(generation,'api',lambda *a,**k:{'message':{'content':raw},'done_reason':'length'})
    config={'structured_output':True,'context_chars':1000,'ollama_model':'gemma3:4b','temperature':0,'seed':42,'num_ctx':8192,'num_predict':100}
    result=generation.generate('Question',[{'id':'r','text':'Reported problem','product_id':'a'}],config)
    assert result['raw_model_output']==raw==result['answer']
    assert not result['structured_validation']['valid']


def test_structured_contract_rejects_embedded_citations_instead_of_silently_fixing_them():
    evidence=[{'citation_id':'E1','group_alias':'G1','product_id':'a'}]
    data={'groups':{'G1':[{'citations':['E1'],'observation':'Reported [E9]','proposal':'','uncertainty':''}]},'limits':''}
    with pytest.raises(ValueError,match='embed citation'):
        generation.validate_and_render_structured(json.dumps(data),evidence)


def test_structured_request_has_its_own_nonconflicting_system_contract(monkeypatch):
    captured={}
    def fake(path,payload):
        captured.update(payload)
        return {'message':{'content':'{"groups": {"G1": []}, "limits": "Insufficient evidence."}'},'done_reason':'stop'}
    monkeypatch.setattr(generation,'api',fake)
    config={'structured_output':True,'context_chars':1000,'ollama_model':'gemma3:4b','temperature':0,'seed':42,'num_ctx':8192,'num_predict':100}
    result=generation.generate('Question',[{'id':'r','text':'Experience','product_id':'a'}],config)
    assert captured['messages'][0]['content']==generation.STRUCTURED_SYSTEM
    assert captured['messages'][0]['content']!=generation.SYSTEM
    assert result['generation_contract']['schema']==captured['format']
    assert result['structured_validation']['valid'] and result['raw_model_output'].startswith('{')
