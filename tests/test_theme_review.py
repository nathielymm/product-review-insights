import json

import pytest

from product_review_insights.data import digest_file
from scripts.prepare_theme_review import audit_sample
from scripts.summarize_theme_review import summarize


def test_audit_sample_fills_missing_rating_band_without_duplicates():
    rows = [{"id": str(i), "rating": 1 if i < 2 else 5} for i in range(8)]
    selected, availability = audit_sample(rows, product_id="synthetic")
    assert len(selected) == len({r["id"] for r in selected}) == 6
    assert availability["middle"] == 0
    assert selected == audit_sample(list(reversed(rows)), product_id="synthetic")[0]
    with pytest.raises(ValueError):
        audit_sample(rows[:5], product_id="synthetic")
    with pytest.raises(ValueError, match="unique review"):
        audit_sample(rows + [rows[0]], product_id="synthetic")


def fixture_files(tmp_path):
    packet = [{"audit_id": "Q001", "cohort": "test", "product_id": "p", "review_id": "r", "rating": 5}]
    products = [{"cohort": "test", "product_id": "p", "item_asins_in_valid_raw_reviews": ["item"]}]
    codebook = {"themes": [{"id": "T01"}], "consistency": {"compatible": "test"}, "explicit_request_types": ["none"]}
    paths = [tmp_path / name for name in ["packet.json", "products.json", "coding.json", "codebook.json"]]
    for path, data in [(paths[0], packet), (paths[1], products), (paths[3], codebook)]:
        path.write_text(json.dumps(data))
    coding = {"reviewer": "assistant", "sample_sha256": digest_file(paths[0]), "codebook_sha256": digest_file(paths[3]),
        "annotations": [{"audit_id": "Q001", "cohort": "test", "product_id": "p", "review_id": "r", "themes": ["T01"],
                         "consistency": "compatible", "explicit_request_type": "none", "flags": []}]}
    paths[2].write_text(json.dumps(coding))
    return paths


def test_qualitative_summary_is_not_a_human_reference_and_checks_identity(tmp_path):
    paths = fixture_files(tmp_path)
    result = summarize(*paths)
    assert result["reviews_inspected"] == 1
    assert result["independent_human_validation_completed"] is False
    assert result["cohorts"][0]["theme_review_counts"] == {"T01": 1}
    coding = json.loads(paths[2].read_text())
    coding["annotations"][0]["review_id"] = "wrong-source"
    paths[2].write_text(json.dumps(coding))
    with pytest.raises(ValueError, match="identity differs"):
        summarize(*paths)


def test_changed_sample_or_codebook_invalidates_qualitative_summary(tmp_path):
    paths = fixture_files(tmp_path)
    paths[0].write_text(paths[0].read_text() + "\n")
    with pytest.raises(ValueError, match="does not match"):
        summarize(*paths)
