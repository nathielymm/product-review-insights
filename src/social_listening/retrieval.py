"""Exact cosine search and diversity across clusters in a fixed candidate pool."""
import json
import time
from pathlib import Path

from .data import digest_file, read_corpus


def select_hits(ranked, clusters, k, thematic=False):
    if k < 1:
        raise ValueError("k must be positive")
    ranked = list(dict.fromkeys(int(i) for i in ranked if i >= 0))
    if not thematic:
        return ranked[:k]
    selected, used = [], set()
    for i in ranked:
        if int(clusters[i]) not in used:
            selected.append(i)
            used.add(int(clusters[i]))
            if len(selected) == k:
                return selected
    return (selected + [i for i in ranked if i not in selected])[:k]


def build(corpus_path, output, config):
    import faiss
    import numpy as np
    from sklearn.cluster import MiniBatchKMeans
    from sentence_transformers import SentenceTransformer
    started = time.perf_counter()
    documents = read_corpus(corpus_path)
    if len(documents) < config["clusters"] or config["clusters"] < 2:
        raise ValueError("Need 2 <= clusters <= document count")
    model = SentenceTransformer(config["embedding_model"], device="cpu")
    # Chunk long reviews at model token limits so evidence is never silently truncated.
    chunks = []
    tokenizer = model.tokenizer
    limit = model.max_seq_length - tokenizer.num_special_tokens_to_add(pair=False)
    for d in documents:
        tokens = tokenizer.encode(d["title"] + "\n" + d["text"], add_special_tokens=False,
                                  truncation=False, verbose=False)
        for start in range(0, len(tokens), limit):
            chunks.append({**d, "id": f"{d['id']}:{start // limit}", "review_id": d["id"],
                           "text": tokenizer.decode(tokens[start:start + limit], skip_special_tokens=True)})
    vectors = model.encode([d["text"] for d in chunks], normalize_embeddings=True,
                           convert_to_numpy=True, show_progress_bar=True).astype("float32")
    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)
    labels = MiniBatchKMeans(n_clusters=config["clusters"], random_state=config["seed"],
                            n_init=10, batch_size=1024).fit_predict(vectors)
    from sklearn.feature_extraction.text import TfidfVectorizer
    tfidf = TfidfVectorizer(stop_words="english", min_df=2, max_features=10000)
    features = tfidf.fit_transform([d["text"] for d in chunks])
    vocabulary = tfidf.get_feature_names_out()
    topics = []
    for cluster in range(config["clusters"]):
        members = np.flatnonzero(labels == cluster)
        weights = np.asarray(features[members].mean(axis=0)).ravel()
        terms = vocabulary[np.argsort(weights)[::-1][:10]].tolist()
        center = vectors[members].mean(axis=0)
        representatives = members[np.argsort(vectors[members] @ center)[::-1][:3]]
        topics.append({"cluster": cluster, "size": len(members), "top_terms": terms,
                       "representative_ids": [chunks[i]["id"] for i in representatives],
                       "interpretation": "Unsupervised vocabulary; requires human theme validation"})
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(output / "index.faiss"))
    np.save(output / "clusters.npy", labels)
    np.save(output / "embeddings.npy", vectors)
    (output / "chunks.jsonl").write_text("".join(json.dumps(d) + "\n" for d in chunks))
    (output / "topics.json").write_text(json.dumps(topics, indent=2))
    # Save exact encoder snapshot for offline queries and reproducibility.
    model.save(str(output / "encoder"))
    metadata = {"config": config, "corpus_sha256": digest_file(corpus_path),
                "chunks": len(chunks), "dimension": vectors.shape[1],
                "build_seconds": time.perf_counter() - started,
                "index_sha256": digest_file(output / "index.faiss"),
                "chunks_sha256": digest_file(output / "chunks.jsonl"),
                "encoder_files_sha256": {str(p.relative_to(output / "encoder")): digest_file(p)
                    for p in sorted((output / "encoder").rglob("*")) if p.is_file()},
                "encoder_commit": getattr(model[0].auto_model.config, "_commit_hash", None),
                "cluster_counts": np.bincount(labels).tolist()}
    (output / "metadata.json").write_text(json.dumps(metadata, indent=2))
    return metadata


class Retriever:
    def __init__(self, path):
        import faiss
        import numpy as np
        from sentence_transformers import SentenceTransformer
        self.path = Path(path)
        self.metadata = json.loads((self.path / "metadata.json").read_text())
        self.config = self.metadata["config"]
        self.documents = read_corpus(self.path / "chunks.jsonl")
        self.index = faiss.read_index(str(self.path / "index.faiss"))
        self.clusters = np.load(self.path / "clusters.npy", allow_pickle=False)
        if self.index.ntotal != len(self.documents) or len(self.clusters) != len(self.documents):
            raise ValueError("Index, documents and clusters are inconsistent")
        self.model = SentenceTransformer(str(self.path / "encoder"), device="cpu", local_files_only=True)

    def search(self, question, thematic=False):
        vector = self.model.encode([question], normalize_embeddings=True).astype("float32")
        scores, indices = self.index.search(vector, min(self.config["candidate_pool"], self.index.ntotal))
        chosen = select_hits(indices[0], self.clusters, self.config["top_k"], thematic)
        score_map = dict(zip(indices[0].tolist(), scores[0].tolist()))
        return [{**self.documents[i], "cluster": int(self.clusters[i]), "score": score_map[i]} for i in chosen]
