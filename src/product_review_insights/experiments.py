"""Paired runs and blinded human evaluation; unannotated scores stay missing."""
import csv
import hashlib
import json
import platform
import os
import random
import statistics
import threading
import time
from pathlib import Path

from .data import digest_file
from .generation import api, generate, SYSTEM
from .retrieval import Retriever


def run(index_path, questions_path, destination, repetitions=3, cohort=None):
    import psutil
    if repetitions < 1:
        raise ValueError("repetitions must be positive")
    questions = json.loads(Path(questions_path).read_text())
    ids = [q["id"] for q in questions]
    if not questions or len(set(ids)) != len(ids):
        raise ValueError("Need nonempty questions with unique IDs")
    from .study import validate_index_scope
    index_metadata = json.loads((Path(index_path) / "metadata.json").read_text())
    study_scope = validate_index_scope(index_metadata, cohort, any(q.get("scope_required", False) for q in questions))
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=False)
    retriever = Retriever(index_path)
    config = retriever.config
    info = api("/api/show", {"model": config["ollama_model"]})
    tags = api("/api/tags")
    metadata = {"config": config, "index_metadata": retriever.metadata,
                "study": study_scope,
                "questions_sha256": digest_file(questions_path), "repetitions": repetitions,
                "platform": platform.platform(), "python": platform.python_version(),
                "thread_environment": {k: os.environ.get(k) for k in ["OMP_NUM_THREADS", "TOKENIZERS_PARALLELISM"]},
                "requirements_sha256": digest_file("requirements.lock.txt") if Path("requirements.lock.txt").exists() else None,
                "source_files_sha256": {p.name: digest_file(p) for p in sorted(Path(__file__).parent.glob("*.py"))},
                "system_prompt": SYSTEM,
                "status": "running", "questions": ids,
                "ollama_version": api("/api/version"), "model_info": info, "tags": tags,
                "memory_note": "RSS sampled every 50ms; Python and accessible Ollama/llama-server processes; not GPU memory",
                "timing_note": "One warmup excluded; query encoding included in retrieval; ingestion/index separate"}
    (destination / "metadata.json").write_text(json.dumps(metadata, indent=2))
    rng, rows = random.Random(config["seed"]), []
    tasks = [(q, repeat) for q in questions for repeat in range(repetitions)]
    rng.shuffle(tasks)
    stop, observations = threading.Event(), []

    def sample_memory():
        while not stop.is_set():
            python_rss = psutil.Process().memory_info().rss
            ollama_rss = 0
            for p in psutil.process_iter(["name", "memory_info"]):
                try:
                    if any(name in (p.info["name"] or "").lower() for name in ["ollama", "llama-server"]):
                        ollama_rss += p.info["memory_info"].rss
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            observations.append((python_rss, ollama_rss))
            stop.wait(0.05)

    monitor = threading.Thread(target=sample_memory, daemon=True)
    monitor.start()
    try:
        retriever.search("consumer review quality")
        generate("Reply briefly with ready.", [{"id": "warmup", "text": "System ready."}], config)
        with (destination / "runs.jsonl").open("w") as stream:
            for question, repeat in tasks:
                methods = ["traditional", "thematic"]
                rng.shuffle(methods)
                for method in methods:
                    begin, cpu = time.perf_counter(), time.process_time()
                    sample_start = len(observations)
                    hits = retriever.search(question["question"], method == "thematic")
                    retrieval_seconds = time.perf_counter() - begin
                    result = generate(question["question"], hits, config)
                    recent = observations[sample_start:]
                    row = {"question_id": question["id"], "question": question["question"],
                           "study": study_scope,
                           "method": method, "repeat": repeat, **result,
                           "retrieval_seconds": retrieval_seconds,
                           "generation_seconds": time.perf_counter() - begin - retrieval_seconds,
                           "total_seconds": time.perf_counter() - begin,
                           "python_cpu_seconds": time.process_time() - cpu,
                           "python_peak_rss_bytes": max((x[0] for x in recent), default=None),
                           "ollama_peak_rss_bytes": max((x[1] for x in recent), default=None)}
                    stream.write(json.dumps(row) + "\n")
                    stream.flush()
                    rows.append(row)
    finally:
        stop.set()
        monitor.join()
        metadata["completed_runs"] = len(rows)
        metadata["expected_runs"] = len(questions) * repetitions * 2
        metadata["status"] = "complete" if len(rows) == metadata["expected_runs"] else "incomplete"
        (destination / "metadata.json").write_text(json.dumps(metadata, indent=2))
    return {"runs": len(rows), "destination": str(destination)}


