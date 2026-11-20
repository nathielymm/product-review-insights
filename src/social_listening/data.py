"""Local-only ingestion; no raw text or user identifiers in audit reports."""
import hashlib
import heapq
import json
import re
from pathlib import Path


def digest_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def redact(text):
    text = re.sub(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", "[EMAIL]", text)
    text = re.sub(r"https?://\S+", "[URL]", text)
    return re.sub(r"(?<!\w)(?:\+?\d[\d ()-]{8,}\d)(?!\w)", "[NUMBER]", text)


def prepare(source, destination, size=10000, seed=42):
    import pyarrow.parquet as pq
    if size < 1:
        raise ValueError("sample size must be positive")
    source, destination = Path(source), Path(destination)
    parquet = pq.ParquetFile(source)
    required = {"text", "title", "rating", "parent_asin"}
    if not required <= set(parquet.schema_arrow.names):
        raise ValueError(f"Missing fields: {sorted(required - set(parquet.schema_arrow.names))}")
    # Hash priorities yield an order-independent sample without retaining all text.
    seen, heap = set(), []
    counts = {"rows": 0, "empty_text": 0, "invalid_rating": 0, "duplicates": 0}
    ratings = {}
    for batch in parquet.iter_batches(batch_size=8192, columns=sorted(required)):
        for row in batch.to_pylist():
            counts["rows"] += 1
            text = " ".join((row["text"] or "").split())
            if not text:
                counts["empty_text"] += 1
                continue
            if row["rating"] not in (1, 2, 3, 4, 5):
                counts["invalid_rating"] += 1
                continue
            text = redact(text)
            title = redact(" ".join((row["title"] or "").split()))
            # Collapse identical texts within a product; keep cross-product evidence.
            identity = hashlib.sha256((str(row["parent_asin"]) + "\0" + text.casefold()).encode()).hexdigest()
            if identity in seen:
                counts["duplicates"] += 1
                continue
            seen.add(identity)
            rating = int(row["rating"])
            ratings[str(rating)] = ratings.get(str(rating), 0) + 1
            document = {"id": identity, "text": text, "title": title,
                        "product_id": row["parent_asin"], "rating": rating}
            priority = int(hashlib.sha256(f"{seed}:{identity}".encode()).hexdigest(), 16)
            item = (-priority, identity, document)
            if len(heap) < size:
                heapq.heappush(heap, item)
            elif item[:2] > heap[0][:2]:
                heapq.heapreplace(heap, item)
    documents = [item[2] for item in sorted(heap, key=lambda x: (-x[0], x[1]))]
    destination.mkdir(parents=True, exist_ok=True)
    corpus = destination / "corpus.jsonl"
    corpus.write_text("".join(json.dumps(d, ensure_ascii=False) + "\n" for d in documents))
    manifest = {"source_sha256": digest_file(source), "source_bytes": source.stat().st_size,
                "schema": str(parquet.schema_arrow), **counts, "unique_valid": len(seen),
                "valid_unique_rating_counts": ratings, "sample_size": len(documents), "seed": seed,
                "corpus_sha256": digest_file(corpus), "sampling": "sha256 priority, product+normalized redacted text dedup",
                "category": "All_Beauty claimed by supplied context; provenance not independently verified",
                "pii": "user IDs/images omitted; email/URL/phone heuristics applied; manual review still required"}
    (destination / "manifest.json").write_text(json.dumps(manifest, indent=2))
    return manifest


def read_corpus(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]
