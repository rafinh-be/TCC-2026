import argparse, configparser, json
from pathlib import Path

import frontmatter
import numpy as np

import google_embeddings
import local_embeddings
from chunking import chunk_text
from deck_data_logic import cosine_top_k, fit_pca, locate_chunks, normalize_points, project_pca, separation_ratio
from documents_logic import build_document, sort_by_title

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

NOTES_DIR = config.get("database", "NOTES_DIR")
CHUNK_SIZE = config.getint("database", "CHUNK_SIZE")
CHUNK_OVERLAP = config.getint("database", "CHUNK_OVERLAP")
NEIGHBOR_COUNT = 5

QUESTIONS = [
    ("q1", "Quais são os sinais de alerta da pré-eclâmpsia?"),
    ("q2", "Estou sentindo dor, o que pode ser?"),
    ("q3", "Como é feito o diagnóstico de diabetes gestacional?"),
    ("q4", "Qual a dose de ibuprofeno para uma gestante de 30 semanas?"),
    ("q5", "Minha pressão tá alta, é perigoso?"),
    ("q6", "Posso tomar café durante a gravidez?"),
    ("q7", "Perdi um pouco de sangue no começo da gravidez, o que fazer?"),
    ("q8", "Como funciona a visita ao bebê no hospital?"),
]

MODELS = [
    ("minilm", "MiniLM (local)", local_embeddings),
    ("gemini", "Gemini Embedding", google_embeddings),
]

parser = argparse.ArgumentParser("export_deck_data")
parser.add_argument("--output_dir", default="../frontend/src/app/components/deck/data", help="Directory that receives chunks.json and embeddings.json")


def load_documents():
    documents = []
    for markdown_file in Path(NOTES_DIR).glob("*.md"):
        post = frontmatter.load(markdown_file)
        documents.append(build_document(post.metadata, post.content, markdown_file.stem))
    return sort_by_title(documents)


def chunk_document(document):
    paragraph_chunks = chunk_text(document["content"], "paragraph", CHUNK_SIZE, CHUNK_OVERLAP)
    window_chunks = chunk_text(document["content"], "window", CHUNK_SIZE, CHUNK_OVERLAP)
    return {
        "paragraph_chunks": paragraph_chunks,
        "spans": {
            "paragraph": locate_chunks(document["content"], paragraph_chunks),
            "window": locate_chunks(document["content"], window_chunks),
        },
    }


def embedded_chunk_records(documents, chunked):
    records = []
    for document, chunks in zip(documents, chunked):
        for index, text in enumerate(chunks["paragraph_chunks"]):
            records.append({"id": f"{document['id']}:{index}", "documentId": document["id"], "title": document["title"], "text": text})
    return records


def model_entry(model_id, label, module, records):
    model = module.create_embedding_model()
    chunk_vectors = np.array([list(vector) for vector in model.compute_source_embeddings([record["text"] for record in records])])
    question_vectors = np.array([list(model.compute_query_embeddings(text)[0]) for _, text in QUESTIONS])
    mean, components = fit_pca(chunk_vectors)
    chunk_points = project_pca(chunk_vectors, mean, components)
    question_points = project_pca(question_vectors, mean, components)
    normalized = normalize_points(np.vstack([chunk_points, question_points]))
    print(model_id, "dimensions", chunk_vectors.shape[1], "separation ratio", round(separation_ratio(normalized[:len(records)], [record["documentId"] for record in records]), 2))
    return {
        "id": model_id,
        "label": label,
        "dimensions": int(chunk_vectors.shape[1]),
        "points": np.round(normalized[:len(records)], 4).tolist(),
        "questionPoints": np.round(normalized[len(records):], 4).tolist(),
        "neighbors": [
            [{"chunkIndex": index, "score": round(score, 4)} for index, score in cosine_top_k(vector, chunk_vectors, NEIGHBOR_COUNT)]
            for vector in question_vectors
        ],
    }


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


def main():
    args = parser.parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    documents = load_documents()
    chunked = [chunk_document(document) for document in documents]
    records = embedded_chunk_records(documents, chunked)

    write_json(output_dir / "chunks.json", {
        "settings": {"size": CHUNK_SIZE, "overlap": CHUNK_OVERLAP},
        "documents": [
            {"id": document["id"], "title": document["title"], "content": document["content"], "spans": chunks["spans"]}
            for document, chunks in zip(documents, chunked)
        ],
    })
    write_json(output_dir / "embeddings.json", {
        "chunks": records,
        "questions": [{"id": question_id, "text": text} for question_id, text in QUESTIONS],
        "models": [model_entry(model_id, label, module, records) for model_id, label, module in MODELS],
    })
    print("chunks", len(records), "written to", output_dir)


if __name__ == "__main__":
    main()
