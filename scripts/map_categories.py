"""Run catalog-title classification; all raw/derived catalog data stays local."""
import argparse
import json

from product_review_insights.catalog import map_categories

parser = argparse.ArgumentParser()
parser.add_argument("--reviews", default="data/raw/all_beauty.supplied.parquet")
parser.add_argument("--metadata", default="data/raw/meta_all_beauty.parquet")
parser.add_argument("--rules", default="configs/category-rules.json")
parser.add_argument("--output", default="results/category-map")
args = parser.parse_args()
report = map_categories(args.reviews, args.metadata, args.rules, args.output)
print(json.dumps({k: v for k, v in report.items() if k != "categories"}, ensure_ascii=False, indent=2))
