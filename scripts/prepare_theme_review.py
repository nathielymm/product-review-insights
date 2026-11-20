"""Prepare a local, rating-stratified qualitative audit; not an evaluation set."""
import collections
import hashlib
import json
from pathlib import Path

import pyarrow.parquet as pq

from product_review_insights.data import digest_file, redact
from product_review_insights.diversity import deterministic_sample


def audit_sample(rows, per_band=2, seed=101, product_id=""):
    if per_band < 1 or len({r["id"] for r in rows}) != len(rows):
        raise ValueError("Require a positive quota and unique review identities")
    selected = []
    availability = {}
    for band, ratings in [("low", {1, 2}), ("middle", {3}), ("high", {4, 5})]:
        candidates = [r for r in rows if r["rating"] in ratings]
        availability[band] = len(candidates)
        selected.extend(deterministic_sample(candidates, min(per_band, len(candidates)), seed, product_id))
    remaining = [r for r in rows if r["id"] not in {s["id"] for s in selected}]
    shortfall = per_band * 3 - len(selected)
    selected.extend(deterministic_sample(remaining, shortfall, seed + 1, product_id))
    return selected, availability


def main():
    root = Path("results/theme-review")
    root.mkdir(parents=True, exist_ok=True)
    pools_path = Path("results/diversity-exploration/pools.private.json")
    pool_manifest = json.loads(Path("results/diversity-exploration/pool-manifest.json").read_text())
    if digest_file(pools_path) != pool_manifest["pools_sha256"] or digest_file("data/raw/all_beauty.supplied.parquet") != pool_manifest["source_sha256"]:
        raise ValueError("Review source or eligible pool differs from its recorded audit")
    shortlist_path = Path("configs/diversity-shortlist.draft.json")
    shortlist = json.loads(shortlist_path.read_text())
    config = json.loads(Path("configs/diversity-candidates.draft.json").read_text())
    candidates = {c["id"]: c for c in config["candidates"]}
    ids = {p for cid in shortlist["primary_candidate_triple"] for p in candidates[cid]["product_ids"]}
    pools = json.loads(pools_path.read_text())
    catalog = {}
    for batch in pq.ParquetFile("data/raw/meta_all_beauty.parquet").iter_batches(columns=["parent_asin", "title", "details"]):
        for row in batch.to_pylist():
            if row["parent_asin"] in ids:
                try:
                    attributes = json.loads(row["details"] or "{}")
                except (TypeError, json.JSONDecodeError):
                    attributes = {}
                catalog[row["parent_asin"]] = {"title": row["title"], "brand": attributes.get("Brand"), "item_form": attributes.get("Item Form")}
    packet, products = [], []
    for cid in shortlist["primary_candidate_triple"]:
        for pid in candidates[cid]["product_ids"]:
            selected, availability = audit_sample(pools[pid], product_id=pid)
            products.append({"cohort": cid, "product_id": pid, "pool_size": len(pools[pid]), "availability_by_rating_band": availability,
                             "sample_ratings": dict(collections.Counter(r["rating"] for r in selected)), **catalog[pid]})
            for r in selected:
                packet.append({"audit_id": f"Q{len(packet)+1:03d}", "cohort": cid, "product_id": pid,
                               "official_title": catalog[pid]["title"], "review_id": r["id"],
                               "rating": r["rating"], "text": r["text"], "words": r["words"]})
    # Preserve item-level lineage where a parent listing groups more than one ASIN.
    wanted_reviews = {r["review_id"] for r in packet}
    item_ids = collections.defaultdict(set)
    timestamps = collections.defaultdict(set)
    product_item_ids = collections.defaultdict(set)
    for batch in pq.ParquetFile("data/raw/all_beauty.supplied.parquet").iter_batches(columns=["parent_asin", "asin", "text", "rating", "timestamp"]):
        for row in batch.to_pylist():
            pid = row["parent_asin"]
            if pid not in ids or row["rating"] not in (1, 2, 3, 4, 5):
                continue
            text = redact(" ".join((row["text"] or "").split()))
            if not text:
                continue
            if row["asin"]:
                product_item_ids[pid].add(row["asin"])
            identity = hashlib.sha256((pid + "\0" + text.casefold()).encode()).hexdigest()
            if identity in wanted_reviews:
                if row["asin"]:
                    item_ids[identity].add(row["asin"])
                if row["timestamp"] is not None:
                    timestamps[identity].add(row["timestamp"])
    for row in packet:
        row["item_asins"] = sorted(item_ids[row["review_id"]])
        row["source_timestamps_ms"] = sorted(timestamps[row["review_id"]])
        if not row["item_asins"]:
            raise ValueError("A selected review has no matching source item")
    for row in products:
        row["item_asins_in_valid_raw_reviews"] = sorted(product_item_ids[row["product_id"]])
    (root / "sample.private.json").write_text(json.dumps(packet, ensure_ascii=False, indent=2))
    (root / "products.private.json").write_text(json.dumps(products, ensure_ascii=False, indent=2))
    (root / "sample-manifest.json").write_text(json.dumps({"sampling": "up to 2 low, 2 middle and 2 high ratings per product; deterministic fill for shortages", "seed": 101,
        "status": "assistant_qualitative_review_pending_user_validation", "pool_sha256": digest_file(pools_path),
        "review_source_sha256": digest_file("data/raw/all_beauty.supplied.parquet"),
        "metadata_source_sha256": digest_file("data/raw/meta_all_beauty.parquet"),
        "shortlist_sha256": digest_file(shortlist_path), "sample_sha256": digest_file(root / "sample.private.json"),
        "reviews": len(packet), "products": len(products)}, indent=2))
    print(f"Prepared {len(packet)} reviews from {len(products)} products")


if __name__ == "__main__":
    main()
