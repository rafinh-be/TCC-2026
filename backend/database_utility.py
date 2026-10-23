import json, os, lancedb, configparser, frontmatter, contextlib

os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"

from pathlib import Path
from dotenv import load_dotenv
from lancedb.pydantic import LanceModel, Vector
import providers
from retrieval_logic import select_chunks, format_chunk
from huggingface_hub import login
from chunking import chunk_text
from text_cleaning import clean_latex_math

#load_dotenv() 
#huggingface_token = os.getenv("HUGGINGFACE_TOKEN")

#login(token=huggingface_token)

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

NOTES_DIR = config.get("database", "NOTES_DIR")
MEMORY_FILE = config.get("database", "MEMORY_FILE")
DB_PATH = config.get("database", "DB_PATH")
CHUNK_SIZE = config.getint("database", "CHUNK_SIZE")
CHUNK_OVERLAP = config.getint("database", "CHUNK_OVERLAP")
LEGACY_CHUNKING = {"strategy": "paragraph", "clean_latex": False}

embedding_model = None
registry = None

def load_embedding_model():
    global embedding_model
    embedding_model = providers.create_embedding_model()

def chunking_signature(chunking="paragraph", clean_latex=False):
    return {
        "strategy": chunking,
        "size": CHUNK_SIZE,
        "overlap": CHUNK_OVERLAP,
        "clean_latex": clean_latex,
    }

def comparable_chunking(signature):
    if signature["strategy"] == "paragraph":
        return {"strategy": "paragraph", "clean_latex": signature["clean_latex"]}
    return signature

def needs_indexing(verbose=False, chunking="paragraph", clean_latex=False) -> bool:
    path_dir = Path(NOTES_DIR)
    if not path_dir.exists():
        path_dir.mkdir(exist_ok=True)
        return False

    estado_atual = {}
    for arquivo_md in path_dir.glob("*.md"):
        estado_atual[arquivo_md.name] = os.path.getmtime(arquivo_md)

    if not estado_atual:
        return False

    db = conectar_banco()
    if "notas_medicas" in db.table_names() and "chunk_id" not in db.open_table("notas_medicas").schema.names:
        return True

    if not os.path.exists(MEMORY_FILE):
        return True

    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            memoria_salva = json.load(f)
    except Exception:
        return True 

    if (memoria_salva.get("embedding") != providers.embedding_signature()):
        if (verbose):
            print("Embedding provider changed since last sync")
        return True
    chunking_salvo = memoria_salva.get("chunking", LEGACY_CHUNKING)
    if comparable_chunking(chunking_salvo) != comparable_chunking(chunking_signature(chunking, clean_latex)):
        if (verbose):
            print("Chunking options changed since last sync")
        return True
    if not (Path(DB_PATH) / "notas_medicas.lance").exists():
        return True
    memoria_salva = memoria_salva.get("files", {})

    if len(estado_atual) != len(memoria_salva):
        return True

    for nome_arq, mtime_atual in estado_atual.items():
        if nome_arq not in memoria_salva:
            if (verbose):
                print("Found new file for database")
            return True  
        if mtime_atual > memoria_salva[nome_arq]:
            if (verbose):
                print("Found file that has been edited since last sync")
            return True 

    return False

def update_memory(chunking="paragraph", clean_latex=False):
    path_dir = Path(NOTES_DIR)
    estado_atual = {}
    for arquivo_md in path_dir.glob("*.md"):
        estado_atual[arquivo_md.name] = os.path.getmtime(arquivo_md)
        
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump({"embedding": providers.embedding_signature(), "chunking": chunking_signature(chunking, clean_latex), "files": estado_atual}, f, indent=4)

def conectar_banco():
    Path(DB_PATH).mkdir(exist_ok=True)
    return lancedb.connect(DB_PATH)
        
