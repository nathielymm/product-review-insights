"""Explore cohort heterogeneity without generating or evaluating RAG answers."""
import collections
import hashlib
import html
import itertools
import inspect
import importlib.metadata
import json
import math
import re
from pathlib import Path

from .data import digest_file, redact


def clean_review(text):
    return " ".join(re.sub(r"<[^>]*>", " ", html.unescape(text)).split())


def word_count(text):
    return len(re.findall(r"\b[\w'-]+\b", text))


def entropy(values):
    counts = collections.Counter(values)
    n = sum(counts.values())
    return -sum((v / n) * math.log(v / n) for v in counts.values()) if n else 0.0


def catalog_brand(value):
    label = str(value or "").strip().casefold()
    return label if label not in {"", "unknown", "n/v", "n/a", "unbranded", "generic", "no brand"} else None


def deterministic_sample(rows, n, seed, product_id):
    if len(rows) < n:
        raise ValueError(f"Insufficient eligible reviews for {product_id}: {len(rows)} < {n}")
    return sorted(rows, key=lambda r: hashlib.sha256(f"{seed}:{product_id}:{r['id']}".encode()).hexdigest())[:n]


def stratified_sample(rows, quotas, field, seed, product_id):
    selected = []
    for bucket, n in quotas.items():
        if field == "length":
            subset = [r for r in rows if ("20_39" if r["words"] < 40 else "40_79" if r["words"] < 80 else "80_200") == bucket]
        elif field == "rating":
            subset = [r for r in rows if ("low" if r["rating"] <= 2 else "middle" if r["rating"] == 3 else "high") == bucket]
        else:
            raise ValueError("Unknown stratification field")
        selected.extend(deterministic_sample(subset, n, seed, product_id))
    return selected


def sample_measurements(chosen, embeddings, position, partitions, seed):
    import numpy as np
    selected = [r for rows in chosen.values() for r in rows]
    indices = [position[r["id"]] for r in selected]
    centers = np.array([embeddings[[position[r["id"]] for r in rows]].mean(axis=0) for rows in chosen.values()])
    centers /= np.linalg.norm(centers, axis=1, keepdims=True)
    row = {"seed": seed, "sample_size": len(selected),
           "mean_pairwise_cosine_distance": cosine_dispersion(embeddings[indices]),
           "between_product_centroid_distance": cosine_dispersion(centers),
           "within_product_distance": float(np.mean([cosine_dispersion(embeddings[[position[r["id"]] for r in rows]]) for rows in chosen.values()])),
           "mean_words": float(np.mean([r["words"] for r in selected])),
           "median_words": float(np.median([r["words"] for r in selected])),
           "embedding_truncated_share": sum(r.get("embedding_truncated", False) for r in selected) / len(selected),
           "low_rating_share": sum(r["rating"] <= 2 for r in selected) / len(selected),
           "middle_rating_share": sum(r["rating"] == 3 for r in selected) / len(selected),
           "high_rating_share": sum(r["rating"] >= 4 for r in selected) / len(selected)}
    for k, labels in partitions.items():
        row[f"semantic_cluster_entropy_k{k}"] = entropy(labels[indices].tolist()) / math.log(k)
    return row


def prepare_pools(source, config, output):
    import pyarrow.parquet as pq
    from langdetect import DetectorFactory, detect_langs
    from langdetect.lang_detect_exception import LangDetectException
    DetectorFactory.seed = config["language_detector_seed"]
    wanted = {p for c in config["candidates"] for p in c["product_ids"]}
    records = {}
    for batch in pq.ParquetFile(source).iter_batches(columns=["parent_asin", "text", "rating"]):
        for row in batch.to_pylist():
            pid = row["parent_asin"]
            if pid not in wanted or row["rating"] not in (1, 2, 3, 4, 5):
                continue
            raw = redact(" ".join((row["text"] or "").split()))
            if not raw:
                continue
            identity = hashlib.sha256((pid + "\0" + raw.casefold()).encode()).hexdigest()
            if identity in records:
                records[identity]["rating"] = min(records[identity]["rating"], int(row["rating"]))
                records[identity]["text"] = min(records[identity]["text"], raw)
            else:
                records[identity] = {"id": identity, "product_id": pid, "text": raw, "rating": int(row["rating"])}
    pools = {p: [] for p in sorted(wanted)}
    profiles = {p: {"valid_unique_reviews": 0, "word_range_reviews": 0,
                    "language_top_labels": collections.Counter(), "eligible_reviews": 0,
                    "eligible_ratings": collections.Counter(), "eligible_length_bins": collections.Counter()} for p in sorted(wanted)}
    for i, record in enumerate(sorted(records.values(), key=lambda r: r["id"])):
        pid = record["product_id"]
        profiles[pid]["valid_unique_reviews"] += 1
        record["text"] = clean_review(record["text"])
        words = word_count(record["text"])
        if not config["min_words"] <= words <= config["max_words"]:
            continue
        profiles[pid]["word_range_reviews"] += 1
        try:
            languages = detect_langs(record["text"])
        except LangDetectException:
            languages = []
        label = languages[0].lang if languages else "undetected"
        confidence = languages[0].prob if languages else 0.0
        profiles[pid]["language_top_labels"][label] += 1
        if label != "en" or confidence < config["english_probability_threshold"]:
            continue
        record.update({"words": words, "language": label, "language_score": confidence})
        pools[pid].append(record)
        profiles[pid]["eligible_reviews"] += 1
        profiles[pid]["eligible_ratings"][record["rating"]] += 1
        profiles[pid]["eligible_length_bins"]["20_39" if words < 40 else "40_79" if words < 80 else "80_200"] += 1
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    (output / "pools.private.json").write_text(json.dumps(pools, ensure_ascii=False))
    (output / "product-profiles.json").write_text(json.dumps(profiles, indent=2))
    return pools, profiles


