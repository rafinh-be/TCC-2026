import json, os, lancedb, configparser, frontmatter

from pathlib import Path
from dotenv import load_dotenv
from lancedb.pydantic import LanceModel, Vector
from lancedb.embeddings import get_registry
from huggingface_hub import login

load_dotenv() 
huggingface_token = os.getenv("HUGGINGFACE_TOKEN")

login(token=huggingface_token)

NOTES_DIR = config.get("database", "NOTES_DIR")
MEMORY_FILE = config.get("database", "MEMORY_FILE")
DB_PATH = config.get("database", "DB_PATH")

embedding_model = None

def needs_indexing() -> bool:
    path_dir = Path(NOTES_DIR)
    if not path_dir.exists():
        path_dir.mkdir(exist_ok=True)
        return False

    estado_atual = {}
    for arquivo_md in path_dir.glob("*.md"):
        estado_atual[arquivo_md.name] = os.path.getmtime(arquivo_md)

    if not estado_atual:
        return False

    if not os.path.exists(MEMORY_FILE):
        return True

    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            memoria_salva = json.load(f)
    except Exception:
        return True 


    if len(estado_atual) != len(memoria_salva):
        return True

    for nome_arq, mtime_atual in estado_atual.items():
        if nome_arq not in memoria_salva:
            return True  
        if mtime_atual > memoria_salva[nome_arq]:
            return True 

    return False

def update_memory():
    path_dir = Path(NOTES_DIR)
    estado_atual = {}
    for arquivo_md in path_dir.glob("*.md"):
        estado_atual[arquivo_md.name] = os.path.getmtime(arquivo_md)
        
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(estado_atual, f, indent=4)

def conectar_banco():
    Path(DB_PATH).mkdir(exist_ok=True)
    return lancedb.connect(DB_PATH)
        
def index_data():
    db = conectar_banco()
    path_dir = Path(NOTES_DIR)
    path_dir.mkdir(exist_ok=True)
    
    registry = get_registry()
    global embedding_model
    if (not embedding_model):    
        embedding_model = registry.get("sentence-transformers").create(
            name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", 
            device="cpu"
        )

    class DocumentoOBGYN(LanceModel):
        text: str = embedding_model.SourceField()
        vector: Vector(embedding_model.ndims()) = embedding_model.VectorField()
        nome_arquivo: str
        tags: list[str]  
    
    chunks_to_save = []
    
    for arquivo_md in path_dir.glob("*.md"):
        post = frontmatter.load(arquivo_md)
        
        tags = post.get("tags", [])
        conteudo_limpo = post.content
        
        paragrafos = [p.strip() for p in conteudo_limpo.split("\n\n") if p.strip()]
        
        for para in paragrafos:
            chunks_to_save.append({
                "text": para,
                "nome_arquivo": post.get("titulo", arquivo_md.stem),  
                "tags": tags
            })
            print(para, tags)
        
    if not chunks_to_save:
        print("⚠️ Nenhum arquivo ou parágrafo encontrado para indexar.")
        return

    table = db.create_table("notas_medicas", schema=DocumentoOBGYN, mode="overwrite")
    table.add(chunks_to_save)
    
    table.create_fts_index("text", replace=True)
    
    update_memory()
    
    

def _tokenize_query(pergunta: str) -> list[float]:
    registry = get_registry()
    global embedding_model
    if (not embedding_model):    
        embedding_model = registry.get("sentence-transformers").create(
            name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", 
            device="cpu"
        )
    
    return embedding_model.compute_query_embeddings(pergunta)[0]


def retrieve_context(pergunta: str) -> tuple[str, set[str]]:
    db = conectar_banco()

    if "notas_medicas" not in db.table_names():
        return "", set()

    table = db.open_table("notas_medicas")

    vetor_query = _tokenize_query(pergunta)

    SCORE_MINIMO = 0.02

    resultados = (
        table.search(query_type="hybrid")
        .vector(vetor_query)
        .text(pergunta)
        .metric("l2")
        .limit(10)
        .to_list()
    )

    blocos_validos = []
    fontes_validas = set()

    for res in resultados:
        score = res.get("_relevance_score", 0.0)
        
        if score < SCORE_MINIMO:
            continue

        nome_documento = res.get("nome_arquivo", "Documento Sem Título")

        blocos_validos.append(res["text"])
        if (nome_documento not in fontes_validas):
            fontes_validas.add(nome_documento)
        
    if not blocos_validos:
        return None, []
        
    contexto_unificado = "\n\n---\n\n".join(blocos_validos)
    return contexto_unificado, list(fontes_validas)