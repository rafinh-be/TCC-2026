import os
import glob
import json
import pandas as pd
from pydantic import BaseModel, Field
import ollama

# -----------------------------------------------------------------------------
# 1. ESTRUTURA PARA GERAÇÃO SINTÉTICA DE PERGUNTAS (Estilo Ragas Testset)
# -----------------------------------------------------------------------------
class SyntheticQA(BaseModel):
    pergunta_simples: str = Field(
        description="Uma pergunta direta sobre um fato especifico do texto."
    )
    resposta_simples: str = Field(
        description="A resposta exata extraida do texto para a pergunta simples."
    )
    pergunta_raciocinio: str = Field(
        description="Uma pergunta clinica que exija raciocinio ou diagnostico com base nas regras do texto."
    )
    resposta_raciocinio: str = Field(
        description="A resposta explicada e fundamentada no texto para a pergunta de raciocinio."
    )
    pergunta_fora_escopo: str = Field(
        description="Uma pergunta plausivel sobre medicina mas cuja resposta NAO esta no texto (para testar recusa)."
    )

def obter_modelo_disponivel():
    """
    Obtém automaticamente um modelo instalado no Ollama local.
    """
    try:
        modelos_resp = ollama.list()
        # Se for objeto com atributo 'models' ou dicionario
        if hasattr(modelos_resp, 'models'):
            lista = [m.model for m in modelos_resp.models]
        elif isinstance(modelos_resp, dict) and 'models' in modelos_resp:
            lista = [m['model'] for m in modelos_resp['models']]
        else:
            lista = []
            
        if lista:
            print(f"[*] Modelos Ollama encontrados: {lista}")
            # Priorizar qwen3.5:9b ou qwen2.5:7b se disponivel
            for pref in ["qwen3.5:9b", "qwen2.5:7b"]:
                if any(pref in m for m in lista):
                    return pref
            return lista[0]
    except Exception as e:
        print(f"[-] Aviso ao listar modelos: {e}")
    return "qwen3.5:9b"

def carregar_markdowns(diretorio: str = "my_notes"):
    """
    Carrega todos os arquivos Markdown do diretorio especificado.
    """
    arquivos = glob.glob(os.path.join(diretorio, "*.md"))
    documentos = []
    
    for arq in arquivos:
        with open(arq, "r", encoding="utf-8") as f:
            conteudo = f.read()
            nome_base = os.path.basename(arq)
            documentos.append({
                "fonte": nome_base,
                "conteudo": conteudo
            })
    return documentos

def gerar_perguntas_sinteticas_por_chunk(fonte: str, chunk_texto: str, model_name: str):
    """
    Gera variacoes sinteticas de QA (Simples, Raciocinio, Recusa) para um trecho de texto.
    """
    prompt = f"""
    Voce eh um gerador de datasets sinteticos de teste para RAG medico (Obstetricia e Ginecologia).
    Com base EXCLUSIVAMENTE no documento de referencia abaixo, crie um conjunto de perguntas e respostas realistas em portugues.

    [DOCUMENTO DE REFERENCIA ({fonte})]:
    {chunk_texto[:2500]}

    Gere:
    1. Uma pergunta simples e direta com sua resposta exata.
    2. Uma pergunta clinica complexa de raciocinio (diagnostico/conduta) com sua resposta explicada.
    3. Uma pergunta plausivel cuja resposta NAO esteja contida neste documento (para testar a taxa de recusa do RAG).
    """

    try:
        response = ollama.chat(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            format=SyntheticQA.model_json_schema()
        )
        dados = json.loads(response['message']['content'])
        return dados
    except Exception as e:
        print(f"[-] Aviso ao gerar para {fonte}: {e}")
        return None

def construir_testset_sintetico(diretorio_notes: str = "my_notes", max_documentos: int = 3):
    """
    Processa os arquivos Markdown e monta o Testset no formato de avaliacao RAG.
    """
    modelo = obter_modelo_disponivel()
    print(f"[*] Usando modelo Ollama: '{modelo}'")

    print(f"[*] Lendo arquivos Markdown em '{diretorio_notes}'...")
    docs = carregar_markdowns(diretorio_notes)
    print(f"[*] Total de documentos encontrados: {len(docs)}")

    dataset_sintetico = []

    # Processa ate max_documentos
    docs_para_processar = docs[:max_documentos]

    for idx, doc in enumerate(docs_para_processar, 1):
        fonte = doc["fonte"]
        conteudo = doc["conteudo"]
        print(f"[-] [{idx}/{len(docs_para_processar)}] Gerando perguntas sinteticas para '{fonte}'...")
        
        qa_sintetico = gerar_perguntas_sinteticas_por_chunk(fonte, conteudo, model_name=modelo)
        
        if qa_sintetico:
            # 1. Pergunta Simples
            dataset_sintetico.append({
                "fonte_documento": fonte,
                "evolution_type": "simple",
                "question": qa_sintetico["pergunta_simples"],
                "ground_truth": qa_sintetico["resposta_simples"],
                "context": conteudo[:1500],
                "expected_refusal": False
            })
            
            # 2. Pergunta de Raciocínio
            dataset_sintetico.append({
                "fonte_documento": fonte,
                "evolution_type": "reasoning",
                "question": qa_sintetico["pergunta_raciocinio"],
                "ground_truth": qa_sintetico["resposta_raciocinio"],
                "context": conteudo[:1500],
                "expected_refusal": False
            })
            
            # 3. Pergunta Fora do Escopo (Recusa)
            dataset_sintetico.append({
                "fonte_documento": fonte,
                "evolution_type": "unanswerable_refusal",
                "question": qa_sintetico["pergunta_fora_escopo"],
                "ground_truth": "Informacao nao disponivel nos documentos.",
                "context": conteudo[:1500],
                "expected_refusal": True
            })

    # Exportar para CSV e JSON
    df = pd.DataFrame(dataset_sintetico)
    
    csv_file = "testset_sintetico_tcc.csv"
    json_file = "testset_sintetico_tcc.json"
    
    df.to_csv(csv_file, index=False, encoding="utf-8-sig")
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(dataset_sintetico, f, ensure_ascii=False, indent=2)

    print("\n=======================================================")
    print("   TESTSET SINTETICO GERADO COM SUCESSO!")
    print("=======================================================")
    print(f"Total de pares (Pergunta/Resposta) gerados: {len(df)}")
    print(f"Categorias: Simple, Reasoning e Unanswerable (Recusa)")
    print(f"[OK] Arquivos salvos: '{csv_file}' e '{json_file}'")

if __name__ == "__main__":
    construir_testset_sintetico()
