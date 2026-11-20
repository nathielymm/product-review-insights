"""Prepare isolated, traceable study corpora; no model or answer evaluation."""
import collections
import hashlib
import json
import statistics
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

from .data import digest_file, read_corpus, redact
from .diversity import deterministic_sample


def ids_digest(ids):
    return hashlib.sha256(json.dumps(sorted(ids), separators=(",", ":")).encode()).hexdigest()


def validate_design(scope):
    used, counts = set(), set()
    names = set()
    for cohort in scope["cohorts"]:
        ids = [p["parent_asin"] for p in cohort["families"]]
        if not ids or len(set(ids)) != len(ids) or used.intersection(ids) or cohort["id"] in names:
            raise ValueError("Evaluation families/cohorts must be nonempty, unique and disjoint")
        used.update(ids)
        names.add(cohort["id"])
        counts.add(len(ids))
    dev = scope["development"]["parent_asins"]
    if not dev or len(set(dev)) != len(dev) or used.intersection(dev):
        raise ValueError("Development families must be unique and disjoint from evaluation")
    if len(counts) != 1:
        raise ValueError("Sensitivity comparison requires equal family counts")
    sizes = scope["sensitivity_analysis"]["reviews_per_family"]
    seeds = scope["sensitivity_analysis"]["seeds"]
    if not sizes or any(n < 1 for n in sizes) or len(set(sizes)) != len(sizes) or not seeds or len(set(seeds)) != len(seeds):
        raise ValueError("Invalid sensitivity grid")


def validate_corpus(documents, manifest, corpus_path=None):
    if corpus_path is not None and digest_file(corpus_path) != manifest["corpus_sha256"]:
        raise ValueError("Corpus checksum differs from study manifest")
    ids = [r["id"] for r in documents]
    counts = dict(sorted(collections.Counter(r["product_id"] for r in documents).items()))
    if len(set(ids)) != len(ids) or len(ids) != manifest["reviews"] or ids_digest(ids) != manifest["review_ids_sha256"]:
        raise ValueError("Review identities differ from study manifest")
    if counts != manifest["product_counts"] or set(counts) != set(manifest["allowed_parent_asins"]):
        raise ValueError("Corpus contains missing or foreign families")
    if any(not r.get("item_asins") for r in documents):
        raise ValueError("Study corpus requires item ASIN lineage")


def load_corpus_manifest(corpus_path, documents):
    path = Path(corpus_path).with_name("manifest.json")
    if not path.exists():
        return None
    manifest = json.loads(path.read_text())
    if "study" not in manifest:
        return None  # historical global pilot
    validate_corpus(documents, manifest, corpus_path)
    return manifest


def validate_index_scope(metadata, expected_cohort=None, requires_scope=False):
    study = metadata.get("study")
    if (expected_cohort or requires_scope) and not study:
        raise ValueError("Scoped questions require a study index; global pilot is not eligible")
    if requires_scope and not expected_cohort:
        raise ValueError("Scoped questions require an explicit --cohort")
    if expected_cohort and study["cohort_id"] != expected_cohort:
        raise ValueError("Requested cohort differs from index cohort")
    return study


def validate_scoped_chunks(documents, manifest):
    by_review = {}
    allowed = set(manifest["allowed_parent_asins"])
    for chunk in documents:
        pid, rid = chunk["product_id"], chunk["review_id"]
        if pid not in allowed or (rid in by_review and by_review[rid] != pid):
            raise ValueError("Index contains foreign or inconsistent families")
        by_review[rid] = pid
    if ids_digest(by_review) != manifest["review_ids_sha256"]:
        raise ValueError("Index review identities differ from study corpus")
    if dict(sorted(collections.Counter(by_review.values()).items())) != manifest["product_counts"]:
        raise ValueError("Index family counts differ from study corpus")


