import sys
from pathlib import Path

import ollama
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


def typed_response(content, done_reason="stop", thinking=None):
    return ollama.ChatResponse(model="qwen", done_reason=done_reason, message=ollama.Message(role="assistant", content=content, thinking=thinking))


def test_answer_accepts_citations_and_raw_content_like_the_gemini_answer(scripted_chat):
    scripted_chat([typed_response("resposta [1]")])
    answer = ollama_interaction.chat_with_thought_limit(PAYLOAD)
    answer["message"]["raw_content"] = "resposta [1]"
    answer["citations"] = []
    assert answer["message"]["content"] == "resposta [1]"


def test_fallback_answer_is_a_plain_dict_with_thinking(scripted_chat):
    scripted_chat([typed_response("", "length", "pensando"), typed_response("resposta final")])
    answer = ollama_interaction.chat_with_thought_limit(PAYLOAD)
    answer["citations"] = []
    assert answer["message"]["content"] == "resposta final"
    assert answer["message"]["thinking"].startswith("<think>")


def test_stream_answer_event_carries_the_plain_answer(scripted_chat):
    scripted_chat([typed_response("resposta")])
    events = list(ollama_interaction.chat_stream(PAYLOAD))
    assert events == [{"type": "answer", "answer": {"message": {"role": "assistant", "content": "resposta"}}}]


def test_reasoning_can_be_disabled_without_thinking_fallback(scripted_chat):
    calls = scripted_chat([response('resposta')])
    result = ollama_interaction.chat_with_thought_limit(PAYLOAD, think=False)
    assert calls[0]['think'] is False
    assert 'num_predict' not in calls[0]['options']
    assert result['message']['content'] == 'resposta'
    assert len(calls) == 1


def test_reasoning_can_be_enabled_explicitly(scripted_chat):
    calls = scripted_chat([response('resposta', thinking='pensamento')])
    result = ollama_interaction.chat_with_thought_limit(PAYLOAD, think=True)
    assert calls[0]['think'] is True
    assert result['message']['thinking'] == 'pensamento'


def test_disabled_reasoning_rejects_unexpected_thinking(scripted_chat):
    scripted_chat([response('resposta', thinking='pensamento inesperado')])
    with pytest.raises(ValueError, match='thinking desativado'):
        ollama_interaction.chat_with_thought_limit(PAYLOAD, think=False)


def test_base_model_is_selected_for_non_thinking_demo(scripted_chat):
    calls = scripted_chat([response('resposta')])
    result = ollama_interaction.chat_with_thought_limit(PAYLOAD, think=False, model_variant='base')
    assert calls[0]['model'] == ollama_interaction.config.get('model', 'model_base')
    assert calls[0]['think'] is False
    assert result['message']['content'] == 'resposta'


def test_seed_is_forwarded_to_ollama(scripted_chat):
    calls = scripted_chat([response('resposta')])
    ollama_interaction.chat_with_thought_limit(PAYLOAD, think=False, model_variant='base', seed=1)
    assert calls[0]['options']['seed'] == 1