def index_data(verbose=False, chunking="paragraph", clean_latex=False):
    db = conectar_banco()
    path_dir = Path(NOTES_DIR)
    path_dir.mkdir(exist_ok=True)
    
    global embedding_model
    global registry
    if (not embedding_model):
        load_embedding_model()

    class DocumentoOBGYN(LanceModel):
        text: str = embedding_model.SourceField()
        vector: Vector(embedding_model.ndims()) = embedding_model.VectorField()
        nome_arquivo: str
        chunk_id: str
        tags: list[str]  
    
    chunks_to_save = []
    
    for arquivo_md in path_dir.glob("*.md"):
        post = frontmatter.load(arquivo_md)
        
        tags = post.get("tags", [])
        conteudo_limpo = clean_latex_math(post.content) if clean_latex else post.content
        
        # paragrafos = [conteudo_limpo]
        paragrafos = chunk_text(conteudo_limpo, chunking, CHUNK_SIZE, CHUNK_OVERLAP)
        
        if (verbose):
            print("Indexing:", post.get("titulo", arquivo_md.stem))
        
        for indice, para in enumerate(paragrafos):
            chunks_to_save.append({
                "text": para,
                "nome_arquivo": post.get("titulo", arquivo_md.stem),  
                "chunk_id": f"{post.get('id', arquivo_md.stem)}:{indice}",
                "tags": tags
            })
            if (verbose):
                print(para, tags)
        
    if not chunks_to_save:
        print("⚠️ Nenhum arquivo ou parágrafo encontrado para indexar.")
        return

    table = db.create_table("notas_medicas", schema=DocumentoOBGYN, mode="overwrite")
    table.add(chunks_to_save)
    
    table.create_fts_index("text", replace=True)
    
    update_memory(chunking, clean_latex)
    
def _tokenize_query(pergunta: str) -> list[float]:
    global embedding_model
    global registry
    if (not embedding_model):
        load_embedding_model()
    
    return embedding_model.compute_query_embeddings(pergunta)[0]

def _to_chunk(res: dict) -> dict:
    return {
        "chunk_id": res["chunk_id"],
        "title": res.get("nome_arquivo", "Documento Sem Título"),
        "text": res["text"],
    }

def retrieve_context(pergunta: str, debug_rag=False, min_score=None) -> list[dict]:
    if min_score is None:
        min_score = config.getfloat("retrieval", "MIN_SCORE", fallback=0.015)

    db = conectar_banco()

    if "notas_medicas" not in db.table_names():
        return []

    table = db.open_table("notas_medicas")
    vetor_query = _tokenize_query(pergunta)

    resultados = (
        table.search(query_type="hybrid")
        .vector(vetor_query)
        .text(pergunta)
        .metric("l2")
        .limit(10)
        .to_list()
    )

    chunks = []
    for res in select_chunks(resultados, min_score):
        score = res.get("_relevance_score", 0.0)

        if (debug_rag):
            print("Found this document with score of", score, "and title:", res.get("nome_arquivo", "Documento Sem Título"))

        chunks.append(_to_chunk(res))

    return chunks

def fetch_chunks(chunk_ids: list[str]) -> list[dict]:
    if not chunk_ids:
        return []

    db = conectar_banco()
    if "notas_medicas" not in db.table_names():
        return []

    table = db.open_table("notas_medicas")
    ids_escapados = ", ".join("'" + chunk_id.replace("'", "''") + "'" for chunk_id in chunk_ids)
    resultados = table.search().where(f"chunk_id IN ({ids_escapados})").limit(len(chunk_ids)).to_list()

    return [_to_chunk(res) for res in resultados]

def merge_chunks(*chunk_lists: list[dict]) -> list[dict]:
    vistos = {}
    for chunks in chunk_lists:
        for chunk in chunks:
            vistos.setdefault(chunk["chunk_id"], chunk)
    return list(vistos.values())

def format_context(chunks: list[dict], label_chunks=False) -> str:
    return "\n\n---\n\n".join(format_chunk(chunk["title"], chunk["text"], label_chunks) for chunk in chunks)
