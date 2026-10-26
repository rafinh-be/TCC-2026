import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import ollama_interaction


def response(content, done_reason="stop", thinking=""):
    return {"message": {"content": content, "thinking": thinking}, "done_reason": done_reason}


@pytest.fixture
def scripted_chat(monkeypatch):
    calls = []

    def install(responses):
        queue = list(responses)

        def fake_chat(**kwargs):
            calls.append(kwargs)
            return queue.pop(0)

        monkeypatch.setattr(ollama_interaction.ollama, "chat", fake_chat)
        return calls

    return install


PAYLOAD = [{"role": "user", "content": "pergunta"}]


def test_complete_first_response_is_returned_without_fallback(scripted_chat):
    calls = scripted_chat([response("resposta")])
    result = ollama_interaction.chat_with_thought_limit(PAYLOAD)
    assert result["message"]["content"] == "resposta"
    assert len(calls) == 1


def test_thinking_limit_comes_from_config(scripted_chat):
    calls = scripted_chat([response("resposta")])
    ollama_interaction.chat_with_thought_limit(PAYLOAD)
    assert calls[0]["options"]["num_predict"] == ollama_interaction.config.getint("model", "max_think_tokens")


def test_truncated_thinking_falls_back_to_a_final_answer(scripted_chat):
    calls = scripted_chat([response("", "length", "pensando"), response("resposta final")])
    result = ollama_interaction.chat_with_thought_limit(PAYLOAD)
    assert result["message"]["content"] == "resposta final"
    assert result["message"]["thinking"].startswith("<think>")
    assert len(calls) == 2


def test_empty_fallback_is_retried_once(scripted_chat):
    calls = scripted_chat([response("", "length", "pensando"), response("  "), response("resposta depois do retry")])
    result = ollama_interaction.chat_with_thought_limit(PAYLOAD)
    assert result["message"]["content"] == "resposta depois do retry"
    assert len(calls) == 3


def test_fallback_gives_up_after_one_retry(scripted_chat):
    calls = scripted_chat([response("", "length", "pensando"), response(""), response("")])
    result = ollama_interaction.chat_with_thought_limit(PAYLOAD)
    assert result["message"]["content"] == ""
    assert len(calls) == 3
