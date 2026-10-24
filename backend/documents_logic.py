def build_document(metadata, content, stem):
    return {
        "id": metadata.get("id", stem),
        "title": metadata.get("titulo", stem),
        "tags": metadata.get("tags", []),
        "content": content,
    }


def summarize(document):
    return {key: value for key, value in document.items() if key != "content"}


def sort_by_title(documents):
    return sorted(documents, key=lambda document: document["title"].casefold())


def find_by_id(documents, document_id):
    return next((document for document in documents if document["id"] == document_id), None)
