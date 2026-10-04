"""
Servidor Backend Principal (FastAPI) - Sistema RAG para Obstetrícia e Ginecologia.

Este arquivo é o ponto de entrada da aplicação backend. Ele configura a API FastAPI,
os middlewares de CORS, define endpoints REST e WebSocket, gerencia o fluxo de processamento 
das mensagens (RAG + Ollama) e permite execução via CLI local para testes rápidos.
"""

import configparser, sys, json, ollama, asyncio, uvicorn, argparse

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel
from pathlib import Path

from database_utility import needs_indexing, index_data, retrieve_context
from ollama_interaction import create_payload, chat_with_thought_limit  
from user_prompt_proccessing import get_command, execute_command

# -----------------------------------------------------------------------------
# Carregamento de Configurações
# -----------------------------------------------------------------------------
config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

# Leitura de prompts estruturados do arquivo de configuração
prompt_critica = config.get('prompts', 'prompt_critica')
prompt_refinamento = config.get('prompts', 'prompt_refinamento')
prompt_validacao_ferramenta = config.get('prompts', 'prompt_validacao_ferramenta')

# -----------------------------------------------------------------------------
# Inicialização do FastAPI e Configuração de CORS
# -----------------------------------------------------------------------------
app = FastAPI(
    title="Agente Obstétrico - Backend API",
    description="API para atendimento médico assistido por IA com RAG em Obstetrícia e Ginecologia.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8501", "*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------------------------
# Configuração de Argumentos da Linha de Comando (CLI)
# -----------------------------------------------------------------------------
parser = argparse.ArgumentParser("main")
parser.add_argument("-v", "--verbose", action="store_true", help="Ativa saída detalhada para depuração geral")
parser.add_argument("--debug_rag", action="store_true", help="Ativa logs detalhados para as etapas do RAG (vetores e busca)")
parser.add_argument("--debug_model", action="store_true", help="Ativa logs detalhados do payload e resposta da LLM")
parser.add_argument("--local", action="store_true", help="Executa o agente em modo CLI interativo para testes no terminal")
args = parser.parse_args()


# -----------------------------------------------------------------------------
# Modelos de Dados Pydantic para Requisições e Respostas HTTP
# -----------------------------------------------------------------------------
class ChatRequest(BaseModel):
    """Modelo para payload recebido na rota HTTP /api/chat."""
    message: str
    historico_conversa: list[dict] = []


class ChatResponse(BaseModel):
    """Modelo para resposta enviada pela rota HTTP /api/chat."""
    user: str
    assistant: str
    historico_conversa: list[dict]


# -----------------------------------------------------------------------------
# Lógica Principal do Chat (Pipeline RAG + LLM)
# -----------------------------------------------------------------------------
def process_chat(message: str, historico_conversa: list, verbose: bool = False, debug_rag: bool = False, debug_model: bool = False) -> dict:
    """
    Processa uma mensagem do usuário dentro do pipeline RAG.
    
    Etapas:
    1. Verifica se a base de dados em vetores (LanceDB) precisa de reindexação.
    2. Verifica se a mensagem é um comando do sistema (ex: /clear ou /reset).
    3. Busca contexto relevante e fontes na base de conhecimentos local (LanceDB).
    4. Monta o payload estruturado e chama a LLM via Ollama com limite de raciocínio.
    5. Atualiza o histórico da conversa e retorna o dicionário com os resultados.
    """
    # Step 1: Atualização automática da base de vetores se houver alterações nos Markdowns
    if needs_indexing((verbose or debug_rag)):
        if (verbose or debug_rag):
            print("Atualizando índice no LanceDB...")
        index_data((verbose or debug_rag))
    
    contexto, fontes = "", []
    
    # Step 2: Verificação e execução de comandos especiais (ex: /clear)
    command = get_command(message, verbose)
    if command:
        response = execute_command(command, historico_conversa)
        if response == "continue":
            return {
                "user": message,
                "assistant": "Comando executado com sucesso.",
                "historico_conversa": historico_conversa
            }

    # Step 3: Recuperação de contexto relevante na base híbrida
    contexto_novo, fontes_novas = retrieve_context(message, debug_rag)
    if contexto_novo and contexto_novo not in contexto:
        contexto = (contexto + "\n\n---\n\n" + contexto_novo).strip()
    for fonte in fontes_novas:
        if fonte not in fontes:
            fontes.append(fonte)

    # Step 4: Montagem do payload e chamada da LLM via Ollama
    payload = create_payload(historico_conversa, message, contexto, fontes)
    answer = chat_with_thought_limit(payload)
    assistant_reply = answer['message']['content']

    # Step 5: Atualização do histórico da conversa
    historico_conversa.append({"role": "user", "content": message})
    historico_conversa.append({"role": "assistant", "content": assistant_reply})

    if (verbose or debug_model):
        print("\n\nPayload enviado para o modelo:\n", payload)
        print("\nResposta recebida do modelo:\n", answer)

    return {
        "user": message,
        "assistant": assistant_reply,
        "historico_conversa": historico_conversa
    }


# -----------------------------------------------------------------------------
# Endpoint WebSocket para Comunicação em Tempo Real
# -----------------------------------------------------------------------------
@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """
    Endpoint WebSocket em /ws/chat.
    Permite comunicação bidirecional contínua com a interface (Streamlit / Frontend).
    """
    await websocket.accept()
    print("Conexão WebSocket estabelecida.")
    historico_conversa = []
    try:
        while True:
            # Recebe payload em texto/JSON enviado pelo cliente
            data_raw = await websocket.receive_text()
            if not data_raw:
                continue

            # Decodifica JSON com suporte a histórico existente
            try:
                data = json.loads(data_raw)
                message = data.get("message", "")
                if "historico_conversa" in data and isinstance(data["historico_conversa"], list):
                    historico_conversa = data["historico_conversa"]
            except Exception:
                message = data_raw

            if not message.strip():
                continue

            # Processa o chat pelo pipeline RAG
            result = process_chat(
                message=message,
                historico_conversa=historico_conversa,
                verbose=args.verbose,
                debug_rag=args.debug_rag,
                debug_model=args.debug_model
            )
            historico_conversa = result["historico_conversa"]

            # Envia a resposta de volta ao cliente via WebSocket
            await websocket.send_text(json.dumps(result, ensure_ascii=False))

    except WebSocketDisconnect:
        print("Conexão WebSocket encerrada pelo cliente.")
    except Exception as e:
        print(f"Erro no WebSocket: {e}")


# -----------------------------------------------------------------------------
# Endpoint REST (HTTP POST)
# -----------------------------------------------------------------------------
@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Endpoint REST padrão para receber uma mensagem e retornar a resposta do assistente."""
    try:
        result = process_chat(
            message=request.message,
            historico_conversa=request.historico_conversa,
            verbose=args.verbose,
            debug_rag=args.debug_rag,
            debug_model=args.debug_model
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------------------------------------------------------------
# Execução CLI em Modo Local
# -----------------------------------------------------------------------------
def run_local_agent():
    """Modo CLI interativo para testar o agente diretamente no terminal."""
    print("Iniciando agente em modo local (CLI)...")
    historico_conversa = []
    while True:
        try:
            message = input("\nDigite sua mensagem: ")
            if not message.strip():
                continue
            res = process_chat(
                message=message,
                historico_conversa=historico_conversa,
                verbose=args.verbose,
                debug_rag=args.debug_rag,
                debug_model=args.debug_model
            )
            historico_conversa = res["historico_conversa"]
            print(f"\nAssistente: {res['assistant']}")
        except KeyboardInterrupt:
            print("\nEncerrando agente local.")
            sys.exit(0)
        except Exception as e:
            print(f"Erro: {e}")


# -----------------------------------------------------------------------------
# Ponto de Entrada do Script
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    if (not args.local):
        # Inicia servidor web com Uvicorn
        uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True, reload_excludes=["*.db", "*.sqlite", "lancedb/*", "*.lancedb"])
    else:
        # Executa via terminal
        run_local_agent()


