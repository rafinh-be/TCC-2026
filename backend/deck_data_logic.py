import numpy as np

from chunking import PARAGRAPH_SEPARATOR


def locate_chunks(content, chunks):
    spans = []
    cursor = 0
    for chunk in chunks:
        pieces = chunk.split(PARAGRAPH_SEPARATOR)
        start = content.find(pieces[0], cursor)
        if start == -1:
            raise ValueError(f"chunk not found in content: {chunk[:40]!r}")
        last_piece_start = content.find(pieces[-1], start)
        spans.append([start, last_piece_start + len(pieces[-1])])
        cursor = start + 1
    return spans


def cosine_top_k(query_vector, vectors, k):
    matrix = np.asarray(vectors, dtype=float)
    query = np.asarray(query_vector, dtype=float)
    scores = matrix @ query / (np.linalg.norm(matrix, axis=1) * np.linalg.norm(query))
    order = np.argsort(-scores)[:k]
    return [(int(index), float(scores[index])) for index in order]


def fit_pca(vectors):
    matrix = np.asarray(vectors, dtype=float)
    mean = matrix.mean(axis=0)
    _, _, components = np.linalg.svd(matrix - mean, full_matrices=False)
    return mean, components[:2]


def project_pca(vectors, mean, components):
    return (np.asarray(vectors, dtype=float) - mean) @ components.T


def normalize_points(points, margin=0.05):
    array = np.asarray(points, dtype=float)
    low = array.min(axis=0)
    span = array.max(axis=0) - low
    span[span == 0] = 1
    return margin + (array - low) / span * (1 - 2 * margin)


def separation_ratio(points, labels):
    array = np.asarray(points, dtype=float)
    distances = np.linalg.norm(array[:, None, :] - array[None, :, :], axis=2)
    label_array = np.asarray(labels)
    same_label = label_array[:, None] == label_array[None, :]
    upper = np.triu(np.ones_like(same_label, dtype=bool), k=1)
    return float(distances[upper & ~same_label].mean() / distances[upper & same_label].mean())
