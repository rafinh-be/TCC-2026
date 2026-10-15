import configparser
import os
import ssl
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types
import truststore

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR.parent / ".env")
load_dotenv(BASE_DIR / ".env")
config = configparser.ConfigParser()
config.read(BASE_DIR / "config.ini", encoding="utf-8")


def model_setting(name):
    return os.getenv(name.upper()) or config.get("model", name)


@lru_cache(maxsize=1)
def get_client():
    key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not key:
        raise RuntimeError("Defina GEMINI_API_KEY no ambiente ou em backend/.env para usar a API do Google.")
    ssl_context = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    # Preserva certificados adicionais configurados pelo administrador.
    cafile = os.getenv("SSL_CERT_FILE")
    capath = os.getenv("SSL_CERT_DIR")
    if cafile or capath:
        ssl_context.load_verify_locations(cafile=cafile, capath=capath)
    return genai.Client(
        api_key=key,
        http_options=types.HttpOptions(
            timeout=int(model_setting("request_timeout_seconds")) * 1000,
            client_args={"verify": ssl_context},
            async_client_args={"verify": ssl_context},
        ),
    )
