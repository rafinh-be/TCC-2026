import json, os, lancedb, configparser, frontmatter


from pathlib import Path
from lancedb.pydantic import LanceModel, Vector
from google_embeddings import GoogleEmbeddings
from google_models import model_setting

BASE_DIR = Path(__file__).parent
config = configparser.ConfigParser()
config_path = BASE_DIR / 'config.ini'
config.read(config_path, encoding='utf-8')

NOTES_DIR = (BASE_DIR / config.get("database", "NOTES_DIR")).resolve()
MEMORY_FILE = (BASE_DIR / config.get("database", "MEMORY_FILE")).resolve()
DB_PATH = (BASE_DIR / config.get("database", "DB_PATH")).resolve()
CHUNK_SIZE = int(config.get("database", "CHUNK_SIZE", fallback="500"))
CHUNK_OVERLAP = int(config.get("database", "CHUNK_OVERLAP", fallback=str(int(CHUNK_SIZE * 0.20))))


embedding_model = None
registry = None

def clean_latex_math(text: str) -> str:
    if not text:
        return text

    import re
    text = re.sub(r'\\text\{([^}]+)\}', r'\1', text)
    text = text.replace(r'\ge', '>=').replace(r'\le', '<=').replace(r'^\circ', '°')
    text = re.sub(r'_([0-9a-zA-Z])', r'\1', text)
    text = re.sub(r'\$([^$]+)\$', r'\1', text)
    text = re.sub(r' +', ' ', text)
    return text

def split_text_into_chunks(text: str, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP) -> list[str]:

    if chunk_overlap is None:
        chunk_overlap = int(chunk_size * 0.20)
        
    if not text or not text.strip():
        return []
    
    text = text.strip()
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    step = chunk_size - chunk_overlap
    if step <= 0:
        step = 1

    start = 0
    text_length = len(text)

    while start < text_length:
        if start > 0 and start < text_length and not text[start - 1].isspace():
            space_before = max(text.rfind('\n', 0, start), text.rfind(' ', 0, start))
            if space_before != -1 and (start - space_before) < (chunk_overlap // 2):
                start = space_before + 1

        end = min(start + chunk_size, text_length)

        if end < text_length:
            last_space = max(text.rfind('\n', start, end), text.rfind(' ', start, end))
            if last_space > start + int(chunk_size * 0.5):
                end = last_space

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end == text_length:
            break

        start = start + step

    return chunks


def load_embedding_model():
    global embedding_model
    embedding_model = GoogleEmbeddings.create(
        name=model_setting("embedding_model"),
        dimensions=int(model_setting("embedding_dimensions")),
    )


def embedding_signature():
    return {
        "provider": "google-gemini",
        "model": model_setting("embedding_model"),
        "dimensions": int(model_setting("embedding_dimensions")),
    }


def needs_indexing(verbose=False) -> bool:
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

    if memoria_salva.get("embedding") != embedding_signature():
        return True
    if not (DB_PATH / "notas_medicas.lance").exists():
        return True
    memoria_salva = memoria_salva.get("files", {})

    if len(estado_atual) != len(memoria_salva):
        return True

    for nome_arq, mtime_atual in estado_atual.items():
        if nome_arq not in memoria_salva:
            if (verbose):
                print("Arquivo novo encontrado para a base de dados.")
            return True  
        if mtime_atual > memoria_salva[nome_arq]:
            if (verbose):
                print("Arquivo modificado desde a última sincronização.")
            return True 

    return False

def update_memory():
    path_dir = Path(NOTES_DIR)
    estado_atual = {}
    for arquivo_md in path_dir.glob("*.md"):
        estado_atual[arquivo_md.name] = os.path.getmtime(arquivo_md)
        
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump({"embedding": embedding_signature(), "files": estado_atual}, f, indent=4)

def conectar_banco():
    Path(DB_PATH).mkdir(exist_ok=True)
    return lancedb.connect(DB_PATH)
        
def index_data(verbose=False):
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
        tags: list[str]  
    
    chunks_to_save = []
    
    for arquivo_md in path_dir.glob("*.md"):
        post = frontmatter.load(arquivo_md)
        
        tags = post.get("tags", [])
        conteudo_limpo = clean_latex_math(post.content)

        
        chunks = split_text_into_chunks(conteudo_limpo, CHUNK_SIZE, CHUNK_OVERLAP)
        
        if (verbose):
            print("Indexando:", post.get("titulo", arquivo_md.stem))
        
        for chunk in chunks:
            chunks_to_save.append({
                "text": chunk,
                "nome_arquivo": post.get("titulo", arquivo_md.stem),  
                "tags": tags
            })
            if (verbose):
                print(chunk, tags)

        
    if not chunks_to_save:
        print("⚠️ Nenhum arquivo ou parágrafo encontrado para indexar.")
        return

    table = db.create_table("notas_medicas", schema=DocumentoOBGYN, mode="overwrite")
    table.add(chunks_to_save)
    
    table.create_fts_index("text", replace=True)
    
    update_memory()
    
def _tokenize_query(pergunta: str) -> list[float]:
    global embedding_model
    global registry
    if (not embedding_model):
        load_embedding_model()
    
    return embedding_model.compute_query_embeddings(pergunta)[0]

def retrieve_context(pergunta: str, debug_rag=False) -> tuple[str, set[str]]:
    db = conectar_banco()

    if "notas_medicas" not in db.table_names():
        return "", set()

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

    blocos_validos = []
    fontes_validas = set()

    for res in resultados:
        score = res.get("_relevance_score", 0.0)
        
        # O score RRF ordena resultados; não mede confiança semântica.
        # Um resultado presente só na busca vetorial tem score ~0.016,
        # mesmo sendo relevante. A suficiência é avaliada pela LLM.

        nome_documento = res.get("nome_arquivo", "Documento Sem Título")

        blocos_validos.append(f"Documento: {nome_documento}\n{res['text']}")
        if (nome_documento not in fontes_validas):
            fontes_validas.add(nome_documento)
        
        if (debug_rag):
            from rich.console import Console
            from rich.panel import Panel
            Console().print(Panel(
                f"[bold yellow]Documento:[/bold yellow] {nome_documento}\n"
                f"[bold magenta]Relevância (Score):[/bold magenta] {score:.4f}\n\n"
                f"[white]{res['text']}[/white]",
                title="[bold blue]🔍 RAG Chunk Recuperado[/bold blue]",
                border_style="blue"
            ))

        
    if not blocos_validos:
        return None, []
        
    contexto_unificado = "\n\n---\n\n".join(blocos_validos)
    return contexto_unificado, list(fontes_validas)