def materialize_corpus(rows, folder, study, common):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=False)
    rows = sorted(rows, key=lambda r: r["id"])
    path = folder / "corpus.jsonl"
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
    words = [r["words"] for r in rows]
    years = collections.Counter(datetime.fromtimestamp(t / 1000, ZoneInfo("America/Sao_Paulo")).year
                                for r in rows for t in r["timestamps_ms"])
    manifest = {"schema": "study_corpus_v1", "study": study, **common,
        "qc_status": "automated_checks_passed_manual_review_pending",
        "reviews": len(rows), "corpus_sha256": digest_file(path),
        "review_ids_sha256": ids_digest(r["id"] for r in rows),
        "allowed_parent_asins": sorted({r["product_id"] for r in rows}),
        "product_counts": dict(sorted(collections.Counter(r["product_id"] for r in rows).items())),
        "rating_counts": dict(sorted(collections.Counter(r["rating"] for r in rows).items())),
        "words": {"min": min(words), "median": statistics.median(words), "max": max(words)},
        "source_year_occurrences": dict(sorted(years.items())),
        "year_note": "Source occurrences, may include duplicate dates; timezone America/Sao_Paulo",
        "rating_conflict_reviews": sum(r["duplicate_rating_conflict"] for r in rows)}
    (folder / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    validate_corpus(rows, manifest, path)
    return manifest


def prepare_study(scope_path, source, pools_path, output):
    import pyarrow.parquet as pq
    scope_path, source, pools_path, output = map(Path, [scope_path, source, pools_path, output])
    scope = json.loads(scope_path.read_text())
    validate_design(scope)
    if output.exists():
        raise FileExistsError("Study destination exists; use a new --output to preserve snapshots")
    if digest_file(source) != scope["sources"]["reviews_sha256"] or digest_file(pools_path) != scope["sources"]["eligible_pool_sha256"]:
        raise ValueError("Source or eligible pool differs from accepted scope")
    audit_path = Path(scope["sampling"]["audit_review_exclusion_file"])
    if digest_file(audit_path) != scope["sampling"]["audit_review_exclusion_sha256"]:
        raise ValueError("Audit exclusion snapshot changed")
    excluded = {r["review_id"] for r in json.loads(audit_path.read_text())}
    pools = json.loads(pools_path.read_text())
    classes = {p["parent_asin"]: p["functional_label"] for c in scope["cohorts"] for p in c["families"]}
    classes.update(scope["development"]["functional_classes"])
    selected = {}
    per_product = {}
    for pid in classes:
        rows = [r for r in pools[pid] if r["id"] not in excluded]
        if not rows or len({r["id"] for r in rows}) != len(rows):
            raise ValueError("Empty or duplicate source family")
        per_product[pid] = rows
        for row in rows:
            if row["product_id"] != pid or row["language"] != "en" or row["language_score"] < scope["sampling"]["english_score_threshold"]:
                raise ValueError("Eligible pool violates scope criteria")
            if not scope["sampling"]["min_words"] <= row["words"] <= scope["sampling"]["max_words"]:
                raise ValueError("Eligible pool violates word limits")
            selected[row["id"]] = row
    maximum = max(scope["sensitivity_analysis"]["reviews_per_family"])
    if any(len(rows) < maximum for rows in per_product.values()):
        raise ValueError("Sensitivity grid exceeds an evaluation/development family's capacity")
    lineage = {rid: {"asins": set(), "timestamps": set(), "ratings": set(), "occurrences": 0} for rid in selected}
    for batch in pq.ParquetFile(source).iter_batches(columns=["parent_asin", "asin", "text", "rating", "timestamp"]):
        for row in batch.to_pylist():
            if row["parent_asin"] not in classes or row["rating"] not in (1, 2, 3, 4, 5):
                continue
            text = redact(" ".join((row["text"] or "").split()))
            identity = hashlib.sha256((row["parent_asin"] + "\0" + text.casefold()).encode()).hexdigest()
            if identity not in lineage:
                continue
            entry = lineage[identity]
            entry["occurrences"] += 1
            entry["ratings"].add(int(row["rating"]))
            if row["asin"]:
                entry["asins"].add(row["asin"])
            if row["timestamp"] is not None:
                entry["timestamps"].add(int(row["timestamp"]))
    documents = {}
    for rid, row in selected.items():
        trace = lineage[rid]
        if not trace["asins"] or not trace["timestamps"] or row["rating"] != min(trace["ratings"]):
            raise ValueError("Source lineage or canonical rating differs from eligible pool")
        documents[rid] = {"id": rid, "product_id": row["product_id"], "functional_class": classes[row["product_id"]],
            "title": "", "text": row["text"], "rating": row["rating"], "words": row["words"],
            "language": row["language"], "language_score": row["language_score"],
            "item_asins": sorted(trace["asins"]), "timestamps_ms": sorted(trace["timestamps"]),
            "source_occurrences": trace["occurrences"], "duplicate_rating_conflict": len(trace["ratings"]) > 1}
    common = {"scope_config_sha256": digest_file(scope_path), "source_sha256": digest_file(source),
              "eligible_pool_sha256": digest_file(pools_path), "audit_exclusion_sha256": digest_file(audit_path),
              "audited_reviews_reserved": len(excluded)}
    summary = {"status": "corpora_prepared_final_qa_and_benchmark_pending", **common, "primary": [], "sensitivity": [], "development": []}
    groups = [(c["id"], [p["parent_asin"] for p in c["families"]], "evaluation") for c in scope["cohorts"]]
    groups.append(("development_disjoint", scope["development"]["parent_asins"], "development"))
    for cid, pids, split in groups:
        all_rows = [documents[r["id"]] for p in pids for r in per_product[p]]
        study = {"scope_id": scope["scope_version"], "cohort_id": cid, "split": split,
                 "analysis_kind": "primary" if split == "evaluation" else "development_full"}
        full = materialize_corpus(all_rows, output / ("main" if split == "evaluation" else "development") / cid, study, common)
        summary["primary" if split == "evaluation" else "development"].append(full)
        for seed in scope["sensitivity_analysis"]["seeds"]:
            for n in scope["sensitivity_analysis"]["reviews_per_family"]:
                rows = [documents[r["id"]] for p in pids for r in deterministic_sample(per_product[p], n, seed, p)]
                nested = {**study, "analysis_kind": "sensitivity" if split == "evaluation" else "development_curve", "reviews_per_family": n, "seed": seed}
                section = "sensitivity" if split == "evaluation" else "development_curve"
                manifest = materialize_corpus(rows, output / section / f"n{n}" / f"seed{seed}" / cid, nested, common)
                summary["sensitivity" if split == "evaluation" else "development"].append(manifest)
    summary["primary_reviews"] = sum(m["reviews"] for m in summary["primary"])
    (output / "preparation-summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    return summary
