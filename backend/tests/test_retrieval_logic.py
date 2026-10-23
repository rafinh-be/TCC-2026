import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from retrieval_logic import select_chunks, format_chunk


def test_keeps_equal_and_above_and_drops_below():
    results = [
        {"text": "a", "_relevance_score": 0.02},
        {"text": "b", "_relevance_score": 0.015},
        {"text": "c", "_relevance_score": 0.014},
    ]
    assert [r["text"] for r in select_chunks(results, 0.015)] == ["a", "b"]


def test_zero_keeps_everything():
    results = [{"text": "a", "_relevance_score": 0.0}, {"text": "b"}]
    assert select_chunks(results, 0) == results


def test_preserves_order():
    results = [
        {"text": "a", "_relevance_score": 0.016},
        {"text": "b", "_relevance_score": 0.03},
        {"text": "c", "_relevance_score": 0.02},
    ]
    assert [r["text"] for r in select_chunks(results, 0.015)] == ["a", "b", "c"]


def test_missing_score_is_treated_as_zero():
    results = [{"text": "a"}]
    assert select_chunks(results, 0.015) == []
    assert select_chunks(results, 0) == results


def test_format_chunk_with_label():
    assert format_chunk("Pré-natal", "texto", True) == "Documento: Pré-natal\ntexto"


def test_format_chunk_without_label():
    assert format_chunk("Pré-natal", "texto", False) == "texto"
