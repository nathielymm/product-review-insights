"""Pilot gates: isolate one product and preserve prior results before model calls."""
import importlib.util
import json
from pathlib import Path
import pytest


def load_module(monkeypatch):
    scripts=Path(__file__).resolve().parents[1]/'scripts'
    monkeypatch.syspath_prepend(str(scripts))
    spec=importlib.util.spec_from_file_location('product_pilot',scripts/'run_product_pilot.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def test_foreign_product_rejected_even_when_hash_and_count_match(tmp_path,monkeypatch):
    m=load_module(monkeypatch);corpus=tmp_path/'corpus.jsonl'
    corpus.write_text(json.dumps({'id':'a','product_id':'foreign','text':'text'})+'\n')
    spec=tmp_path/'spec.json';spec.write_text(json.dumps({'corpus':str(corpus),'corpus_sha256':m.digest_file(corpus),'expected_reviews':1,'product_id':'target'}))
    with pytest.raises(ValueError,match='Foreign product'):m.load_spec(spec)
    corpus.write_text(json.dumps({'id':'a','product_id':'target','text':'changed'})+'\n')
    with pytest.raises(ValueError,match='hash differs'):m.load_spec(spec)


def test_pilot_never_overwrites_previous_runs_or_calls_model(tmp_path,monkeypatch):
    m=load_module(monkeypatch);folder=tmp_path/'results';folder.mkdir()
    (folder/'runs.private.jsonl').write_text('preserve')
    monkeypatch.setattr(m,'api',lambda *a,**k:pytest.fail('No API call allowed before overwrite guard'))
    with pytest.raises(FileExistsError):m.run({'results':str(folder)},'unused')
    assert (folder/'runs.private.jsonl').read_text()=='preserve'
