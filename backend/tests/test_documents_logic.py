import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from documents_logic import build_document, summarize, sort_by_title, find_by_id


def test_build_document_reads_frontmatter_fields():
    metadata = {"id": "pre_eclampsia", "titulo": "Pré-eclâmpsia", "tags": ["alto_risco"]}
    assert build_document(metadata, "corpo", "arquivo") == {
        "id": "pre_eclampsia",
        "title": "Pré-eclâmpsia",
        "tags": ["alto_risco"],
        "content": "corpo",
    }


def test_build_document_falls_back_to_file_stem():
    assert build_document({}, "corpo", "arquivo") == {"id": "arquivo", "title": "arquivo", "tags": [], "content": "corpo"}


def test_summarize_drops_content():
    document = build_document({"id": "a", "titulo": "A"}, "corpo", "a")
    assert summarize(document) == {"id": "a", "title": "A", "tags": []}


def test_sort_by_title_ignores_case():
    documents = [{"title": "banana"}, {"title": "Abacate"}, {"title": "cereja"}]
    assert [document["title"] for document in sort_by_title(documents)] == ["Abacate", "banana", "cereja"]


def test_find_by_id_returns_match_or_none():
    documents = [{"id": "a"}, {"id": "b"}]
    assert find_by_id(documents, "b") == {"id": "b"}
    assert find_by_id(documents, "c") is None