def cosine_dispersion(vectors):
    import numpy as np
    if len(vectors) < 2:
        return None
    similarity = np.clip(vectors @ vectors.T, -1, 1)
    indices = np.triu_indices(len(vectors), k=1)
    return float((1 - similarity[indices]).mean())


def summarize_measurements(rows):
    import statistics
    keys = [k for k, v in rows[0].items() if isinstance(v, (int, float)) and k != "seed"]
    return {key: {"mean": statistics.mean(row[key] for row in rows),
                  "min": min(row[key] for row in rows), "max": max(row[key] for row in rows)} for key in keys}


def analyze(config_path, output, source="data/raw/all_beauty.supplied.parquet", reuse_pools=False):
    import numpy as np
    from sentence_transformers import SentenceTransformer
    from sklearn.cluster import MiniBatchKMeans
    config = json.loads(Path(config_path).read_text())
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    expected = {"source_sha256": digest_file(source), "config_sha256": digest_file(config_path)}
    filter_settings = {k: config[k] for k in ["min_words", "max_words", "english_probability_threshold", "language_detector_seed"]}
    filter_settings["product_ids"] = sorted({p for c in config["candidates"] for p in c["product_ids"]})
    filter_settings["langdetect_version"] = importlib.metadata.version("langdetect")
    filter_settings["preprocessing_source"] = "\n".join(inspect.getsource(f) for f in [clean_review, word_count, prepare_pools])
    expected_pool = {"source_sha256": expected["source_sha256"],
                     "filter_settings_sha256": hashlib.sha256(json.dumps(filter_settings, sort_keys=True).encode()).hexdigest()}
    cache_manifest = output / "pool-manifest.json"
    cached = json.loads(cache_manifest.read_text()) if cache_manifest.exists() else {}
    reusable = (reuse_pools and all(cached.get(k) == v for k, v in expected_pool.items())
                and (output / "pools.private.json").exists() and (output / "product-profiles.json").exists()
                and cached.get("pools_sha256") == digest_file(output / "pools.private.json")
                and cached.get("profiles_sha256") == digest_file(output / "product-profiles.json"))
    if reusable:
        pools = json.loads((output / "pools.private.json").read_text())
        profiles = json.loads((output / "product-profiles.json").read_text())
    else:
        pools, profiles = prepare_pools(source, config, output)
        cache_manifest.write_text(json.dumps({**expected_pool,
            "pools_sha256": digest_file(output / "pools.private.json"),
            "profiles_sha256": digest_file(output / "product-profiles.json")}, indent=2))
    print("Language audit complete; loading local encoder", flush=True)
    model = SentenceTransformer(config["encoder_path"], device="cpu", local_files_only=True)
    records = sorted([r for rows in pools.values() for r in rows], key=lambda r: r["id"])
    inputs, truncated = [], 0
    for record in records:
        tokens = model.tokenizer.encode(record["text"], add_special_tokens=False, truncation=False, verbose=False)
        record["embedding_truncated"] = len(tokens) > config["embedding_max_tokens"]
        truncated += len(tokens) > config["embedding_max_tokens"]
        inputs.append(model.tokenizer.decode(tokens[:config["embedding_max_tokens"]], skip_special_tokens=True))
    embeddings = model.encode(inputs, normalize_embeddings=True, convert_to_numpy=True,
                              show_progress_bar=True).astype("float32")
    np.save(output / "embeddings.private.npy", embeddings)
    position = {r["id"]: i for i, r in enumerate(records)}
    # Shared exploratory partitions, trained on an equal number of reviews per product.
    training = []
    n = config["reviews_per_product"]
    for pid, rows in sorted(pools.items()):
        training += [position[r["id"]] for r in deterministic_sample(rows, min(n, len(rows)), 997, pid)]
    partitions = {}
    for k in config["cluster_counts"]:
        estimator = MiniBatchKMeans(n_clusters=k, random_state=42, n_init=10, batch_size=256)
        estimator.fit(embeddings[training])
        partitions[k] = estimator.predict(embeddings)
    candidates = []
    measurements = {}
    sampled_ids = {}
    catalog_attributes = {}
    import pyarrow.parquet as pq
    metadata_path = Path("data/raw/meta_all_beauty.parquet")
    for batch in pq.ParquetFile(metadata_path).iter_batches(columns=["parent_asin", "details"]):
        for record in batch.to_pylist():
            if record["parent_asin"] in pools:
                try:
                    details = json.loads(record["details"] or "{}")
                except (json.JSONDecodeError, TypeError):
                    details = {}
                catalog_attributes[record["parent_asin"]] = details
    for cohort in config["candidates"]:
        pids = cohort["product_ids"]
        if len(set(pids)) != len(pids):
            raise ValueError("Duplicate product in a candidate")
        capacities = {p: len(pools[p]) for p in pids}
        descriptors = [config["product_descriptors"][p] for p in pids]
        item = {**cohort, "status": "eligible_for_exploratory_comparison" if min(capacities.values()) >= n else "insufficient_pool",
                "eligible_pool_reviews": sum(capacities.values()), "minimum_product_pool": min(capacities.values()),
                "products": len(pids), "reviews_per_sample": n * len(pids),
                "unique_domains": len({d["domain"] for d in descriptors}),
                "unique_functions": len({d["function"] for d in descriptors}),
                "unique_coded_formats": len({d["format"] for d in descriptors}),
                "unknown_coded_formats": sum("unconfirmed" in d["format"] for d in descriptors),
                "distinct_provisional_families": len({d["family"] for d in descriptors})}
        brands = [catalog_brand(catalog_attributes.get(p, {}).get("Brand")) for p in pids]
        item["known_catalog_brands"] = len({b for b in brands if b})
        item["products_missing_brand_attribute"] = sum(not b for b in brands)
        values = []
        if item["status"] != "insufficient_pool":
            for seed in config["seeds"]:
                chosen = {p: deterministic_sample(pools[p], n, seed, p) for p in pids}
                row = sample_measurements(chosen, embeddings, position, partitions, seed)
                values.append(row)
                sampled_ids[f"{cohort['id']}:{seed}"] = [r["id"] for rows in chosen.values() for r in rows]
            item["measurements"] = summarize_measurements(values)
            item["sensitivity"] = {}
            for mode, spec in config.get("sensitivity_sampling", {}).items():
                rows = []
                for seed in config["seeds"]:
                    chosen = {p: stratified_sample(pools[p], spec["quotas"], spec["field"], seed, p) for p in pids}
                    rows.append(sample_measurements(chosen, embeddings, position, partitions, seed))
                    sampled_ids[f"{cohort['id']}:{mode}:{seed}"] = [r["id"] for batch in chosen.values() for r in batch]
                item["sensitivity"][mode] = {"sampling": spec, "measurements": summarize_measurements(rows), "by_seed": rows}
        measurements[cohort["id"]] = values
        candidates.append(item)
    overlaps = [{"a": a["id"], "b": b["id"], "shared_products": len(set(a["product_ids"]) & set(b["product_ids"]))}
                for a, b in itertools.combinations(config["candidates"], 2)]
    report = {"status": "exploratory_not_rag_evaluation_not_frozen", **expected, "config": config,
              "analysis_code_sha256": digest_file(__file__),
              "langdetect_version": importlib.metadata.version("langdetect"),
              "requirements_sha256": digest_file("requirements.lock.txt"),
              "product_profiles": profiles, "candidate_overlap": overlaps, "candidates": candidates,
              "encoded_reviews": len(records), "reviews_truncated_for_embedding": truncated,
              "pool_sha256": digest_file(output / "pools.private.json"),
              "metadata_source_sha256": digest_file(metadata_path),
              "encoder_files_sha256": {str(p.relative_to(config["encoder_path"])): digest_file(p)
                   for p in sorted(Path(config["encoder_path"]).rglob("*")) if p.is_file()},
              "measurements_by_seed": measurements,
              "warning": "Cosine dispersion and cluster entropy are proxies, not validated thematic diversity. Seed ranges are not confidence intervals. Language scores are detector scores, not calibrated probabilities."}
    (output / "sampled-ids.private.json").write_text(json.dumps(sampled_ids))
    (output / "diversity-summary.json").write_text(json.dumps(report, indent=2, ensure_ascii=False))
    return report
