import configparser
from google.genai import types
from google_models import get_client

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

def chat(payload, verbose=False, debug_model=False):
    system_prompt = "\n\n".join(message["content"] for message in payload if message["role"] == "system")

    contents = []
    for message in payload:
        if (message["role"] == "system"):
            continue
        role = "model" if message["role"] == "assistant" else "user"
        contents.append(types.Content(role=role, parts=[types.Part.from_text(text=message["content"])]))

    model_name = config.get("gemini", "llm_model")
    if (verbose or debug_model):
        print("Starting model", model_name)

    response = get_client().models.generate_content(
        model=model_name,
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            thinking_config=types.ThinkingConfig(thinking_level=config.get("gemini", "thinking_level")),
            max_output_tokens=config.getint("gemini", "max_output_tokens"),
        ),
    )

    if (not response.text or not response.text.strip()):
        raise RuntimeError("Gemini não retornou texto. Verifique os filtros de segurança do modelo.")
    if (response.candidates[0].finish_reason != types.FinishReason.STOP):
        raise RuntimeError(f"Gemini não concluiu a resposta: {response.candidates[0].finish_reason}")

    return {"message": {"role": "assistant", "content": response.text}}
