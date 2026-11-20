import argparse

from product_review_insights.diversity import analyze

parser = argparse.ArgumentParser(description="Explore equally sized cohort candidates using local data and encoder")
parser.add_argument("--config", default="configs/diversity-candidates.draft.json")
parser.add_argument("--output", default="results/diversity-exploration")
parser.add_argument("--reuse-pools", action="store_true")
args = parser.parse_args()
report = analyze(args.config, args.output, reuse_pools=args.reuse_pools)
for c in report["candidates"]:
    print(c["id"], c["status"], c.get("measurements", {}).get("mean_pairwise_cosine_distance"))
