import faiss
import numpy as np
import pytest

from product_review_insights.retrieval import select_hits


def test_diversity_preserves_similarity_order_within_each_theme():
    vectors = np.array([[1, 0], [.99, .01], [.8, .6], [0, 1]], dtype="float32")
    faiss.normalize_L2(vectors)
    index = faiss.IndexFlatIP(2)
    index.add(vectors)
    _, ranked = index.search(np.array([[1, 0]], dtype="float32"), 4)
    clusters = [0, 0, 1, 2]
    assert select_hits(ranked[0], clusters, 3) == [0, 1, 2]
    assert select_hits(ranked[0], clusters, 3, True) == [0, 2, 3]


def test_sparse_themes_fill_without_duplicates_or_invalid_faiss_indices():
    assert select_hits([0, 0, 1, -1], [0, 0], 4, True) == [0, 1]
    with pytest.raises(ValueError):
        select_hits([0], [0], 0)
