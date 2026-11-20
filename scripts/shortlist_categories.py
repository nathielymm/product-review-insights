"""Aggregate narrower cohorts without exporting official titles or review text."""
import collections
import json
import re
from pathlib import Path

from product_review_insights.data import digest_file

root = Path("results/category-map")
products = json.loads((root / "product-assignments.private.json").read_text())
rules_path = Path("configs/category-shortlist-rules.json")
rules = json.loads(rules_path.read_text())
rows = []
for rule in rules["groups"]:
    members = [p for p in products if p["inferred_category"] == rule["parent_category"]
               and p["reviews"] >= rules["min_reviews_per_product"]
               and p["reviews_ge_20_words"] >= rules["min_reviews_ge_20_words"]
               and (not rule.get("include") or re.search(rule["include"], p["official_title"], re.I))
               and (not rule.get("exclude") or not re.search(rule["exclude"], p["official_title"], re.I))]
    members.sort(key=lambda p: (-p["reviews"], p["product_id"]))
    total = sum(p["reviews"] for p in members)
    ratings = collections.Counter()
    for member in members:
        ratings.update(member["rating_counts"])
    rows.append({"id": rule["id"], "label_pt": rule["label_pt"], "products": len(members),
        "reviews": total, "reviews_ge_20_words": sum(p["reviews_ge_20_words"] for p in members),
        "rating_counts": dict(sorted(ratings.items())),
        "top_product_share": members[0]["reviews"] / total if total else None,
        "product_ids": [p["product_id"] for p in members],
        "product_review_counts": {p["product_id"]: p["reviews"] for p in members}})
report = {"status": "candidate_cohorts_not_selected_or_frozen", "rules_sha256": digest_file(rules_path),
          "min_reviews_per_product": rules["min_reviews_per_product"],
          "min_reviews_ge_20_words": rules["min_reviews_ge_20_words"],
          "language_filter_applied": False, "groups_overlap": True, "groups": rows}
(root / "shortlist.json").write_text(json.dumps(report, ensure_ascii=False, indent=2))
print(json.dumps(report, ensure_ascii=False, indent=2))
