import copy
import hashlib
import json

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from product_review_insights.data import digest_file, read_corpus
from product_review_insights.study import (prepare_study, validate_corpus, validate_design,
    validate_index_scope, validate_scoped_chunks)


def make_inputs(tmp_path):
    raw, pools = [], {}
    for pid in ["a", "b", "c", "d", "dev"]:
        pools[pid] = []
        for i in range(4):
            text = f"Synthetic review {i} for family {pid}"
            rid = hashlib.sha256((pid + "\0" + text.casefold()).encode()).hexdigest()
            pools[pid].append({"id": rid, "product_id": pid, "text": text, "rating": 5,
                               "words": 6, "language": "en", "language_score": .99})
            raw.append({"parent_asin": pid, "asin": f"{pid}-item", "text": text, "rating": 5,
                        "timestamp": 1500000000000 + i, "user_id": "DO_NOT_EXPORT"})
    # Exact duplicate body across a different item and rating keeps all lineage.
    raw.append({**raw[0], "asin": "a-variant", "rating": 1})
    pools["a"][0]["rating"] = 1
    source = tmp_path / "source.parquet"
    pq.write_table(pa.Table.from_pylist(raw), source)
    pool_path = tmp_path / "pools.json"
    pool_path.write_text(json.dumps(pools))
    audit = tmp_path / "audit.json"
    audit.write_text(json.dumps([{"review_id": pools["a"][-1]["id"]}]))
    scope = {"scope_version": "test_scope", "cohorts": [
        {"id": "first", "families": [{"parent_asin": p, "functional_label": "test"} for p in ["a", "b"]]},
        {"id": "second", "families": [{"parent_asin": p, "functional_label": "test"} for p in ["c", "d"]]}],
        "development": {"parent_asins": ["dev"], "functional_classes": {"dev": "test"}},
        "sensitivity_analysis": {"reviews_per_family": [1, 2], "seeds": [11]},
        "sources": {"reviews_sha256": digest_file(source), "eligible_pool_sha256": digest_file(pool_path)},
        "sampling": {"audit_review_exclusion_file": str(audit), "audit_review_exclusion_sha256": digest_file(audit),
                     "english_score_threshold": .9, "min_words": 1, "max_words": 200}}
    scope_path = tmp_path / "scope.json"
    scope_path.write_text(json.dumps(scope))
    return scope, scope_path, source, pool_path, audit


def test_full_corpus_preserves_all_eligible_reviews_and_item_lineage(tmp_path):
    scope, config, source, pools, audit = make_inputs(tmp_path)
    out = tmp_path / "out"
    summary = prepare_study(config, source, pools, out)
    assert summary["primary_reviews"] == 15  # 16 eligible minus one reserved audit
    assert [m["reviews"] for m in summary["primary"]] == [7, 8]
    docs = read_corpus(out / "main/first/corpus.jsonl")
    assert len(docs) > 2 * max(scope["sensitivity_analysis"]["reviews_per_family"])
    flagged = next(r for r in docs if r["duplicate_rating_conflict"])
    assert flagged["item_asins"] == ["a-item", "a-variant"] and flagged["rating"] == 1
    assert flagged["source_occurrences"] == 2
    assert all(r["timestamps_ms"] and "user_id" not in r for r in docs)
    assert "DO_NOT_EXPORT" not in (out / "main/first/corpus.jsonl").read_text()
    reserved = json.loads(audit.read_text())[0]["review_id"]
    assert reserved not in {r["id"] for r in docs}
    # Matched views are nested prefixes, not competing "best" datasets.
    for cid in ["first", "second"]:
        one = read_corpus(out / f"sensitivity/n1/seed11/{cid}/corpus.jsonl")
        two = read_corpus(out / f"sensitivity/n2/seed11/{cid}/corpus.jsonl")
        assert len(one) == 2 and len(two) == 4
        assert {r["id"] for r in one} <= {r["id"] for r in two}
    with pytest.raises(FileExistsError):
        prepare_study(config, source, pools, out)


def test_disjoint_design_and_source_checks_fail_before_writing(tmp_path):
    scope, config, source, pools, audit = make_inputs(tmp_path)
    bad = copy.deepcopy(scope)
    bad["development"]["parent_asins"] = ["a"]
    with pytest.raises(ValueError, match="disjoint"):
        validate_design(bad)
    pools.write_text(pools.read_text() + "\n")
    with pytest.raises(ValueError, match="differs"):
        prepare_study(config, source, pools, tmp_path / "out")
    assert not (tmp_path / "out").exists()


def test_scope_guards_reject_global_or_wrong_index_and_foreign_chunks(tmp_path):
    _, config, source, pools, _ = make_inputs(tmp_path)
    out = tmp_path / "out"
    summary = prepare_study(config, source, pools, out)
    manifest = summary["primary"][0]
    metadata = {"study": manifest["study"]}
    assert validate_index_scope(metadata, "first", True)["cohort_id"] == "first"
    for meta, expected in [({}, "first"), (metadata, "second"), (metadata, None)]:
        with pytest.raises(ValueError):
            validate_index_scope(meta, expected, True)
    docs = read_corpus(out / "main/first/corpus.jsonl")
    chunks = [{**d, "review_id": d["id"], "id": d["id"] + ":0"} for d in docs]
    validate_scoped_chunks(chunks, manifest)
    chunks[0]["product_id"] = "foreign-family"
    with pytest.raises(ValueError, match="foreign"):
        validate_scoped_chunks(chunks, manifest)
    docs[0]["product_id"] = "foreign-family"
    with pytest.raises(ValueError, match="foreign"):
        validate_corpus(docs, manifest)


def test_corpus_tampering_invalidates_manifest(tmp_path):
    _, config, source, pools, _ = make_inputs(tmp_path)
    out = tmp_path / "out"
    manifest = prepare_study(config, source, pools, out)["primary"][0]
    path = out / "main/first/corpus.jsonl"
    docs = read_corpus(path)
    path.write_text(path.read_text() + "\n")
    with pytest.raises(ValueError, match="checksum"):
        validate_corpus(docs, manifest, path)
