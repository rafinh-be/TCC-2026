PARAGRAPH_SEPARATOR = "\n\n"
WHITESPACE_CHARACTERS = (" ", "\n", "\t")


def split_paragraphs(text):
    if not text:
        return []
    return [paragraph.strip() for paragraph in text.split(PARAGRAPH_SEPARATOR) if paragraph.strip()]


def _next_word_start(text, position):
    while position < len(text) and not text[position - 1].isspace():
        position += 1
    while position < len(text) and text[position].isspace():
        position += 1
    return position


def _cut_position(text, start, size):
    limit = start + size
    if limit >= len(text):
        return len(text)
    if text[limit].isspace():
        return limit
    cut = max(text.rfind(character, start, limit) for character in WHITESPACE_CHARACTERS)
    if cut > start:
        return cut
    following = [index for index in (text.find(character, limit) for character in WHITESPACE_CHARACTERS) if index != -1]
    return min(following) if following else len(text)


def _split_long_paragraph(paragraph, size, overlap):
    chunks = []
    start = 0
    while start < len(paragraph):
        end = _cut_position(paragraph, start, size)
        chunk = paragraph[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(paragraph):
            break
        next_start = end - overlap
        if next_start <= start:
            next_start = end
        start = _next_word_start(paragraph, next_start)
    return chunks


def split_window(text, size, overlap):
    if overlap >= size:
        raise ValueError("overlap must be smaller than size")
    chunks = []
    current = ""
    for paragraph in split_paragraphs(text):
        if len(paragraph) > size:
            if current:
                chunks.append(current)
                current = ""
            chunks.extend(_split_long_paragraph(paragraph, size, overlap))
            continue
        candidate = f"{current}{PARAGRAPH_SEPARATOR}{paragraph}" if current else paragraph
        if len(candidate) <= size:
            current = candidate
        else:
            chunks.append(current)
            current = paragraph
    if current:
        chunks.append(current)
    return chunks


def chunk_text(text, strategy, size, overlap):
    if strategy == "paragraph":
        return split_paragraphs(text)
    if strategy == "window":
        return split_window(text, size, overlap)
    raise ValueError(f"unknown chunking strategy: {strategy}")
