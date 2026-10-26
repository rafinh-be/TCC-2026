import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np

from chunking import paragraph_spans, split_paragraphs, split_window
from deck_data_logic import cosine_top_k, fit_pca, locate_chunks, normalize_points, project_pca, separation_ratio


def test_locate_chunks_matches_paragraph_spans():
    content = "primeiro\n\nsegundo trecho\n\n\n\nterceiro"
    chunks = split_paragraphs(content)
    assert locate_chunks(content, chunks) == paragraph_spans(content)


def test_locate_chunks_handles_packed_chunks_with_irregular_separators():
    content = "aaaa bbbb\n\n\n\ncccc dddd\n\neeee ffff"
    chunks = split_window(content, 30, 5)
    spans = locate_chunks(content, chunks)
    assert content[spans[0][0]:spans[0][1]].startswith("aaaa bbbb")
    assert content[spans[0][0]:spans[0][1]].endswith("cccc dddd")
    assert content[spans[-1][0]:spans[-1][1]] == "eeee ffff"


def test_locate_chunks_follows_overlapping_chunks_in_order():
    content = " ".join(f"palavra{i}" for i in range(60))
    chunks = split_window(content, 80, 30)
    spans = locate_chunks(content, chunks)
    starts = [start for start, _ in spans]
    assert starts == sorted(starts)
    assert spans[1][0] < spans[0][1]


def test_cosine_top_k_orders_by_similarity():
    vectors = [[1.0, 0.0], [0.0, 1.0], [0.9, 0.1]]
    ranked = cosine_top_k([1.0, 0.0], vectors, 2)
    assert [index for index, _ in ranked] == [0, 2]
    assert ranked[0][1] > ranked[1][1]


def test_cosine_top_k_ignores_vector_scale():
    ranked = cosine_top_k([2.0, 0.0], [[10.0, 0.0], [0.0, 1.0]], 1)
    assert ranked[0][0] == 0
    assert abs(ranked[0][1] - 1.0) < 1e-9


def test_pca_projects_to_two_columns_with_ordered_variance():
    rng = np.random.default_rng(0)
    vectors = rng.normal(size=(40, 6)) * np.array([5, 2, 1, 1, 1, 1])
    mean, components = fit_pca(vectors)
    projected = project_pca(vectors, mean, components)
    assert projected.shape == (40, 2)
    assert projected[:, 0].var() >= projected[:, 1].var()


def test_normalize_points_fits_inside_margins():
    points = np.array([[-3.0, 10.0], [5.0, 20.0], [1.0, 15.0]])
    normalized = normalize_points(points, margin=0.1)
    assert normalized.min() >= 0.1 - 1e-9
    assert normalized.max() <= 0.9 + 1e-9


def test_separation_ratio_is_high_for_distinct_clusters():
    points = [[0, 0], [0.1, 0], [10, 10], [10.1, 10]]
    assert separation_ratio(points, ["a", "a", "b", "b"]) > 10
    assert separation_ratio(points, ["a", "b", "a", "b"]) < 2
