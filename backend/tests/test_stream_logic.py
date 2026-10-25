import json
import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from stream_logic import split_parts, thinking_event, final_event, error_event, encode_event


def part(text, thought=False):
    return SimpleNamespace(text=text, thought=thought)


def test_split_parts_separates_thoughts_from_answer_text():
    parts = [part("pensando", True), part("resposta"), part("mais pensamento", True)]
    assert split_parts(parts) == (["pensando", "mais pensamento"], ["resposta"])


def test_split_parts_drops_empty_and_missing_text():
    parts = [part("", True), part(None), part("ok")]
    assert split_parts(parts) == ([], ["ok"])


def test_split_parts_with_no_parts_returns_empty_lists():
    assert split_parts([]) == ([], [])


def test_events_carry_their_type():
    assert thinking_event("x") == {"type": "thinking", "text": "x"}
    assert error_event("falhou") == {"type": "error", "message": "falhou"}
    assert final_event({"message": {}}, [], []) == {"type": "final", "answer": {"message": {}}, "sources": [], "citations": []}


def test_encode_event_is_one_json_line_keeping_accents():
    line = encode_event(thinking_event("pré-eclâmpsia"))
    assert line.endswith("\n") and line.count("\n") == 1
    assert "pré-eclâmpsia" in line
    assert json.loads(line) == thinking_event("pré-eclâmpsia")
