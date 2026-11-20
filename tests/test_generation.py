import json
import pytest

from social_listening import generation


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
