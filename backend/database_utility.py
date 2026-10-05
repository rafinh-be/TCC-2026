"""
Módulo de Banco de Dados Vetorial e Indexação RAG (LanceDB + Sentence Transformers).

Este módulo é responsável por:
1. Gerenciar o modelo de embeddings multilíngue (sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2).
2. Monitorar a pasta de notas médicas em Markdown e verificar se houve alterações ou novos arquivos.
3. Indexar parágrafos das notas médicas no banco vetorial LanceDB com suporte a Busca Híbrida (FTS + Vetorial).
4. Realizar a busca de contextos relevantes para responder às perguntas médicas.
"""

import json, os, lancedb, configparser, frontmatter, contextlib

# Desativa barras de progresso do Hugging Face Hub no console
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"

from pathlib import Path
from dotenv import load_dotenv
from lancedb.pydantic import LanceModel, Vector
from lancedb.embeddings import get_registry
from huggingface_hub import login

# -----------------------------------------------------------------------------
# Configuração e Inicialização
# -----------------------------------------------------------------------------
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
    """
    Remove ou simplifica notações de sintaxe LaTeX no texto dos documentos Markdown,
    convertendo elementos como $\text{MgSO}_4$ ou $MgSO_4$ para texto limpo 'MgSO4'.
    """
    if not text:
        return text

    import re
    # Remove comandos \text{...}
    text = re.sub(r'\\text\{([^}]+)\}', r'\1', text)
    # Substitui operadores de comparação e símbolo de grau
    text = text.replace(r'\ge', '>=').replace(r'\le', '<=').replace(r'^\circ', '°')
    # Remove subscrito simples com underline (ex: MgSO_4 -> MgSO4)
    text = re.sub(r'_([0-9a-zA-Z])', r'\1', text)
    # Remove delimitadores de equações embutidas $...$
    text = re.sub(r'\$([^$]+)\$', r'\1', text)
    # Remove espaços duplos remanescentes
    text = re.sub(r' +', ' ', text)
    return text

def split_text_into_chunks(text: str, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP) -> list[str]:

    """
    Divide um texto em chunks de tamanho máximo 'chunk_size' com sobreposição 'chunk_overlap'.
    Por padrão, o chunk_overlap é 20% do chunk_size.
    Preserva a integridade de palavras ajustando os limites em espaços ou quebras de linha.
    """
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
    """
    Carrega o modelo de embeddings multilíngue via Sentence Transformers no LanceDB.
    Utiliza CPU por padrão para compatibilidade ampla.
    """
    global embedding_model
    global registry
    
    registry = get_registry()
    embedding_model = registry.get("sentence-transformers").create(
        name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", 
        device="cpu",
    )

def needs_indexing(verbose=False) -> bool:
    """
    Verifica se a base de dados vetorial precisa ser reindexada.
    Compara o tempo de modificação (mtime) dos arquivos .md em NOTES_DIR
    com o estado salvo no arquivo JSON de memória (MEMORY_FILE).
    
    :return: True se houver arquivos novos, editados ou removidos; False caso contrário.
    """
    path_dir = Path(NOTES_DIR)
    if not path_dir.exists():
        path_dir.mkdir(exist_ok=True)
        return False

    # Mapeia cada arquivo .md para a sua última data de modificação
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

    # Se a quantidade de arquivos mudou, precisa reindexar
    if len(estado_atual) != len(memoria_salva):
        return True

    # Verifica se algum arquivo foi modificado desde a última sincronização
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
    """Atualiza o arquivo JSON de memória com os timestamps mtime dos arquivos Markdown atuais."""
    path_dir = Path(NOTES_DIR)
    estado_atual = {}
    for arquivo_md in path_dir.glob("*.md"):
        estado_atual[arquivo_md.name] = os.path.getmtime(arquivo_md)
        
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(estado_atual, f, indent=4)

def conectar_banco():
    """Estabelece e retorna a conexão com o banco de dados LanceDB no caminho configurado."""
    Path(DB_PATH).mkdir(exist_ok=True)
    return lancedb.connect(DB_PATH)
        
def index_data(verbose=False):
    """
    Lê todos os arquivos Markdown na pasta de notas, faz o parsing do frontmatter (tags/título),
    divide o texto em parágrafos e gera a tabela 'notas_medicas' no LanceDB com índice FTS (Full Text Search).
    """
    db = conectar_banco()
    path_dir = Path(NOTES_DIR)
    path_dir.mkdir(exist_ok=True)
    
    global embedding_model
    global registry
    if (not embedding_model):
        load_embedding_model()

    # Esquema da tabela LanceDB com suporte a embedding automático no campo 'text'
    class DocumentoOBGYN(LanceModel):
        text: str = embedding_model.SourceField()
        vector: Vector(embedding_model.ndims()) = embedding_model.VectorField()
        nome_arquivo: str
        tags: list[str]  
    
    chunks_to_save = []
    
    # Processa cada nota médica em Markdown
    for arquivo_md in path_dir.glob("*.md"):
        post = frontmatter.load(arquivo_md)
        
        tags = post.get("tags", [])
        conteudo_limpo = clean_latex_math(post.content)

        
        # Divisão do texto em chunks com sobreposição (chunk_overlap = 20% de chunk_size)
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

    # Sobrescreve a tabela no LanceDB e adiciona os novos dados
    table = db.create_table("notas_medicas", schema=DocumentoOBGYN, mode="overwrite")
    table.add(chunks_to_save)
    
    # Cria índice de busca em texto completo (FTS) para suporte à busca híbrida
    table.create_fts_index("text", replace=True)
    
    # Salva o estado atual na memória para evitar reindexações desnecessárias
    update_memory()
    
def _tokenize_query(pergunta: str) -> list[float]:
    """Gera o vetor de embedding para a pergunta de consulta do usuário."""
    global embedding_model
    global registry
    if (not embedding_model):
        load_embedding_model()
    
    return embedding_model.compute_query_embeddings(pergunta)[0]

def retrieve_context(pergunta: str, debug_rag=False) -> tuple[str, set[str]]:
    """
    Realiza a busca híbrida (vetorial + texto) na tabela 'notas_medicas' do LanceDB.
    
    :param pergunta: Texto da dúvida médica do usuário.
    :param debug_rag: Se True, imprime logs detalhados dos chunks encontrados e seus scores.
    :return: Tupla com (contexto_unificado_em_string, lista_de_nomes_de_fontes).
    """
    db = conectar_banco()

    if "notas_medicas" not in db.table_names():
        return "", set()

    table = db.open_table("notas_medicas")

    vetor_query = _tokenize_query(pergunta)

    SCORE_MINIMO = 0.02

    # Executa busca híbrida combinando dissimilaridade vetorial (L2) e FTS
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
        
        # Filtra resultados com relevância abaixo do threshold
        if score < SCORE_MINIMO:
            continue

        nome_documento = res.get("nome_arquivo", "Documento Sem Título")

        blocos_validos.append(res["text"])
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
