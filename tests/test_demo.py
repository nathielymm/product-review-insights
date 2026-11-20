"""Demonstration boundary tests, without models or private consumer data."""
import importlib.util
from pathlib import Path
import pytest

spec = importlib.util.spec_from_file_location('demo_server', Path(__file__).resolve().parents[1] / 'scripts/serve_demo.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_demo_validation_and_evidence_boundary(monkeypatch):
    demo = module.Demo()
    calls = []
    class FakeRetriever:
        def __init__(self, path):
            calls.append(path)
        def search(self, question, thematic=False):
            calls.append((question, thematic))
            return [{'text': 'included'}, {'text': 'excluded'}]
    def fake_generate(question, hits, config):
        return {'answer': 'Finding [E1]', 'evidence': [{'citation_id': 'E1', 'text': hits[0]['text'], 'product_id': 'example'}], 'ollama': {}, 'structured_validation': {'valid': True}}
    monkeypatch.setattr(module, 'Retriever', FakeRetriever)
    monkeypatch.setattr(module, 'generate', fake_generate)
    for bad in [{}, {'question': ' ', 'cohort': 'compact_mascaras', 'method': 'traditional'}, {'question': 'test', 'cohort': '../../', 'method': 'traditional'}]:
        with pytest.raises(ValueError):
            demo.answer(bad)
    result = demo.answer({'question': 'test', 'cohort': 'compact_mascaras', 'method': 'thematic'})
    assert calls[-1] == ('test', True)
    assert [x['text'] for x in result['evidence']] == ['included']
    assert result['demo_only'] and result['format_valid']


def test_generation_failure_releases_demo_lock(monkeypatch):
    demo = module.Demo()
    class Broken:
        def search(self, *args, **kwargs):
            raise RuntimeError('offline')
    demo.retrievers['compact_mascaras'] = Broken()
    with pytest.raises(RuntimeError):
        demo.answer({'question': 'test', 'cohort': 'compact_mascaras', 'method': 'traditional'})
    assert not demo.lock.locked()


def test_portuguese_demo_keeps_sources_and_frozen_prompt(monkeypatch):
    from product_review_insights.generation import STRUCTURED_SYSTEM
    hits = [{'text': 'Original English evidence', 'product_id': 'B08TCBP8HV'}]
    config = module.Demo().freeze['config']
    original = dict(config)
    def fake_api(path, payload):
        assert 'Brazilian Portuguese' in payload['messages'][0]['content']
        assert 'Original English evidence' in payload['messages'][1]['content']
        assert 'Essence Lash Princess' not in payload['messages'][1]['content']
        return {'message': {'content': '{"groups":{"G1":[{"observation":"Relato de dificuldade.","proposal":"Rever o aplicador.","uncertainty":"Verificar o uso.","citations":["E1"]}]},"limits":"Amostra limitada."}'}, 'done_reason': 'stop'}
    monkeypatch.setattr(module, 'api', fake_api)
    result = module.generate('Que melhorias investigar?', hits, config)
    assert 'Melhoria proposta: Rever o aplicador.' in result['answer']
    assert 'Incerteza: Verificar o uso.' in result['answer']
    assert 'Limites das evidências: Amostra limitada.' in result['answer']
    assert '[E1]' in result['answer']
    assert 'Máscara de cílios · Essence Lash Princess — G1 (B08TCBP8HV)' in result['answer']
    assert result['evidence'][0]['text'] == hits[0]['text']
    assert config == original
    assert 'Use concise English sentences.' in STRUCTURED_SYSTEM


def test_product_labels_cover_study_without_merging_families():
    import json
    scope = json.loads((module.ROOT / 'configs/study-scope.json').read_text())
    ids = {f['parent_asin'] for c in scope['cohorts'] for f in c['families']}
    assert set(module.PRODUCT_LABELS) == ids
    assert len(set(module.PRODUCT_LABELS.values())) == 15
    assert 'Essence Lash Princess' in module.product_label('B08TCBP8HV')
    assert module.product_label('unknown') == 'Família de produto não identificada'


def test_demo_groups_findings_without_rewriting_them(monkeypatch):
    demo = module.Demo()
    findings = [{'observation': 'Relato original.', 'proposal': 'Sugestão original.', 'uncertainty': 'Verificar.', 'citations': ['E1']}]
    demo.retrievers['compact_mascaras'] = type('RetrieverStub', (), {'search': lambda *a, **k: []})()
    monkeypatch.setattr(module, 'generate', lambda *args: {
        'answer': 'Original', 'evidence': [{'citation_id': 'E1', 'group_alias': 'G1', 'product_id': 'B08TCBP8HV', 'text': 'Source'}],
        'structured': {'groups': {'G1': findings, 'G2': []}, 'limits': 'Amostra limitada.'},
        'ollama': {}, 'structured_validation': {'valid': True}})
    result = demo.answer({'question': 'test', 'cohort': 'compact_mascaras', 'method': 'traditional'})
    assert len(result['products']) == 1
    assert result['products'][0]['findings'] == findings
    assert result['products'][0]['name'] == module.product_label('B08TCBP8HV')
    assert result['limits'] == 'Amostra limitada.'


def test_cited_scope_counts_unique_reviews_and_only_cited_products():
    result = {'structured': {'groups': {'G1': [{'citations': ['E1', 'E2', 'E1']}]}},
              'evidence': [{'citation_id': 'E1', 'review_id': 'review-a', 'product_id': 'product-a'},
                           {'citation_id': 'E2', 'id': 'review-a:1', 'product_id': 'product-a'},
                           {'citation_id': 'E3', 'review_id': 'review-b', 'product_id': 'product-b'}]}
    assert module.cited_scope(result) == {'reviews': 1, 'products': 1}
    result['structured']['groups']['G2'] = [{'citations': ['E3']}]
    assert module.cited_scope(result) == {'reviews': 2, 'products': 2}
    assert module.cited_scope({'evidence': []}) is None
    assert module.cited_scope({'structured': {'groups': {}}, 'evidence': []}) == {'reviews': 0, 'products': 0}


def test_product_search_restricts_candidates_before_ranking():
    import faiss
    import numpy as np
    from types import SimpleNamespace
    vectors = np.array([[1., 0.], [.9, .1], [.8, .2], [.7, .3]], dtype='float32')
    index = faiss.IndexFlatIP(2)
    index.add(vectors)
    r = SimpleNamespace(index=index, documents=[{'product_id': p, 'id': str(i)} for i,p in enumerate(['other','other','target','target'])],
        clusters=np.array([0,1,0,1]), config={'candidate_pool': 2, 'top_k': 2},
        model=SimpleNamespace(encode=lambda *a, **k: np.array([[1.,0.]], dtype='float32')))
    searcher = module.ProductSearch(r, 'target')
    for thematic in [False, True]:
        hits = searcher.search('question', thematic)
        assert [h['id'] for h in hits] == ['2','3']
        assert {h['product_id'] for h in hits} == {'target'}
    assert index.ntotal == 4
    with pytest.raises(ValueError): module.ProductSearch(r,'missing')


def test_demo_rejects_product_from_another_cohort_before_search():
    demo = module.Demo()
    with pytest.raises(ValueError, match='pertencente'):
        demo.answer({'question':'test','cohort':'compact_mascaras','method':'traditional','product_id':'B012Q9NGE4'})
    assert demo.retrievers == {} and not demo.lock.locked()
