"""Fresh-install data boundaries and asset verification, without network or real reviews."""
import copy
import hashlib
import json
from pathlib import Path

import pytest

from product_review_insights import local_app as app


def recipe():
    return {'min_words': 5, 'max_reviews_per_product': 1000, 'language': 'en', 'language_seed': 42}


def test_exact_item_selection_deduplication_and_private_fields(tmp_path):
    rows = [
        {'asin': 'p', 'parent_asin': 'other', 'text': 'This brush has soft bristles and works very well.',
         'title': 'Email me at reviewer@example.com', 'rating': 5, 'user_id': 'PRIVATE', 'images': ['PRIVATE']},
        {'asin': 'p', 'text': 'This brush has soft bristles and works very well.', 'title': 'A brush', 'rating': 2},
        {'asin': 'other', 'parent_asin': 'p', 'text': 'This must not enter the selected product corpus.', 'rating': 1},
    ]
    for i in range(4):
        rows.append({'asin': 'p', 'text': f'The handle broke after {i+2} days of daily brushing at home.', 'rating': 1})
    source = tmp_path/'reviews.jsonl'
    source.write_text(''.join(json.dumps(r)+'\n' for r in rows))
    original = app.product_corpora(source, ['p'], recipe())
    source.write_text(''.join(json.dumps(r)+'\n' for r in reversed(rows)))
    assert app.product_corpora(source, ['p'], recipe()) == original
    assert len(original['p']) == 5
    assert all(set(d) == {'id', 'product_id', 'text', 'title', 'rating'} for d in original['p'])
    assert 'PRIVATE' not in json.dumps(original) and 'reviewer@example.com' not in json.dumps(original)
    assert next(d for d in original['p'] if 'soft bristles' in d['text'])['rating'] == 2


def test_insufficient_product_evidence_stops_preparation(tmp_path):
    source = tmp_path/'reviews.jsonl'
    source.write_text(json.dumps({'asin': 'other', 'text': 'Enough words but the wrong product.', 'rating': 5})+'\n')
    with pytest.raises(ValueError, match='quatro'):
        app.product_corpora(source, ['p'], recipe())


def test_corrupt_download_is_never_published_and_partial_is_removed(tmp_path, monkeypatch):
    import io
    monkeypatch.setattr(app.urllib.request, 'urlopen', lambda *a, **kw: io.BytesIO(b'corrupt'))
    destination = tmp_path/'raw.jsonl'
    spec = {'repository': 'owner/repo', 'revision': 'fixed', 'filename': 'data.jsonl',
            'bytes': 7, 'sha256': hashlib.sha256(b'correct').hexdigest()}
    with pytest.raises(ValueError, match='checksum'):
        app.download_dataset(spec, destination)
    assert not destination.exists() and not destination.with_suffix('.part').exists()


def test_cached_dataset_is_checked_without_network(tmp_path, monkeypatch):
    destination = tmp_path/'raw.jsonl';destination.write_bytes(b'correct')
    monkeypatch.setattr(app.urllib.request, 'urlopen', lambda *a, **kw: pytest.fail('No download for verified cache'))
    assert app.download_dataset({'sha256': hashlib.sha256(b'correct').hexdigest()}, destination) == destination
    destination.write_bytes(b'changed')
    with pytest.raises(ValueError, match='alterado'):
        app.download_dataset({'sha256': hashlib.sha256(b'correct').hexdigest()}, destination)


def test_missing_assets_explain_setup_command(tmp_path):
    with pytest.raises(ValueError, match='setup_demo.py'):
        app.load_application(tmp_path)


def test_changed_application_assets_are_rejected(tmp_path):
    path = tmp_path/app.APP;path.mkdir(parents=True)
    (path/'application.json').write_text(json.dumps({'schema': 'local_application_v1',
        'file_hashes': {'asset': hashlib.sha256(b'original').hexdigest()}}))
    (tmp_path/'asset').write_text('changed')
    with pytest.raises(ValueError, match='alterado'):
        app.load_application(tmp_path)


def test_model_download_is_local_and_only_if_missing(monkeypatch):
    calls = [];models = []
    def api(path, payload=None, **kwargs):
        calls.append((path, payload))
        if path == '/api/version': return {'version': 'local-version'}
        if path == '/api/tags': return {'models': models}
        assert path == '/api/pull' and payload == {'model': 'gemma3:4b', 'stream': False}
        models.append({'name': 'gemma3:4b', 'digest': 'local-digest'})
        return {'status': 'success'}
    monkeypatch.setattr(app.generation, 'api', api)
    model = app.local_model('gemma3:4b')
    assert model['expected_digest'] == 'local-digest' and model['cloud_allowed'] is False
    app.local_model('gemma3:4b')
    assert len([c for c in calls if c[0] == '/api/pull']) == 1
