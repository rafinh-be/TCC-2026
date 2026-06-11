# ferramentas.py
import os
from pathlib import Path

# --- 1. FUNÇÕES REAIS EM PYTHON ---

def criar_arquivo_markdown(nome_arquivo: str, conteudo: str) -> str:
    """Cria um novo arquivo markdown na pasta correspondente."""
    # Garante a extensão correta
    if not nome_arquivo.endswith(".md"):
        nome_arquivo += ".md"
        
    pasta = Path("./patient_notes")
    pasta.mkdir(exist_ok=True)
    
    caminho_final = pasta / nome_arquivo
    with open(caminho_final, "w", encoding="utf-8") as f:
        f.write(conteudo)
        
    return f"Sucesso: O arquivo '{nome_arquivo}' foi criado com sucesso em './patient_notes'."

def adicionar_conteudo_arquivo(nome_arquivo: str, conteudo_adicional: str) -> str:
    """Adiciona texto ao final de um arquivo markdown existente."""
    if not nome_arquivo.endswith(".md"):
        nome_arquivo += ".md"
        
    caminho_final = Path("./my_notes") / nome_arquivo
    
    if not caminho_final.exists():
        return f"Erro: O arquivo '{nome_arquivo}' não existe para ser editado."
        
    with open(caminho_final, "a", encoding="utf-8") as f:
        f.write("\n\n" + conteudo_adicional)
        
    return f"Sucesso: O conteúdo foi adicionado ao final do arquivo '{nome_arquivo}'."


# --- 2. MAPA DE ESPECIFICAÇÃO PARA O OLLAMA ---
# O modelo lê este dicionário para entender QUANDO e COMO chamar as funções.

DEFINICAO_FERRAMENTAS = [
    {
        "type": "function",
        "function": {
            "name": "criar_arquivo_markdown",
            "description": (
                "CRITICAL: USE APENAS quando o usuário der uma ordem explícita de criação, persistência ou salvamento de arquivos físicos no disco. "
                "PROIBIDO usar esta função se o usuário estiver apenas tirando dúvidas clínicas, fazendo perguntas teóricas ou pedindo explicações. "
                "Exemplo de uso correto: 'Salve essas informações em um arquivo chamado conduta.md'. "
                "Exemplo de uso ERRADO (NÃO USE AQUI): 'Quais são os critérios de diabetes gestacional?' -> Responda apenas com texto."
                ),
            "parameters": {
                "type": "object",
                "properties": {
                    "nome_arquivo": {
                        "type": "string",
                        "description": "O nome do arquivo a ser criado (ex: 'resumo_paciente_maria.md')."
                    },
                    "conteudo": {
                        "type": "string",
                        "description": "O conteúdo textual completo em formato markdown a ser escrito no arquivo."
                    }
                },
                "required": ["nome_arquivo", "conteudo"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "adicionar_conteudo_arquivo",
            "description": (
                "CRITICAL: USE APENas para atualizar, editar ou anexar novas informações ao final de um documento que já existe na base. "
                "NÃO USE se o usuário estiver apenas conversando ou fazendo perguntas sobre os dados. "
                "Exemplo de uso correto: 'Adicione a dose de ataque do sulfato de magnésio no arquivo de pré-eclâmpsia'."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "nome_arquivo": {
                        "type": "string",
                        "description": "O nome do arquivo markdown existente a ser editado (ex: 'pre_eclampsia.md')."
                    },
                    "conteudo_adicional": {
                        "type": "string",
                        "description": "O novo texto ou parágrafo médico que deve ser adicionado ao arquivo."
                    }
                },
                "required": ["nome_arquivo", "conteudo_adicional"]
            }
        }
    }
]