import configparser, os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

client = None

def get_client():
    global client
    if (not client):
        api_key = os.getenv("GEMINI_API_KEY")
        if (not api_key):
            raise RuntimeError("Defina GEMINI_API_KEY em backend/.env para usar o Gemini.")
        client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(timeout=config.getint("gemini", "request_timeout_seconds") * 1000),
        )
    return client
