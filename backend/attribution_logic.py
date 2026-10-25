import math, re

CITATION_PATTERN = re.compile(r"[ \t]*\[(\d+(?:\s*,\s*\d+)*)\]")
SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?])\s+|\n+")
MARKDOWN_PREFIX = re.compile(r"^[\s>#*\-\d.)]+")
MIN_SENTENCE_LENGTH = 15


def split_sentences(text):
    sentences = []
    for piece in SENTENCE_BOUNDARY.split(text):
        cleaned = MARKDOWN_PREFIX.sub("", piece).replace("*", "").strip()
        if len(cleaned) >= MIN_SENTENCE_LENGTH:
            sentences.append(cleaned)
    return sentences


def cosine(first, second):
    dot = sum(a * b for a, b in zip(first, second))
    norm = math.sqrt(sum(a * a for a in first)) * math.sqrt(sum(b * b for b in second))
    return dot / norm if norm else 0.0


def similar_chunks(sentence_vectors, chunks, threshold):
    return [
        chunk for chunk in chunks
        if any(cosine(sentence, chunk["vector"]) >= threshold for sentence in sentence_vectors)
    ]


def extract_citations(answer, chunk_count):
    cited = set()
    for match in CITATION_PATTERN.finditer(answer):
        for number in match.group(1).split(","):
            index = int(number)
            if 1 <= index <= chunk_count:
                cited.add(index - 1)
    return CITATION_PATTERN.sub("", answer), cited


def keep_valid_citations(answer, chunk_count):
    def keep(match):
        numbers = [int(number) for number in match.group(1).split(",")]
        valid = [number for number in numbers if 1 <= number <= chunk_count]
        return f" [{', '.join(str(number) for number in valid)}]" if valid else ""
    return CITATION_PATTERN.sub(keep, answer)


def strip_citations(text):
    return CITATION_PATTERN.sub("", text)


def build_citations(chunks, cited_indexes, paragraph_chunks):
    citations = []
    for index in sorted(cited_indexes):
        document_id, _, chunk_index = chunks[index]["chunk_id"].rpartition(":")
        citations.append({
            "number": index + 1,
            "doc_id": document_id,
            "title": chunks[index]["title"],
            "chunk_index": int(chunk_index) if paragraph_chunks else None,
        })
    return citations


def cited_chunks(chunks, cited_indexes):
    return [chunk for index, chunk in enumerate(chunks) if index in cited_indexes]


def intersect_chunks(first, second):
    second_ids = {chunk["chunk_id"] for chunk in second}
    return [chunk for chunk in first if chunk["chunk_id"] in second_ids]
