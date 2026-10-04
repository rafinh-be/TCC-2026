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
config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

NOTES_DIR = config.get("database", "NOTES_DIR")
MEMORY_FILE = config.get("database", "MEMORY_FILE")
DB_PATH = config.get("database", "DB_PATH")

embedding_model = None
registry = None

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
        conteudo_limpo = post.content
        
        # Divisão simples em parágrafos
        paragrafos = [p.strip() for p in conteudo_limpo.split("\n\n") if p.strip()]
        
        if (verbose):
            print("Indexando:", post.get("titulo", arquivo_md.stem))
        
        for para in paragrafos:
            chunks_to_save.append({
                "text": para,
                "nome_arquivo": post.get("titulo", arquivo_md.stem),  
                "tags": tags
            })
            if (verbose):
                print(para, tags)
        
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
            print("Documento encontrado com score de", score, "e título:", nome_documento, "\n\n", res["text"])
        
    if not blocos_validos:
        return None, []
        
    contexto_unificado = "\n\n---\n\n".join(blocos_validos)
    return contexto_unificado, list(fontes_validas)