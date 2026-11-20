import pytest

from product_review_insights.experiments import human_metrics
from product_review_insights.experiments import paired_bootstrap, evaluate, blind
import csv
import json


def test_missing_annotations_are_not_zero_scores():
    assert human_metrics({})["faithfulness"] is None


def test_metrics_match_manual_counts():
    scores = human_metrics({"reference_theme_count": "4", "covered_reference_themes": "3",
                           "factual_claims": "5", "supported_claims": "3", "contradicted_claims": "1"})
    assert scores == {"coverage": .75, "faithfulness": .6, "contradiction_rate": .2}


def test_invalid_annotation_rejected():
    with pytest.raises(ValueError):
        human_metrics({"reference_theme_count": 1, "covered_reference_themes": 2,
                       "factual_claims": 2, "supported_claims": 1, "contradicted_claims": 0})


def test_bootstrap_averages_repeats_before_resampling_questions():
    result = paired_bootstrap({"a": [1, 3], "b": [4]}, iterations=100)
    assert result["questions"] == 2
    assert result["mean_delta_thematic_minus_traditional"] == 3
    assert result["ci95"] == [2, 4]
    assert paired_bootstrap({}) is None


def test_blinded_export_and_paired_report_do_not_impute_missing_scores(tmp_path):
    path = tmp_path / "runs.jsonl"
    rows = [{"question_id": "q", "question": "synthetic question", "repeat": 0,
             "method": method, "answer": "Synthetic [a]", "evidence": [{"id": "a", "text": "Synthetic", "cluster": 9, "score": .9}],
             "total_seconds": seconds, "retrieval_seconds": .1, "generation_seconds": seconds - .1}
            for method, seconds in [("traditional", 1), ("thematic", 2)]]
    path.write_text("".join(json.dumps(r) + "\n" for r in rows))
    out = tmp_path / "blind"
    blind(path, out)
    exported = json.loads((out / "blind.json").read_text())
    assert all("method" not in r and "cluster" not in r["evidence"][0] for r in exported)
    report = evaluate(path, out / "annotations.csv", out / "key.private.json")
    assert report["paired_comparisons"]["coverage"] is None
    assert report["paired_comparisons"]["total_seconds"]["mean_delta_thematic_minus_traditional"] == 1
    key = json.loads((out / "key.private.json").read_text())
    with (out / "annotations.csv").open("w") as stream:
        writer = csv.DictWriter(stream, fieldnames=["annotation_id", "reference_theme_count", "covered_reference_themes", "factual_claims", "supported_claims", "contradicted_claims"])
        writer.writeheader()
        for annotation_id, item in key.items():
            writer.writerow({"annotation_id": annotation_id, "reference_theme_count": 2,
                             "covered_reference_themes": 2 if item["method"] == "thematic" else 1,
                             "factual_claims": 1, "supported_claims": 1, "contradicted_claims": 0})
    assert evaluate(path, out / "annotations.csv", out / "key.private.json")["paired_comparisons"]["coverage"]["mean_delta_thematic_minus_traditional"] == .5
