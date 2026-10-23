from testset_logic import RECORD_FIELDS, build_records, sample_evenly


def test_sample_evenly_returns_everything_when_count_exceeds_items():
    assert sample_evenly(["a", "b"], 5) == ["a", "b"]


def test_sample_evenly_spreads_across_items():
    assert sample_evenly(list(range(10)), 3) == [0, 4, 9]
    picked = sample_evenly(list(range(10)), 4)
    assert picked[0] == 0 and picked[-1] == 9 and len(set(picked)) == 4


def test_sample_evenly_single_pick_is_middle_item():
    assert sample_evenly(list(range(5)), 1) == [2]


def test_sample_evenly_handles_empty_and_non_positive():
    assert sample_evenly([], 3) == []
    assert sample_evenly([1, 2], 0) == []


def test_build_records_creates_three_cases_with_refusal_phrase():
    qa = {
        "pergunta_simples": "p1",
        "resposta_simples": "r1",
        "pergunta_raciocinio": "p2",
        "resposta_raciocinio": "r2",
        "pergunta_fora_escopo": "p3",
    }
    records = build_records("nota.md", "Nota", "trecho", qa, "recusa")
    assert [record["evolution_type"] for record in records] == ["simple", "reasoning", "unanswerable_refusal"]
    assert [record["expected_refusal"] for record in records] == [False, False, True]
    assert records[2]["ground_truth"] == "recusa"
    assert all(record["context"] == "trecho" and record["arquivo"] == "nota.md" for record in records)
    assert all(set(record) == set(RECORD_FIELDS) for record in records)
