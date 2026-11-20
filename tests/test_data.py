import json

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from social_listening.data import prepare, read_corpus, redact


def test_ingestion_is_order_independent_and_excludes_private_fields(tmp_path):
    rows = [{"text": f"Review {i} contact a@example.com", "title": "Title", "rating": (i % 5) + 1,
             "parent_asin": "product", "user_id": "private-user"} for i in range(12)]
    rows += [{**rows[0], "title": "Another title", "text": rows[0]["text"].upper()},
             {**rows[0], "text": ""}, {**rows[1], "rating": 0}]
    first, second = tmp_path / "a.parquet", tmp_path / "b.parquet"
    pq.write_table(pa.Table.from_pylist(rows), first)
    pq.write_table(pa.Table.from_pylist(list(reversed(rows))), second)
    a = prepare(first, tmp_path / "a", size=5)
    b = prepare(second, tmp_path / "b", size=5)
    assert a["corpus_sha256"] == b["corpus_sha256"]
    assert a["valid_unique_rating_counts"] == b["valid_unique_rating_counts"]
    assert a["duplicates"] == 1 and a["empty_text"] == 1 and a["invalid_rating"] == 1
    corpus = read_corpus(tmp_path / "a/corpus.jsonl")
    assert len(corpus) == 5
    assert all("user_id" not in d and "a@example.com" not in d["text"] for d in corpus)
    assert len({d["id"] for d in corpus}) == 5


def test_schema_rejected(tmp_path):
    path = tmp_path / "wrong.parquet"
    pq.write_table(pa.Table.from_pylist([{"text": "hi"}]), path)
    with pytest.raises(ValueError, match="Missing fields"):
        prepare(path, tmp_path / "out")


def test_redaction():
    assert redact("email me at name@example.org or https://example.org") == "email me at [EMAIL] or [URL]"
