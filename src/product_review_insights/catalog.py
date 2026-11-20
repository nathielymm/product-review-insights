"""Exploratory title taxonomy joined to the locally audited review population."""
import collections
import hashlib
import html
import json
import re
import statistics
from pathlib import Path

from .data import digest_file, redact


def classify_title(title, rules):
    title = html.unescape(title or "").casefold()
    matches = [rule["id"] for rule in rules if re.search(rule["include"], title, re.I)
               and not (rule.get("exclude") and re.search(rule["exclude"], title, re.I))]
    return (matches[0] if len(matches) == 1 else "ambiguous" if matches else "unclassified"), matches


def review_statistics(source):
    import pyarrow.parquet as pq
    products = {}
    seen = {}
    for batch in pq.ParquetFile(source).iter_batches(columns=["parent_asin", "text", "rating"]):
        for row in batch.to_pylist():
            text = redact(" ".join((row["text"] or "").split()))
            if not text or row["rating"] not in (1, 2, 3, 4, 5) or not row["parent_asin"]:
                continue
            pid = row["parent_asin"]
            identity = hashlib.sha256((pid + "\0" + text.casefold()).encode()).hexdigest()
            rating = int(row["rating"])
            stats = products.setdefault(pid, {"reviews": 0, "ratings": collections.Counter(), "reviews_ge_20_words": 0})
            if identity in seen:
                previous = seen[identity]
                if rating < previous:
                    stats["ratings"][previous] -= 1
                    stats["ratings"][rating] += 1
                    seen[identity] = rating
                continue
            seen[identity] = rating
            stats["reviews"] += 1
            stats["ratings"][rating] += 1
            stats["reviews_ge_20_words"] += len(text.split()) >= 20
    return products


def map_categories(reviews, metadata, rules_path, output):
    import pyarrow.parquet as pq
    rules_document = json.loads(Path(rules_path).read_text())
    rules = rules_document["rules"]
    products = review_statistics(reviews)
    catalog, conflicts = {}, set()
    metadata_rows = 0
    nonempty_subcategories = 0
    main = collections.Counter()
    for batch in pq.ParquetFile(metadata).iter_batches(columns=["parent_asin", "title", "categories", "main_category"]):
        for row in batch.to_pylist():
            metadata_rows += 1
            nonempty_subcategories += bool(row["categories"])
            main[row["main_category"]] += 1
            pid = row["parent_asin"]
            record = {"title": row["title"] or "", "official_main_category": row["main_category"]}
            if pid in catalog and catalog[pid] != record:
                conflicts.add(pid)
            catalog[pid] = record
    assignments, groups = [], collections.defaultdict(list)
    for pid, stats in sorted(products.items()):
        record = catalog.get(pid)
        if record is None:
            category, matches = "missing_metadata", []
        elif pid in conflicts:
            category, matches = "conflicting_metadata", []
        else:
            category, matches = classify_title(record["title"], rules)
        item = {"product_id": pid, "inferred_category": category, "matching_rules": matches,
                "official_title": record["title"] if record else None,
                "reviews": stats["reviews"], "rating_counts": dict(sorted(stats["ratings"].items())),
                "reviews_ge_20_words": stats["reviews_ge_20_words"]}
        assignments.append(item)
        groups[category].append(item)
    labels = {r["id"]: r["label_pt"] for r in rules}
    summaries = []
    for category, members in groups.items():
        eligible = [p for p in members if p["reviews"] >= 100 and p["reviews_ge_20_words"] >= 30]
        values = sorted(p["reviews"] for p in members)
        total = sum(values)
        ratings = collections.Counter()
        for member in members:
            ratings.update(member["rating_counts"])
        summaries.append({"category_id": category, "label_pt": labels.get(category, category),
            "products": len(members), "reviews": total,
            "products_by_min_reviews": {str(n): sum(v >= n for v in values) for n in [20, 50, 100, 200, 500]},
            "eligible_products_100_reviews_30_long": len(eligible),
            "eligible_reviews": sum(p["reviews"] for p in eligible),
            "rating_counts": dict(sorted(ratings.items())),
            "median_reviews_per_product": statistics.median(values),
            "top_product_share_all_category_reviews": max(values) / total,
            "top_three_share_all_category_reviews": sum(values[-3:]) / total,
            "screening_candidate": category in labels and len(eligible) >= 5 and sum(p["reviews"] for p in eligible) >= 1000})
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    report = {"status": "exploratory_title_taxonomy_not_official_categories",
        "review_source_sha256": digest_file(reviews), "metadata_source_sha256": digest_file(metadata),
        "rules_sha256": digest_file(rules_path), "rules_version": rules_document["version"],
        "metadata_rows": metadata_rows, "metadata_unique_ids": len(catalog),
        "metadata_ids_with_conflicting_titles": len(conflicts),
        "metadata_nonempty_subcategories": nonempty_subcategories,
        "metadata_main_categories": dict(main), "review_products": len(products),
        "valid_unique_reviews": sum(p["reviews"] for p in products.values()),
        "joined_products": sum(p in catalog for p in products),
        "classification_policy": rules_document["policy"],
        "screening_rule": "at least 5 products each with >=100 valid unique reviews and >=30 reviews of >=20 words, >=1000 eligible reviews total",
        "language_filter_applied": False,
        "categories": sorted(summaries, key=lambda s: (-s["eligible_products_100_reviews_30_long"], -s["eligible_reviews"], s["category_id"]))}
    (output / "category-summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2))
    # Titles and per-product data remain local; do not commit or publish.
    (output / "product-assignments.private.json").write_text(json.dumps(assignments, ensure_ascii=False, indent=2))
    return report
