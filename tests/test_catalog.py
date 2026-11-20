import json
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from product_review_insights.catalog import classify_title, map_categories


RULES = [
    {"id": "shampoo", "label_pt": "Shampoos", "include": r"\bshampoo\b", "exclude": r"\bbrush\b"},
    {"id": "conditioner", "label_pt": "Condicionadores", "include": r"\bconditioner\b"},
]


def test_title_classifier_preserves_unknowns_ambiguity_and_accessory_exclusions():
    assert classify_title("A shampoo", RULES) == ("shampoo", ["shampoo"])
    assert classify_title("Shampoo &amp; Conditioner set", RULES)[0] == "ambiguous"
    assert classify_title("Shampoo brush", RULES)[0] == "unclassified"
    assert classify_title("unrelated product", RULES)[0] == "unclassified"


def test_production_rules_do_not_confuse_accessories_and_multicomponent_products():
    rules = json.loads((Path(__file__).parents[1] / "configs/category-rules.json").read_text())["rules"]
    assert classify_title("Refillable Travel Bottles for Shampoo", rules)[0] != "shampoo"
    assert classify_title("Makeup Brush Cleaning Mat", rules)[0] != "makeup_brush"
    assert classify_title("Magnetic Eyelashes with Eyeliner Kit", rules)[0] == "magnetic_eyelashes"
    assert classify_title("Shampoo and Conditioner Set", rules)[0] == "ambiguous"


def test_catalog_join_does_not_invent_categories_or_count_missing_evidence(tmp_path):
    reviews = [
        {"parent_asin": "a", "text": "Good shampoo", "rating": 5},
        {"parent_asin": "a", "text": "Good shampoo", "rating": 1},
        {"parent_asin": "b", "text": "Two products together", "rating": 4},
        {"parent_asin": "c", "text": "Unknown item", "rating": 3},
        {"parent_asin": "d", "text": "No catalog entry", "rating": 2},
        {"parent_asin": "a", "text": "", "rating": 1},
        {"parent_asin": "a", "text": "Bad rating", "rating": 0},
    ]
    metadata = [
        {"parent_asin": "a", "title": "Test shampoo", "categories": [], "main_category": "All Beauty"},
        {"parent_asin": "b", "title": "Shampoo and conditioner", "categories": [], "main_category": "All Beauty"},
        {"parent_asin": "c", "title": "Unknown item", "categories": [], "main_category": "All Beauty"},
    ]
    review_path, metadata_path = tmp_path / "reviews.parquet", tmp_path / "metadata.parquet"
    pq.write_table(pa.Table.from_pylist(reviews), review_path)
    pq.write_table(pa.Table.from_pylist(metadata), metadata_path)
    rules = tmp_path / "rules.json"
    rules.write_text(json.dumps({"version": "test", "policy": "exploratory", "rules": RULES}))
    report = map_categories(review_path, metadata_path, rules, tmp_path / "out")
    assert report["review_products"] == 4 and report["valid_unique_reviews"] == 4
    assert report["joined_products"] == 3 and report["metadata_nonempty_subcategories"] == 0
    groups = {s["category_id"]: s for s in report["categories"]}
    assert set(groups) == {"shampoo", "ambiguous", "unclassified", "missing_metadata"}
    assert groups["shampoo"]["rating_counts"].get(1) == 1
    assert groups["shampoo"]["rating_counts"].get(5, 0) == 0
    assert all(not group["screening_candidate"] for group in groups.values())
    assert sum(g["reviews"] for g in groups.values()) == 4
