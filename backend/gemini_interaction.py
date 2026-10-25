import configparser
from google.genai import types
from google_models import get_client
from stream_logic import split_parts, thinking_event

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

def build_request(payload):
    system_prompt = "\n\n".join(message["content"] for message in payload if message["role"] == "system")

    contents = []
    for message in payload:
        if (message["role"] == "system"):
            continue
        role = "model" if message["role"] == "assistant" else "user"
        contents.append(types.Content(role=role, parts=[types.Part.from_text(text=message["content"])]))

    return system_prompt, contents

def chat(payload, verbose=False, debug_model=False):
    system_prompt, contents = build_request(payload)

    model_name = config.get("gemini", "llm_model")
    if (verbose or debug_model):
        print("Starting model", model_name)

    response = get_client().models.generate_content(
        model=model_name,
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            thinking_config=types.ThinkingConfig(
                thinking_level=config.get("gemini", "thinking_level"),
                include_thoughts=debug_model,
            ),
            max_output_tokens=config.getint("gemini", "max_output_tokens"),
        ),
    )

    if (not response.text or not response.text.strip()):
        raise RuntimeError("Gemini não retornou texto. Verifique os filtros de segurança do modelo.")
    if (response.candidates[0].finish_reason != types.FinishReason.STOP):
        raise RuntimeError(f"Gemini não concluiu a resposta: {response.candidates[0].finish_reason}")

    thoughts = "\n".join(part.text for part in response.candidates[0].content.parts if part.thought and part.text)
    if (debug_model):
        print("Gemini thoughts:\n" + (thoughts or "(no thought summary returned)"))

    message = {"role": "assistant", "content": response.text}
    if (thoughts):
        message["thinking"] = thoughts

    return {"message": message}


def chat_stream(payload, verbose=False, debug_model=False):
    system_prompt, contents = build_request(payload)

    model_name = config.get("gemini", "llm_model")
    if (verbose or debug_model):
        print("Starting model", model_name)

    stream = get_client().models.generate_content_stream(
        model=model_name,
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            thinking_config=types.ThinkingConfig(
                thinking_level=config.get("gemini", "stream_thinking_level"),
                include_thoughts=True,
            ),
            max_output_tokens=config.getint("gemini", "max_output_tokens"),
        ),
    )

    thoughts = []
    answers = []
    finish_reason = None
    for chunk in stream:
        if (not chunk.candidates):
            continue
        candidate = chunk.candidates[0]
        finish_reason = candidate.finish_reason or finish_reason
        parts = candidate.content.parts if candidate.content and candidate.content.parts else []
        new_thoughts, new_answers = split_parts(parts)
        for thought in new_thoughts:
            thoughts.append(thought)
            yield thinking_event(thought)
        answers.extend(new_answers)

    text = "".join(answers)
    if (not text.strip()):
        raise RuntimeError("Gemini não retornou texto. Verifique os filtros de segurança do modelo.")
    if (finish_reason != types.FinishReason.STOP):
        raise RuntimeError(f"Gemini não concluiu a resposta: {finish_reason}")

    message = {"role": "assistant", "content": text}
    if (thoughts):
        message["thinking"] = "\n".join(thoughts)

    yield {"type": "answer", "answer": {"message": message}}
