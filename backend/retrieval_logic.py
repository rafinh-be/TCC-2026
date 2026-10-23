def select_chunks(results, min_score):
    return [res for res in results if res.get("_relevance_score", 0.0) >= min_score]


def format_chunk(nome_arquivo, text, label):
    if label:
        return f"Documento: {nome_arquivo}\n{text}"
    return text
