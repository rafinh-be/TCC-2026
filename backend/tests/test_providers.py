import sys
from pathlib import Path
from unittest import mock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import providers


def fake_module(name):
    module = mock.Mock()
    module.chat.return_value = f"{name}-chat"
    module.chat_stream.return_value = iter([f"{name}-stream"])
    return module


@pytest.fixture
def modules(monkeypatch):
    loaded = {"gemini_interaction": fake_module("gemini"), "ollama_interaction": fake_module("ollama")}
    monkeypatch.setattr(providers, "import_module", lambda name: loaded[name])
    monkeypatch.setattr(providers, "_active_provider", "ollama")
    return loaded


def test_chat_uses_the_active_provider_by_default(modules):
    assert providers.chat([]) == "ollama-chat"
    assert list(providers.chat_stream([])) == ["ollama-stream"]


def test_chat_provider_argument_overrides_the_active_provider(modules):
    assert providers.chat([], provider="gemini") == "gemini-chat"
    assert list(providers.chat_stream([], provider="gemini")) == ["gemini-stream"]
