import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from attribution_logic import split_sentences, cosine, similar_chunks, extract_citations, cited_chunks, intersect_chunks, keep_valid_citations, strip_citations, build_citations


def chunk(chunk_id, vector=None):
    return {"chunk_id": chunk_id, "title": chunk_id, "text": chunk_id, "vector": vector or [1.0, 0.0]}


def test_split_sentences_drops_short_and_markdown_markers():
    text = "Ok.\n- A pré-eclâmpsia cursa com hipertensão. **Procure** atendimento médico imediato!"
    assert split_sentences(text) == ["A pré-eclâmpsia cursa com hipertensão.", "Procure atendimento médico imediato!"]


def test_cosine_of_identical_and_orthogonal_vectors():
    assert cosine([1.0, 0.0], [2.0, 0.0]) == 1.0
    assert cosine([1.0, 0.0], [0.0, 1.0]) == 0.0
    assert cosine([0.0, 0.0], [1.0, 0.0]) == 0.0


def test_similar_chunks_keeps_only_chunks_above_threshold():
    chunks = [chunk("a", [1.0, 0.0]), chunk("b", [0.0, 1.0])]
    assert similar_chunks([[1.0, 0.1]], chunks, 0.9) == [chunks[0]]


def test_similar_chunks_with_no_sentences_keeps_nothing():
    assert similar_chunks([], [chunk("a")], 0.1) == []


def test_extract_citations_strips_markers_and_returns_zero_based_indexes():
    clean, cited = extract_citations("Faça repouso [1]. Procure ajuda [2, 3][1].", 3)
    assert clean == "Faça repouso. Procure ajuda."
    assert cited == {0, 1, 2}


def test_extract_citations_ignores_out_of_range_numbers_but_still_strips_them():
    clean, cited = extract_citations("Texto [9] e [0] e [1].", 2)
    assert clean == "Texto e e."
    assert cited == {0}


def test_cited_chunks_preserves_order():
    chunks = [chunk("a"), chunk("b"), chunk("c")]
    assert cited_chunks(chunks, {2, 0}) == [chunks[0], chunks[2]]


def test_intersect_chunks_keeps_first_list_order():
    first = [chunk("a"), chunk("b"), chunk("c")]
    second = [chunk("c"), chunk("a")]
    assert intersect_chunks(first, second) == [first[0], first[2]]


def test_keep_valid_citations_drops_out_of_range_numbers():
    answer = "Fato um [1]. Fato dois [2, 9]. Fato inventado [7]."
    assert keep_valid_citations(answer, 3) == "Fato um [1]. Fato dois [2]. Fato inventado."


def test_strip_citations_removes_every_marker():
    assert strip_citations("Fato um [1]. Fato dois [2, 3].") == "Fato um. Fato dois."


def test_build_citations_maps_numbers_to_documents_and_paragraphs():
    chunks = [
        {"chunk_id": "pre_eclampsia:4", "title": "Pré-eclâmpsia"},
        {"chunk_id": "diabetes:0", "title": "Diabetes"},
    ]
    assert build_citations(chunks, {1, 0}, True) == [
        {"number": 1, "doc_id": "pre_eclampsia", "title": "Pré-eclâmpsia", "chunk_index": 4},
        {"number": 2, "doc_id": "diabetes", "title": "Diabetes", "chunk_index": 0},
    ]


def test_build_citations_without_paragraph_chunks_has_no_chunk_index():
    chunks = [{"chunk_id": "pre_eclampsia:4", "title": "Pré-eclâmpsia"}]
    assert build_citations(chunks, {0}, False)[0]["chunk_index"] is None
