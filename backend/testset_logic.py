RECORD_FIELDS = ("fonte_documento", "arquivo", "evolution_type", "question", "ground_truth", "context", "expected_refusal")


def sample_evenly(items, count):
    if count <= 0 or not items:
        return []
    if count >= len(items):
        return list(items)
    if count == 1:
        return [items[len(items) // 2]]
    last = len(items) - 1
    return [items[round(position * last / (count - 1))] for position in range(count)]


def build_records(arquivo, titulo, chunk, qa, refusal_phrase):
    base = {"fonte_documento": titulo, "arquivo": arquivo, "context": chunk}
    return [
        {**base, "evolution_type": "simple", "question": qa["pergunta_simples"], "ground_truth": qa["resposta_simples"], "expected_refusal": False},
        {**base, "evolution_type": "reasoning", "question": qa["pergunta_raciocinio"], "ground_truth": qa["resposta_raciocinio"], "expected_refusal": False},
        {**base, "evolution_type": "unanswerable_refusal", "question": qa["pergunta_fora_escopo"], "ground_truth": refusal_phrase, "expected_refusal": True},
    ]
