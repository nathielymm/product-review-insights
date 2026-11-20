"""Validate local qualitative coding and export only aggregate, provisional findings."""
import collections
import itertools
import json
from pathlib import Path

from product_review_insights.data import digest_file


def summarize(packet_path, products_path, coding_path, codebook_path):
    packet = json.loads(Path(packet_path).read_text())
    products = json.loads(Path(products_path).read_text())
    coding = json.loads(Path(coding_path).read_text())
    codebook = json.loads(Path(codebook_path).read_text())
    if coding["sample_sha256"] != digest_file(packet_path) or coding["codebook_sha256"] != digest_file(codebook_path):
        raise ValueError("Coding does not match the sample or codebook")
    source = {r["audit_id"]: r for r in packet}
    annotations = coding["annotations"]
    if len(source) != len(packet) or len({r["audit_id"] for r in annotations}) != len(annotations):
        raise ValueError("Duplicate audit identity")
    if set(source) != {r["audit_id"] for r in annotations}:
        raise ValueError("Coding does not cover the exact review sample")
    allowed_themes = {t["id"] for t in codebook["themes"]}
    for row in annotations:
        original = source[row["audit_id"]]
        if any(row[k] != original[k] for k in ["cohort", "product_id", "review_id"]):
            raise ValueError("Annotation identity differs from sample")
        if not set(row["themes"]) <= allowed_themes or len(row["themes"]) != len(set(row["themes"])):
            raise ValueError("Unknown or duplicate theme code")
        if row["consistency"] not in codebook["consistency"] or row["explicit_request_type"] not in codebook["explicit_request_types"]:
            raise ValueError("Unknown consistency/request code")
    cohorts = []
    for cid in dict.fromkeys(r["cohort"] for r in packet):
        sample = [r for r in annotations if r["cohort"] == cid]
        cohort_products = [p for p in products if p["cohort"] == cid]
        themes = collections.Counter(t for r in sample for t in r["themes"])
        theme_products = {t: len({r["product_id"] for r in sample if t in r["themes"]}) for t in allowed_themes}
        cohorts.append({"cohort": cid, "reviews_inspected": len(sample), "products_inspected": len(cohort_products),
            "broad_themes_observed": len(themes), "theme_review_counts": dict(sorted(themes.items())),
            "theme_product_counts": dict(sorted(theme_products.items())),
            "consistency_counts": dict(collections.Counter(r["consistency"] for r in sample)),
            "flag_counts": dict(collections.Counter(f for r in sample for f in r["flags"])),
            "explicit_request_types": dict(collections.Counter(r["explicit_request_type"] for r in sample)),
            "sample_rating_counts": dict(sorted(collections.Counter(source[r["audit_id"]]["rating"] for r in sample).items())),
            "products_with_multiple_item_asins_in_valid_raw_reviews": sum(len(p["item_asins_in_valid_raw_reviews"]) > 1 for p in cohort_products),
            "products": [{"product_id": p["product_id"], "inspected": sum(r["product_id"] == p["product_id"] for r in sample),
                "item_asins_in_valid_raw_reviews": len(p["item_asins_in_valid_raw_reviews"]),
                "consistency_counts": dict(collections.Counter(r["consistency"] for r in sample if r["product_id"] == p["product_id"]))}
                for p in cohort_products]})
    overlap = []
    for a, b in itertools.combinations(cohorts, 2):
        ta, tb = set(a["theme_review_counts"]), set(b["theme_review_counts"])
        overlap.append({"a": a["cohort"], "b": b["cohort"], "shared_broad_themes": len(ta & tb),
                        "theme_set_jaccard": len(ta & tb) / len(ta | tb) if ta | tb else None})
    return {"status": "assistant_review_pending_user_validation_not_gold_reference",
        "reviews_inspected": len(packet), "products_inspected": len(products),
        "reviewer": coding["reviewer"], "independent_human_validation_completed": False,
        "sample_sha256": digest_file(packet_path), "coding_sha256": digest_file(coding_path),
        "codebook_sha256": digest_file(codebook_path),
        "sampling": "six reviews per product, rating-stratified with deterministic fill for shortages; not population-representative",
        "cohorts": cohorts, "broad_theme_overlap": overlap,
        "warning": "Counts are descriptive for the inspected sample and depend on coding granularity. No RAG scores, clinical conclusions, fraud findings or corpus-wide consistency guarantees."}


if __name__ == "__main__":
    root = Path("results/theme-review")
    report = summarize(root / "sample.private.json", root / "products.private.json",
                       root / "assistant-coding.private.json", "configs/theme-review-codebook.draft.json")
    (root / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"reviews": report["reviews_inspected"], "products": report["products_inspected"],
                      "cohorts": [{k: c[k] for k in ["cohort", "broad_themes_observed", "consistency_counts", "explicit_request_types"]} for c in report["cohorts"]]}, indent=2))
