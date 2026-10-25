import pytest

from chunking import chunk_text, paragraph_spans, split_paragraphs, split_window


def old_paragraph_split(text):
    return [p.strip() for p in text.split("\n\n") if p.strip()]


def test_paragraph_matches_previous_behavior():
    text = "  um\n\n\n\ndois linhas\ncontinua\n\n   \n\ntres  "
    assert split_paragraphs(text) == old_paragraph_split(text)
    assert chunk_text(text, "paragraph", 500, 100) == old_paragraph_split(text)


def test_window_packs_whole_paragraphs():
    text = "aaaa bbbb\n\ncccc dddd\n\neeee ffff"
    chunks = split_window(text, 25, 5)
    assert chunks == ["aaaa bbbb\n\ncccc dddd", "eeee ffff"]


def test_window_single_paragraph_fits():
    assert split_window("curto", 50, 10) == ["curto"]


def test_oversized_paragraph_overlaps_and_cuts_on_whitespace():
    words = [f"palavra{i}" for i in range(60)]
    text = " ".join(words)
    chunks = split_window(text, 80, 30)
    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk) <= 80
        assert all(word in words for word in chunk.split())
    for previous, current in zip(chunks, chunks[1:]):
        assert set(previous.split()) & set(current.split())
    assert set(" ".join(chunks).split()) == set(words)


def test_oversized_paragraph_flushes_pending_chunk_first():
    long_paragraph = " ".join(["xx"] * 100)
    text = "inicio\n\n" + long_paragraph
    chunks = split_window(text, 50, 10)
    assert chunks[0] == "inicio"
    assert all(len(chunk) <= 50 for chunk in chunks)


def test_no_empty_chunks():
    text = "\n\n  \n\na b\n\n\n\n" + " ".join(["w"] * 200) + "\n\n   "
    for strategy in ("paragraph", "window"):
        assert all(chunk.strip() for chunk in chunk_text(text, strategy, 40, 10))


def test_empty_text_returns_empty_list():
    assert split_window("", 50, 10) == []
    assert split_window("  \n\n ", 50, 10) == []
    assert split_paragraphs("") == []


@pytest.mark.parametrize("size,overlap", [(10, 10), (10, 11)])
def test_overlap_not_smaller_than_size_raises(size, overlap):
    with pytest.raises(ValueError):
        split_window("texto qualquer", size, overlap)


def test_unbreakable_word_is_kept_whole():
    text = "a " + "x" * 100 + " b"
    chunks = split_window(text, 20, 5)
    assert "x" * 100 in chunks
    assert all(len(chunk) <= 20 or chunk == "x" * 100 for chunk in chunks)


def test_unknown_strategy_raises():
    with pytest.raises(ValueError):
        chunk_text("texto", "desconhecida", 50, 10)


def test_paragraph_spans_locate_each_paragraph_in_the_text():
    text = "  um\n\n\n\ndois linhas\ncontinua\n\n   \n\ntres  "
    spans = paragraph_spans(text)
    assert [text[start:end] for start, end in spans] == split_paragraphs(text)


def test_paragraph_spans_of_empty_text():
    assert paragraph_spans("") == []
