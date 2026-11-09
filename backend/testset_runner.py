import json
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter


def load_cases(path):
    cases = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(cases, list) or not cases:
        raise ValueError("O testset deve conter uma lista não vazia de casos.")
    identifiers = set()
    for case in cases:
        if not isinstance(case, dict):
            raise ValueError("Cada caso deve ser um objeto JSON.")
        for field in ("id", "question", "reference", "source_document", "category"):
            if not isinstance(case.get(field), str) or not case[field].strip():
                raise ValueError(f"Campo obrigatório ausente ou vazio: {field}.")
        passages = case.get("supporting_passages")
        if not isinstance(passages, list) or not passages or any(
            not isinstance(passage, str) or not passage.strip() for passage in passages
        ):
            raise ValueError(f"Trechos de suporte inválidos no caso {case['id']}.")
        if case["id"] in identifiers:
            raise ValueError(f"Identificador duplicado: {case['id']}.")
        identifiers.add(case["id"])
    return cases


def run_testset(input_path, output_path, configuration, respond):
    cases = load_cases(input_path)
    output = Path(output_path)
    if output.resolve() == Path(input_path).resolve():
        raise ValueError("O arquivo de saída deve ser diferente do testset.")
    report = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "testset": str(Path(input_path).resolve()),
        "configuration": configuration,
        "results": [],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2)
    for case in cases:
        started = perf_counter()
        result = {**case}
        try:
            response, contexts = respond(case["question"])
            result.update(response=response, retrieved_contexts=contexts, status="ok")
        except Exception as error:
            result.update(status="error", error=str(error))
        result["elapsed_seconds"] = perf_counter() - started
        report["results"].append(result)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"{case['id']}: {result['status']}")
    print(f"Resultados salvos em {output}")
    return report
