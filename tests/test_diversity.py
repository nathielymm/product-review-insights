import numpy as np
import pytest

from product_review_insights.diversity import clean_review, cosine_dispersion, deterministic_sample, entropy, stratified_sample, catalog_brand


def test_text_cleanup_does_not_turn_html_into_extra_content():
    assert clean_review('Good<br />brush &amp; soft <b>bristles</b>.') == 'Good brush & soft bristles .'


def test_sampling_is_stable_to_input_order_and_rejects_shortages():
    rows = [{"id": str(i)} for i in range(20)]
    assert deterministic_sample(rows, 5, 11, "product") == deterministic_sample(list(reversed(rows)), 5, 11, "product")
    assert len({r["id"] for r in deterministic_sample(rows, 5, 11, "product")}) == 5
    with pytest.raises(ValueError, match="Insufficient"):
        deterministic_sample(rows, 21, 11, "product")


def test_semantic_distance_distinguishes_equal_and_orthogonal_vectors():
    assert cosine_dispersion(np.array([[1., 0.], [1., 0.]])) == 0
    assert cosine_dispersion(np.array([[1., 0.], [0., 1.]])) == 1
    assert cosine_dispersion(np.array([[1., 0.]])) is None
    assert entropy(["one"] * 10) == 0
    assert entropy(["one", "two"]) > 0


def test_stratification_controls_length_and_rating_and_rejects_shortage():
    rows = [{"id": str(i), "words": 25 if i < 5 else 60, "rating": 1 if i < 5 else 5} for i in range(10)]
    selected = stratified_sample(rows, {"20_39": 2, "40_79": 3}, "length", 11, "p")
    assert sum(r["words"] == 25 for r in selected) == 2
    selected = stratified_sample(rows, {"low": 2, "high": 2}, "rating", 11, "p")
    assert sum(r["rating"] == 1 for r in selected) == 2
    with pytest.raises(ValueError, match="Insufficient"):
        stratified_sample(rows, {"80_200": 1}, "length", 11, "p")


def test_unknown_brand_labels_are_not_counted_as_manufacturers():
    assert catalog_brand("N/V") is None
    assert catalog_brand(None) is None
    assert catalog_brand(" A brand ") == "a brand"
