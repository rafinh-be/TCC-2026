# config.py
from pathlib import Path
import lancedb
from lancedb.pydantic import LanceModel, Vector
from lancedb.embeddings import get_registry

DB_PATH = "./lancedb_obgyn"
NOTES_DIR = "./my_notes"

# Inicializa o modelo multilíngue adequado para o Português
registry = get_registry()
embedding_model = registry.get("sentence-transformers").create(
    name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", 
    device="cpu"
)

# Schema do Banco de Dados
class DocumentoOBGYN(LanceModel):
    text: str = embedding_model.SourceField()
    vector: Vector(embedding_model.ndims()) = embedding_model.VectorField()
    nome_arquivo: str
    tags: list[str]  # Lista de tags para o agrupamento automático

def conectar_banco():
    Path(DB_PATH).mkdir(exist_ok=True)
    return lancedb.connect(DB_PATH)