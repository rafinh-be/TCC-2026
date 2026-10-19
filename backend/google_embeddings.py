import configparser, math, time
from google.genai import errors, types
from lancedb.embeddings import TextEmbeddingFunction, register
from google_models import get_client

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

def request_embeddings(**kwargs):
    max_attempts = config.getint("gemini", "embedding_max_attempts")
    for attempt in range(max_attempts):
        try:
            return get_client().models.embed_content(**kwargs)
        except errors.APIError as error:
            if (error.code != 429 or attempt == max_attempts - 1):
                raise
            time.sleep(config.getfloat("gemini", "embedding_retry_seconds") * (attempt + 1))

@register("google-gemini")
class GoogleEmbeddings(TextEmbeddingFunction):
    name: str = "gemini-embedding-001"
    dimensions: int = 768
    batch_size: int = 20

    def ndims(self):
        return self.dimensions

    def embed(self, texts, task_type):
        texts = list(self.sanitize_input(texts))
        vectors = []
        for start in range(0, len(texts), self.batch_size):
            batch = texts[start:start + self.batch_size]
            response = request_embeddings(
                model=self.name,
                contents=batch,
                config=types.EmbedContentConfig(task_type=task_type, output_dimensionality=self.dimensions),
            )
            for embedding in response.embeddings:
                norm = math.sqrt(sum(value * value for value in embedding.values))
                vectors.append([value / norm for value in embedding.values])
        return vectors

    def generate_embeddings(self, texts, *args, **kwargs):
        return self.embed(texts, "RETRIEVAL_DOCUMENT")

    def compute_query_embeddings(self, query, *args, **kwargs):
        return self.embed(query, "RETRIEVAL_QUERY")

def create_embedding_model():
    return GoogleEmbeddings.create(
        name=config.get("gemini", "embedding_model"),
        dimensions=config.getint("gemini", "embedding_dimensions"),
        batch_size=config.getint("gemini", "embedding_batch_size"),
    )

def embedding_signature():
    return {
        "provider": "google-gemini",
        "model": config.get("gemini", "embedding_model"),
        "dimensions": config.getint("gemini", "embedding_dimensions"),
    }
