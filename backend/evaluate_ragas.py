import argparse
import asyncio
import configparser
import json
import math
import os
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path

from testset_runner import load_cases


def load_samples(result_path, testset_path):
    run = json.loads(Path(result_path).read_text(encoding="utf-8"))
    cases = {case["id"]: case for case in load_cases(testset_path)}
    samples = []
    seen = set()
    for row in run["results"]:
        identifier = row["id"]
        if identifier in seen:
            raise ValueError(f"Resultado duplicado: {identifier}.")
        seen.add(identifier)
        case = cases[identifier]
        if row["question"] != case["question"]:
            raise ValueError(f"A pergunta mudou no caso {identifier}; gere novamente a resposta.")
        if row.get("status") != "ok":
            raise ValueError(f"O caso {identifier} falhou na geração da resposta.")
        contexts = row.get("retrieved_contexts")
        if not isinstance(contexts, list) or any(not isinstance(text, str) for text in contexts):
            raise ValueError(f"Contextos inválidos no caso {identifier}.")
        if not isinstance(row.get("response"), str) or not row["response"].strip():
            raise ValueError(f"Resposta vazia no caso {identifier}.")
        samples.append({**row, **case})
    if seen != set(cases):
        raise ValueError("Os resultados não cobrem todos os casos do testset revisado.")
    return run, samples


def build_metrics(judge, config):
    from openai import AsyncOpenAI
    from ragas.embeddings.base import BaseRagasEmbedding
    from ragas.llms import llm_factory
    from ragas.metrics.collections import AnswerRelevancy, ContextPrecision, ContextRecall, Faithfulness
    from sentence_transformers import SentenceTransformer

    class LocalEmbeddings(BaseRagasEmbedding):
        def __init__(self):
            super().__init__()
            self.model = SentenceTransformer(
                config.get("local_embeddings", "embedding_model"),
                device=config.get("local_embeddings", "device"),
                local_files_only=config.getboolean("evaluation", "embedding_local_files_only"),
            )

        def embed_text(self, text, **kwargs):
            return self.model.encode(text).tolist()

        async def aembed_text(self, text, **kwargs):
            return await asyncio.to_thread(self.embed_text, text)

    api_key = "ollama" if judge == "ollama" else os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Defina GEMINI_API_KEY em backend/.env para avaliar com Gemini.")
    client = AsyncOpenAI(
        api_key=api_key,
        base_url=config.get("evaluation", f"{judge}_judge_url"),
        timeout=config.getint("evaluation", "judge_timeout_seconds"),
        max_retries=config.getint("evaluation", "judge_max_retries"),
        default_headers={"x-goog-api-client": "tcc-ragas/1.0"} if judge == "gemini" else {},
    )
    judge_options = {}
    if judge == "ollama":
        judge_options["reasoning_effort"] = config.get("evaluation", "ollama_judge_reasoning_effort")
    llm = llm_factory(
        config.get("evaluation", f"{judge}_judge_model"),
        client=client,
        temperature=config.getfloat("evaluation", "judge_temperature"),
        max_tokens=config.getint("evaluation", "judge_max_tokens"),
        **judge_options,
    )
    return client, {
        "context_precision": ContextPrecision(llm=llm),
        "context_recall": ContextRecall(llm=llm),
        "faithfulness": Faithfulness(llm=llm),
        "response_relevancy": AnswerRelevancy(
            llm=llm,
            embeddings=LocalEmbeddings(),
            strictness=config.getint("evaluation", "relevancy_strictness"),
        ),
    }


async def score_samples(samples, metrics, report, output):
    for sample in samples:
        row = {**sample, "scores": {}, "errors": {}}
        for name, metric in metrics.items():
            if name in ("context_precision", "context_recall"):
                arguments = {
                    "user_input": sample["question"], "reference": sample["reference"],
                    "retrieved_contexts": sample["retrieved_contexts"],
                }
            else:
                arguments = {"user_input": sample["question"], "response": sample["response"]}
                if name == "faithfulness":
                    arguments["retrieved_contexts"] = sample["retrieved_contexts"]
            try:
                score = float((await metric.ascore(**arguments)).value)
                if not math.isfinite(score):
                    raise ValueError("A métrica retornou um valor não finito.")
                row["scores"][name] = score
            except Exception as error:
                row["scores"][name] = None
                row["errors"][name] = str(error)
            print(f"{sample['id']} / {name}: {row['scores'][name]}")
        report["results"].append(row)
        report["summary"] = {}
        for name in metrics:
            values = [item["scores"][name] for item in report["results"] if item["scores"][name] is not None]
            report["summary"][name] = {
                "mean": sum(values) / len(values) if values else None,
                "valid_count": len(values),
                "error_count": len(report["results"]) - len(values),
            }
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")


async def evaluate(args):
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).with_name(".env"))
    config = configparser.ConfigParser()
    config.read(Path(__file__).with_name("config.ini"), encoding="utf-8")
    run, samples = load_samples(args.results, args.testset)
    output = Path(args.output)
    if output.exists():
        raise FileExistsError(f"O arquivo de saída já existe: {output}")
    client, metrics = build_metrics(args.judge, config)
    try:
        report = {
            "started_at": datetime.now(timezone.utc).isoformat(),
            "ragas_version": version("ragas"),
            "judge": args.judge,
            "judge_model": config.get("evaluation", f"{args.judge}_judge_model"),
            "evaluation_configuration": dict(config["evaluation"]),
            "embedding_configuration": dict(config["local_embeddings"]),
            "source_results": str(Path(args.results).resolve()),
            "reviewed_testset": str(Path(args.testset).resolve()),
            "generation_configuration": run["configuration"],
            "results": [],
        }
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("x", encoding="utf-8") as stream:
            json.dump(report, stream, ensure_ascii=False, indent=2)
        await score_samples(samples, metrics, report, output)
        print(f"Avaliação salva em {output}")
        return any(row["errors"] for row in report["results"])
    finally:
        await client.close()


def main():
    parser = argparse.ArgumentParser(description="Avalia respostas existentes com RAGAS.")
    parser.add_argument("--results", required=True, help="JSON produzido por main.py --testset")
    parser.add_argument("--testset", required=True, help="JSON com as referências revisadas")
    parser.add_argument("--judge", required=True, choices=["ollama", "gemini"])
    parser.add_argument("--output", required=True, help="Novo arquivo JSON para as pontuações")
    args = parser.parse_args()
    try:
        failed = asyncio.run(evaluate(args))
    except (ImportError, ValueError, OSError, KeyError) as error:
        parser.exit(1, f"Falha na avaliação: {error}\n")
    if failed:
        parser.exit(1, "Avaliação concluída com falhas em métricas; consulte errors no JSON.\n")


if __name__ == "__main__":
    main()
