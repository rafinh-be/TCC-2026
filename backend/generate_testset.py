import argparse, configparser, csv, json
from pathlib import Path

import frontmatter
from pydantic import BaseModel
from google.genai import types

from chunking import chunk_text
from google_models import get_client
from testset_logic import RECORD_FIELDS, build_records, sample_evenly

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

NOTES_DIR = Path(config.get("database", "NOTES_DIR"))
CHUNK_SIZE = config.getint("database", "CHUNK_SIZE")
CHUNK_OVERLAP = config.getint("database", "CHUNK_OVERLAP")
TESTSET_PATH = Path(config.get("evaluation", "TESTSET_PATH"))
prompt_geracao_testset = config.get("evaluation", "prompt_geracao_testset")
refusal_phrase = config.get("prompts_termino", "prompt_restricao_1")


class SyntheticQA(BaseModel):
    pergunta_simples: str
    resposta_simples: str
    pergunta_raciocinio: str
    resposta_raciocinio: str
    pergunta_fora_escopo: str


parser = argparse.ArgumentParser("generate_testset")
parser.add_argument("--chunking", choices=["paragraph", "window"], default="window", help="Strategy used to split notes into the chunks that questions are generated from")
parser.add_argument("--chunks_per_document", type=int, default=2, help="Number of chunks sampled evenly from each note")
parser.add_argument("--output", action="store", default=str(TESTSET_PATH), help="Path of the generated JSON test set")
parser.add_argument("--csv", action="store_true", help="Also write the test set as CSV next to the JSON file")
args = parser.parse_args()


def generate_qa(titulo, chunk):
    response = get_client().models.generate_content(
        model=config.get("gemini", "llm_model"),
        contents=prompt_geracao_testset.format(fonte=titulo, trecho=chunk),
        config=types.GenerateContentConfig(response_mime_type="application/json", response_schema=SyntheticQA),
    )
    return SyntheticQA.model_validate_json(response.text).model_dump()


def build_testset():
    records = []
    failures = 0
    for arquivo_md in sorted(NOTES_DIR.glob("*.md")):
        post = frontmatter.load(arquivo_md)
        titulo = post.get("titulo", arquivo_md.stem)
        chunks = chunk_text(post.content, args.chunking, CHUNK_SIZE, CHUNK_OVERLAP)
        for chunk in sample_evenly(chunks, args.chunks_per_document):
            try:
                qa = generate_qa(titulo, chunk)
            except Exception as error:
                failures += 1
                print(f"Falha ao gerar perguntas para {arquivo_md.name}: {error}")
                continue
            records.extend(build_records(arquivo_md.name, titulo, chunk, qa, refusal_phrase))
            print(f"Gerado: {arquivo_md.name}")
    return records, failures


def write_testset(records, output):
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.csv:
        with open(output.with_suffix(".csv"), "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=RECORD_FIELDS)
            writer.writeheader()
            writer.writerows(records)


if __name__ == "__main__":
    records, failures = build_testset()
    write_testset(records, Path(args.output))
    print(f"{len(records)} casos salvos em {args.output} ({failures} trechos com falha).")
