import json


def split_parts(parts):
    thoughts = [part.text for part in parts if part.thought and part.text]
    answers = [part.text for part in parts if not part.thought and part.text]
    return thoughts, answers


def thinking_event(text):
    return {"type": "thinking", "text": text}


def final_event(answer, sources, citations):
    return {"type": "final", "answer": answer, "sources": sources, "citations": citations}


def error_event(message):
    return {"type": "error", "message": message}


def provider_event(provider, event):
    return {**event, "provider": provider}


def encode_event(event):
    return json.dumps(event, ensure_ascii=False) + "\n"
