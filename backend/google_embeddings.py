"""Embeddings remotos com tarefas distintas para documentos e consultas."""

import math
import logging
import threading
import time

from google.genai import errors, types
from lancedb.embeddings import TextEmbeddingFunction, register

try:
    from .google_models import get_client
except ImportError:
    from google_models import get_client

_request_lock = threading.Lock()
_next_request = 0.0


def _request_embeddings(**kwargs):
    """Limita documentos por minuto, inclusive entre chamadas do LanceDB."""
    global _next_request
    with _request_lock:
        for attempt in range(4):
            delay = max(0.0, _next_request - time.monotonic())
            if delay:
                time.sleep(delay)
            # Cada texto do lote pode consumir uma unidade da quota de embeddings.
            _next_request = time.monotonic() + len(kwargs["contents"]) * 0.8
            try:
                return get_client().models.embed_content(**kwargs)
            except errors.APIError as exc:
                if exc.code != 429:
                    raise
                body = exc.details if isinstance(exc.details, dict) else {}
                details = body.get("error", body).get("details", [])
                retry_delay = None
                for detail in details:
                    if detail.get("@type", "").endswith("RetryInfo"):
                        try:
                            retry_delay = float(detail["retryDelay"].removesuffix("s"))
                        except (KeyError, ValueError):
                            pass
                if retry_delay is None or attempt == 3:
                    # Evita que LanceDB repita todo o lote sem respeitar a quota.
                    raise RuntimeError(
                        "Cota de embeddings do Google esgotada. Consulte os limites "
                        "no AI Studio e tente novamente mais tarde."
                    ) from exc
                wait = max(retry_delay + 2, 2 ** attempt)
                logging.warning("Cota de embeddings atingida; aguardando %.1f segundos.", wait)
                _next_request = time.monotonic() + wait


@register("google-gemini")
class GoogleEmbeddings(TextEmbeddingFunction):
    name: str = "gemini-embedding-001"
    dimensions: int = 768

    def ndims(self):
        return self.dimensions

    def _embed(self, texts, task_type):
        texts = list(self.sanitize_input(texts))
        vectors = []
        for start in range(0, len(texts), 20):
            batch = texts[start:start + 20]
            response = _request_embeddings(
                model=self.name,
                contents=batch,
                config=types.EmbedContentConfig(
                    task_type=task_type, output_dimensionality=self.dimensions,
                ),
            )
            embeddings = response.embeddings or []
            if len(embeddings) != len(batch):
                raise RuntimeError("Google retornou uma quantidade inesperada de embeddings.")
            for embedding in embeddings:
                values = embedding.values
                if not values or len(values) != self.dimensions:
                    raise RuntimeError("Google retornou um embedding de dimensão inesperada.")
                norm = math.sqrt(sum(value * value for value in values))
                if not norm:
                    raise RuntimeError("Google retornou um embedding nulo.")
                vectors.append([value / norm for value in values])
        return vectors

    def generate_embeddings(self, texts, *args, **kwargs):
        return self._embed(texts, "RETRIEVAL_DOCUMENT")

    def compute_query_embeddings(self, query, *args, **kwargs):
        return self._embed(query, "RETRIEVAL_QUERY")
