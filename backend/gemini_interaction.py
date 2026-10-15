import configparser
from time import perf_counter
from pathlib import Path
from google.genai import types
from google_models import get_client, model_setting

BASE_DIR = Path(__file__).parent
config = configparser.ConfigParser()
config.read(BASE_DIR / 'config.ini', encoding='utf-8')

def create_payload(historico_conversa, message, contexto, fontes):
    payload = []
    
    try:
        with open(BASE_DIR / "config_agent.md", "r", encoding="utf-8") as f:
            prompt_sistema = f.read()
    except FileNotFoundError:
        prompt_sistema = config.get('prompts', 'prompt_sistema')

    
    payload.append({"role": "system", "content": prompt_sistema})    
    
    for mensagem in historico_conversa:
        payload.append({"role": mensagem["role"], "content": mensagem["content"]})
    
    if contexto:
        payload.append({"role": "system", "content": f"Contexto adicional: <contexto_local>{contexto}</contexto_local>"})
    else:
        payload.append({"role": "system", "content": f"Contexto adicional: <contexto_local>Não ha contexto local, responda apenas com a frase 'Não encontrei dados ou critérios suficientes para esta conduta específica na minha base local de evidências.'</contexto_local>"})
    if fontes:
        payload.append({"role": "system", "content": f"Fontes adicionais: {', '.join(fontes)}"})
    
    payload.append({"role": "user", "content": message})
    
    return payload


def chat(payload, verbose=False, debug_model=False):
    system = "\n\n".join(m["content"] for m in payload if m["role"] == "system")
    contents = [
        types.Content(
            role="model" if m["role"] == "assistant" else "user",
            parts=[types.Part.from_text(text=m["content"])],
        )
        for m in payload if m["role"] != "system"
    ]
    model = model_setting("llm_model")
    if verbose or debug_model:
        print("Usando Gemini:", model)
    started = perf_counter()
    response = get_client().models.generate_content(
        model=model,
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=system,
            thinking_config=types.ThinkingConfig(
                thinking_level=model_setting("thinking_level"),
            ),
            max_output_tokens=int(model_setting("max_output_tokens")),
        ),
    )
    if verbose or debug_model:
        print(f"Tempo de resposta do Gemini: {perf_counter() - started:.1f}s")
    if not response.text or not response.text.strip():
        raise RuntimeError("Gemini n?o retornou texto. Verifique os filtros de seguran?a e os limites de gera??o.")
    candidates = response.candidates or []
    if candidates and candidates[0].finish_reason != types.FinishReason.STOP:
        raise RuntimeError(f"Gemini n?o concluiu a resposta: {candidates[0].finish_reason}")
    return {"message": {"role": "assistant", "content": response.text}}
