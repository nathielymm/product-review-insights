"""Paired runs and blinded human evaluation; unannotated scores stay missing."""
import csv
import hashlib
import json
import platform
import os
import random
import statistics
import time
from pathlib import Path

from .data import digest_file
from .generation import api, generate, SYSTEM, STRUCTURED_SYSTEM, pack_context, citation_check
from .retrieval import Retriever



def run(index_path, questions_path, destination, repetitions=3, cohort=None, *, expected_model_digest=None, expected_ollama_version=None, evaluation_binding=None, preserve_generation_errors=False):
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
    if destination.exists(): raise FileExistsError("Use a new run destination")
    retriever = Retriever(index_path)
    config = retriever.config
    info = api("/api/show", {"model": config["ollama_model"]})
    tags = api("/api/tags")
    if expected_model_digest:
        model = next((m for m in tags['models'] if m['name']==config['ollama_model']),None)
        if not model or model['digest']!=expected_model_digest:
            raise ValueError('Local model digest differs from frozen model')
    version=api('/api/version')
    if expected_ollama_version and version.get('version')!=expected_ollama_version:
        raise ValueError('Ollama version differs from freeze')
    destination.mkdir(parents=True, exist_ok=False)
    metadata = {"config": config, "index_metadata": retriever.metadata,
                "study": study_scope, "evaluation_binding": evaluation_binding, "expected_model_digest": expected_model_digest,
                "questions_sha256": digest_file(questions_path), "repetitions": repetitions,
                "platform": platform.platform(), "python": platform.python_version(),
                "thread_environment": {k: os.environ.get(k) for k in ["OMP_NUM_THREADS", "TOKENIZERS_PARALLELISM"]},
                "requirements_sha256": digest_file("requirements.lock.txt") if Path("requirements.lock.txt").exists() else None,
                "source_files_sha256": {p.name: digest_file(p) for p in sorted(Path(__file__).parent.glob("*.py"))},
                "system_prompt": STRUCTURED_SYSTEM if config.get("structured_output") else SYSTEM,
                "status": "running", "questions": ids,
                "ollama_version": version, "model_info": info, "tags": tags,
                "resource_policy": "Wall-clock times and Ollama token counts only. No process enumeration, RSS sampling, GPU-memory or energy measurement.",
                "timing_note": "One warmup excluded; query encoding included in retrieval; ingestion/index separate. Tokens are workload proxies, not energy or monetary cost."}
    (destination / "metadata.json").write_text(json.dumps(metadata, indent=2))
    rng, rows = random.Random(config["seed"]), []
    consecutive_generation_errors = 0
    tasks = [(q, repeat) for q in questions for repeat in range(repetitions)]
    rng.shuffle(tasks)
    try:
        retriever.search("consumer review quality")
        generate("Reply briefly with ready.", [{"id": "warmup", "text": "System ready."}], config)
        with (destination / "runs.jsonl").open("w") as stream:
            for question, repeat in tasks:
                methods = ["traditional", "thematic"]
                rng.shuffle(methods)
                for method in methods:
                    begin = time.perf_counter()
                    hits = retriever.search(question["question"], method == "thematic")
                    retrieval_seconds = time.perf_counter() - begin
                    try:
                        result = generate(question["question"], hits, config)
                        consecutive_generation_errors = 0
                    except Exception as error:
                        if not preserve_generation_errors: raise
                        _, included = pack_context(hits, config['context_chars'])
                        result = {'answer':'','raw_model_output':None,'evidence':included,'ollama':{},
                                  'citations':citation_check('',set()),
                                  'structured_validation':{'requested':bool(config.get('structured_output')),'valid':False,'error':'Generation request failed'},
                                  'generation_error':{'type':type(error).__name__,'message':str(error)}}
                        consecutive_generation_errors += 1
                    row = {"question_id": question["id"], "question": question["question"],
                           "study": study_scope, "evaluation_binding": evaluation_binding,
                           "method": method, "repeat": repeat, **result,
                           "retrieval_seconds": retrieval_seconds,
                           "generation_seconds": time.perf_counter() - begin - retrieval_seconds,
                           "total_seconds": time.perf_counter() - begin}
                    stream.write(json.dumps(row) + "\n")
                    stream.flush()
                    rows.append(row)
                    if consecutive_generation_errors >= 3:
                        raise RuntimeError('Aborting after three consecutive generation errors; attempts preserved')
    finally:
        metadata["completed_runs"] = len(rows)
        metadata["expected_runs"] = len(questions) * repetitions * 2
        metadata["status"] = "complete" if len(rows) == metadata["expected_runs"] else "incomplete"
        if expected_model_digest:
            try:
                last_tags=api('/api/tags')
                last=next((m for m in last_tags['models'] if m['name']==config['ollama_model']),None)
                if not last or last['digest']!=expected_model_digest: metadata['status']='invalid_model_digest'
            except Exception:
                metadata['status']='unverified_model_digest_at_end'
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
