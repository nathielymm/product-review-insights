"""Describe product-level evidence without publishing review text or user IDs.

Run from the repository root. Private examples are written only under results/.
Counts use the same normalization/deduplication and minimum-rating rule as prepare.
"""
import argparse
import collections
import hashlib
import json
from pathlib import Path

import pyarrow.parquet as pq

from product_review_insights.data import digest_file, redact, read_corpus


def profile(source, output, top=40):
    if top < 1:
        raise ValueError("top must be positive")
    parquet = pq.ParquetFile(source)
    counts, ratings, informative = collections.Counter(), collections.defaultdict(collections.Counter), collections.Counter()
    seen = {}
    missing_product = 0
    for batch in parquet.iter_batches(columns=["parent_asin", "text", "rating"]):
        for row in batch.to_pylist():
            product = row["parent_asin"]
            text = redact(" ".join((row["text"] or "").split()))
            if not text or row["rating"] not in (1, 2, 3, 4, 5):
                continue
            if not product:
                missing_product += 1
                continue
            identity = hashlib.sha256((product + "\0" + text.casefold()).encode()).hexdigest()
            rating = int(row["rating"])
            if identity in seen:
                previous = seen[identity]
                if rating < previous:
                    ratings[product][previous] -= 1
                    if ratings[product][previous] == 0:
                        del ratings[product][previous]
                    ratings[product][rating] += 1
                    seen[identity] = rating
                continue
            seen[identity] = rating
            counts[product] += 1
            ratings[product][rating] += 1
            informative[product] += len(text.split()) >= 20
    candidates = sorted(counts, key=lambda p: (-counts[p], p))[:top]
    if not candidates:
        raise ValueError("No products with valid reviews")
    # Retain a small deterministic example sample per product and rating.
    examples = {p: {} for p in candidates}
    for batch in parquet.iter_batches(columns=["parent_asin", "text", "title", "rating"]):
        for row in batch.to_pylist():
            product = row["parent_asin"]
            if product not in examples:
                continue
            text = redact(" ".join((row["text"] or "").split()))
            if not text or row["rating"] not in (1, 2, 3, 4, 5):
                continue
            identity = hashlib.sha256((product + "\0" + text.casefold()).encode()).hexdigest()
            rating = seen[identity]
            bucket = examples[product].setdefault(rating, {})
            title = redact(" ".join((row["title"] or "").split()))
            value = {"id": identity, "rating": rating, "title": title, "text": text}
            if identity in bucket:
                if (title, text) < (bucket[identity]["title"], bucket[identity]["text"]):
                    bucket[identity] = value
            elif len(bucket) < 8 or identity < max(bucket):
                bucket[identity] = value
                if len(bucket) > 8:
                    del bucket[max(bucket)]
    from sklearn.feature_extraction.text import TfidfVectorizer
    product_documents = [" ".join(v["title"] + " " + v["text"] for b in examples[p].values() for v in b.values()) for p in candidates]
    tfidf = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), max_features=30000)
    matrix = tfidf.fit_transform(product_documents)
    terms = tfidf.get_feature_names_out()
    pilot_path = Path("data/processed/pilot/corpus.jsonl")
    pilot_counts = collections.Counter(d["product_id"] for d in read_corpus(pilot_path)) if pilot_path.exists() else {}
    summary = {"source_sha256": digest_file(source), "valid_products": len(counts),
               "valid_unique_reviews": sum(counts.values()),
               "missing_product_rows": missing_product,
               "products_ge_100_valid_unique": sum(n >= 100 for n in counts.values()),
               "products_ge_500_valid_unique": sum(n >= 500 for n in counts.values()),
               "count_definition": "valid unique normalized redacted text per parent_asin; canonical minimum rating",
               "label_warning": "Product identity/type inferred from reviews; no product catalog supplied",
               "term_warning": "TF-IDF terms describe a rating-balanced sample, not full-corpus theme prevalence",
               "products": []}
    for i, product in enumerate(candidates):
        weights = matrix[i].toarray().ravel()
        summary["products"].append({"product_id": product, "valid_unique_reviews": counts[product],
            "rating_counts": dict(sorted(ratings[product].items())),
            "reviews_ge_20_words": informative[product], "existing_pilot_reviews": pilot_counts.get(product, 0),
            "sample_tfidf_terms": terms[weights.argsort()[::-1][:18]].tolist()})
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    (output / "summary.json").write_text(json.dumps(summary, indent=2))
    (output / "examples.private.json").write_text(json.dumps({p: [v for b in examples[p].values() for _, v in sorted(b.items())] for p in candidates}, indent=2))
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source")
    parser.add_argument("--output", default="results/product-profile")
    parser.add_argument("--top", type=int, default=40)
    args = parser.parse_args()
    summary = profile(args.source, args.output, args.top)
    print(json.dumps({k: v for k, v in summary.items() if k != "products"}, indent=2))
