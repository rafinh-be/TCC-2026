from chunking import paragraph_spans

BODY_KEYS = ("content", "paragraph_spans")


def build_document(metadata, content, stem):
    return {
        "id": metadata.get("id", stem),
        "title": metadata.get("titulo", stem),
        "tags": metadata.get("tags", []),
        "content": content,
        "paragraph_spans": paragraph_spans(content),
    }


def summarize(document):
    return {key: value for key, value in document.items() if key not in BODY_KEYS}


def sort_by_title(documents):
    return sorted(documents, key=lambda document: document["title"].casefold())


def find_by_id(documents, document_id):
    return next((document for document in documents if document["id"] == document_id), None)
