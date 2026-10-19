import configparser, os

os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"

from lancedb.embeddings import get_registry

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

def create_embedding_model():
    return get_registry().get("sentence-transformers").create(
        name=config.get("local_embeddings", "embedding_model"),
        device=config.get("local_embeddings", "device"),
    )

def embedding_signature():
    return {"provider": "sentence-transformers", "model": config.get("local_embeddings", "embedding_model")}