def blind(run_path, destination, seed=42):
    rows = [json.loads(line) for line in Path(run_path).read_text().splitlines()]
    random.Random(seed).shuffle(rows)
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=False)
    key, blind_rows = {}, []
    for i, row in enumerate(rows):
        identifier = f"A{i + 1:04d}"
        key[identifier] = {k: row[k] for k in ["question_id", "method", "repeat"]}
        blind_rows.append({"annotation_id": identifier, "question_id": row["question_id"],
                           "question": row["question"], "answer": row["answer"],
                           "evidence": [{"id": h["id"], "citation_id": h.get("citation_id", h["id"]),
                                         "text": h["text"], **({"product_id": h["product_id"]} if "product_id" in h else {}),
                                         **({"functional_class": h["functional_class"]} if "functional_class" in h else {})} for h in row["evidence"]]})
    (destination / "blind.json").write_text(json.dumps(blind_rows, indent=2))
    (destination / "key.private.json").write_text(json.dumps(key, indent=2))
    with (destination / "annotations.csv").open("w") as stream:
        fields = ["annotation_id", "reference_theme_count", "covered_reference_themes",
                  "factual_claims", "supported_claims", "contradicted_claims", "notes"]
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows({"annotation_id": r["annotation_id"]} for r in blind_rows)


def human_metrics(row):
    fields = ["reference_theme_count", "covered_reference_themes", "factual_claims",
              "supported_claims", "contradicted_claims"]
    if any(row.get(k) in (None, "") for k in fields):
        return {"coverage": None, "faithfulness": None, "contradiction_rate": None}
    values = {k: int(row[k]) for k in fields}
    if any(v < 0 for v in values.values()):
        raise ValueError("Annotation counts cannot be negative")
    if values["covered_reference_themes"] > values["reference_theme_count"]:
        raise ValueError("Covered themes exceed reference themes")
    if values["supported_claims"] + values["contradicted_claims"] > values["factual_claims"]:
        raise ValueError("Claim categories exceed total factual claims")
    return {"coverage": values["covered_reference_themes"] / values["reference_theme_count"] if values["reference_theme_count"] else None,
            "faithfulness": values["supported_claims"] / values["factual_claims"] if values["factual_claims"] else None,
            "contradiction_rate": values["contradicted_claims"] / values["factual_claims"] if values["factual_claims"] else None}


def summarize(run_path):
    rows = [json.loads(line) for line in Path(run_path).read_text().splitlines()]
    result = {}
    for method in ["traditional", "thematic"]:
        group = [r for r in rows if r["method"] == method]
        if not group:
            continue
        values = sorted(r["total_seconds"] for r in group)
        result[method] = {"n": len(group), "total_seconds_median": statistics.median(values),
                          "total_seconds_p95": values[max(0, __import__('math').ceil(0.95 * len(values)) - 1)],
                          "human_coverage": None, "human_faithfulness": None}
    return result


def paired_bootstrap(pairs, seed=42, iterations=2000):
    """Resample questions, not repeated runs (avoid pseudoreplication)."""
    if not pairs:
        return None
    deltas = [statistics.mean(values) for values in pairs.values()]
    rng = random.Random(seed)
    bootstrap = sorted(statistics.mean(rng.choices(deltas, k=len(deltas))) for _ in range(iterations))
    return {"questions": len(deltas), "mean_delta_thematic_minus_traditional": statistics.mean(deltas),
            "ci95": [bootstrap[int(.025 * iterations)], bootstrap[min(iterations - 1, int(.975 * iterations))]],
            "resampling_unit": "question", "iterations": iterations, "seed": seed}


def evaluate(run_path, annotations_path, key_path):
    runs = [json.loads(line) for line in Path(run_path).read_text().splitlines()]
    key = json.loads(Path(key_path).read_text())
    known = {(r["question_id"], r["method"], r["repeat"]) for r in runs}
    if len(known) != len(runs):
        raise ValueError("Duplicate run identities")
    ratings = {}
    with open(annotations_path) as stream:
        for row in csv.DictReader(stream):
            if row["annotation_id"] not in key:
                raise ValueError("Unknown annotation ID")
            item = key[row["annotation_id"]]
            identity = (item["question_id"], item["method"], item["repeat"])
            if identity not in known or identity in ratings:
                raise ValueError("Unknown or duplicate run annotation")
            ratings[identity] = human_metrics(row)
    report = {"latency": summarize(run_path), "annotated_runs": sum(v["faithfulness"] is not None for v in ratings.values()),
              "total_runs": len(runs), "paired_comparisons": {}}
    for metric in ["total_seconds", "retrieval_seconds", "generation_seconds", "coverage", "faithfulness", "contradiction_rate"]:
        by_pair = {}
        for row in runs:
            identity = (row["question_id"], row["method"], row["repeat"])
            value = row.get(metric) if metric.endswith("seconds") else ratings.get(identity, {}).get(metric)
            if value is not None:
                by_pair.setdefault((row["question_id"], row["repeat"]), {})[row["method"]] = value
        pairs = {}
        for (question, repeat), values in by_pair.items():
            if {"traditional", "thematic"} <= values.keys():
                pairs.setdefault(question, []).append(values["thematic"] - values["traditional"])
        report["paired_comparisons"][metric] = paired_bootstrap(pairs)
    return report
