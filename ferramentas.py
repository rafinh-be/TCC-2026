# ferramentas.py
import os
from pathlib import Path


# --- Funções Python ---

def criar_arquivo_markdown(nome_arquivo: str, conteudo: str) -> str:
    """Cria um novo arquivo markdown em ./patient_notes."""
    if not nome_arquivo.endswith(".md"):
        nome_arquivo += ".md"
    pasta = Path("./patient_notes")
    pasta.mkdir(exist_ok=True)
    caminho_final = pasta / nome_arquivo
    with open(caminho_final, "w", encoding="utf-8") as f:
        f.write(conteudo)
    return f"Arquivo '{nome_arquivo}' criado em './patient_notes'."


def adicionar_conteudo_arquivo(nome_arquivo: str, conteudo_adicional: str) -> str:
    """Adiciona texto ao final de um arquivo markdown existente em ./my_notes."""
    if not nome_arquivo.endswith(".md"):
        nome_arquivo += ".md"
    caminho_final = Path("./my_notes") / nome_arquivo
    if not caminho_final.exists():
        return f"Erro: O arquivo '{nome_arquivo}' não existe em './my_notes'."
    with open(caminho_final, "a", encoding="utf-8") as f:
        f.write("\n\n" + conteudo_adicional)
    return f"Conteúdo adicionado ao arquivo '{nome_arquivo}'."


def salvar_memoria_paciente(tipo: str, conteudo: str) -> str:
    """Salva uma entrada persistente na memória do paciente (MEMORIA.md)."""
    tipos_validos = {"paciente", "preferencia", "historico", "encaminhamento"}
    if tipo not in tipos_validos:
        tipo = "paciente"

    pasta = Path("./patient_notes")
    pasta.mkdir(exist_ok=True)
    caminho = pasta / "MEMORIA.md"

    entrada = f"\n- [{tipo}] {conteudo}"
    with open(caminho, "a", encoding="utf-8") as f:
        f.write(entrada)

    return f"Memória salva (tipo: {tipo})."


# --- Definições de ferramentas para o Ollama ---
# As descrições explicam O QUE a função faz e quais argumentos aceita.
# A POLÍTICA de quando chamá-las está em config_agente.md (seção 2) — não é repetida aqui.

DEFINICAO_FERRAMENTAS = [
    {
        "type": "function",
        "function": {
            "name": "criar_arquivo_markdown",
            "description": "Cria um arquivo markdown físico em './patient_notes'. Use exclusivamente sob comando explícito do usuário.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nome_arquivo": {
                        "type": "string",
                        "description": "Nome do arquivo a ser criado (ex: 'resumo_paciente_maria.md')."
                    },
                    "conteudo": {
                        "type": "string",
                        "description": "Conteúdo completo em formato markdown a ser escrito no arquivo."
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
            "description": "Adiciona texto ao final de um arquivo markdown existente em './my_notes'. Use exclusivamente sob comando explícito do usuário.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nome_arquivo": {
                        "type": "string",
                        "description": "Nome do arquivo existente a ser editado (ex: 'pre_eclampsia.md')."
                    },
                    "conteudo_adicional": {
                        "type": "string",
                        "description": "Texto a ser adicionado ao final do arquivo."
                    }
                },
                "required": ["nome_arquivo", "conteudo_adicional"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "salvar_memoria_paciente",
            "description": "Salva uma informação persistente sobre o paciente em MEMORIA.md para uso em sessões futuras. Use quando o usuário revelar dados clínicos relevantes ou preferências.",
            "parameters": {
                "type": "object",
                "properties": {
                    "tipo": {
                        "type": "string",
                        "description": "Categoria da memória. Valores válidos: 'paciente' (dados clínicos), 'preferencia' (como o paciente prefere ser atendido), 'historico' (decisões de sessões anteriores), 'encaminhamento' (consultas ou referências mencionadas).",
                        "enum": ["paciente", "preferencia", "historico", "encaminhamento"]
                    },
                    "conteudo": {
                        "type": "string",
                        "description": "Fato declarado pelo usuário a ser salvo. Não salve respostas geradas pelo agente."
                    }
                },
                "required": ["tipo", "conteudo"]
            }
        }
    }
]
