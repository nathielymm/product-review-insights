"""Reproducible local comparison of traditional and thematic RAG."""
import os

# Avoid native OpenMP conflicts observed between Torch/FAISS on this macOS runtime.
# Callers can override deliberately; keep the values in experiment metadata.
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
