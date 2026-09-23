import configparser, sys, json, ollama, asyncio, uvicorn, argparse

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel
from pathlib import Path

from database_utility import needs_indexing, index_data, retrieve_context
from ollama_interaction import create_payload, chat_with_thought_limit  
from user_prompt_proccessing import get_command, execute_command

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

prompt_critica = config.get('prompts', 'prompt_critica')
prompt_refinamento = config.get('prompts', 'prompt_refinamento')
prompt_validacao_ferramenta = config.get('prompts', 'prompt_validacao_ferramenta')

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8501", "*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

parser = argparse.ArgumentParser("main")
parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output for debugging")
parser.add_argument("--debug_rag", action="store_true", help="Enables extra verbose output for the RAG sections of the code")
parser.add_argument("--debug_model", action="store_true", help="Enables extra verbose output for the LLM Model processing sections of the code")
parser.add_argument("--local", action="store_true", help="Outputs program to CLI for quick testing")
args = parser.parse_args()


class ChatRequest(BaseModel):
    message: str
    historico_conversa: list[dict] = []


class ChatResponse(BaseModel):
    user: str
    assistant: str
    historico_conversa: list[dict]


def process_chat(message: str, historico_conversa: list, verbose: bool = False, debug_rag: bool = False, debug_model: bool = False) -> dict:
    if needs_indexing((verbose or debug_rag)):
        if (verbose or debug_rag):
            print("Updating LanceDB index...")
        index_data((verbose or debug_rag))
    
    contexto, fontes = "", []
    
    command = get_command(message, verbose)
    if command:
        response = execute_command(command, historico_conversa)
        if response == "continue":
            return {
                "user": message,
                "assistant": "Comando executado com sucesso.",
                "historico_conversa": historico_conversa
            }

    contexto_novo, fontes_novas = retrieve_context(message, debug_rag)
    if contexto_novo and contexto_novo not in contexto:
        contexto = (contexto + "\n\n---\n\n" + contexto_novo).strip()
    for fonte in fontes_novas:
        if fonte not in fontes:
            fontes.append(fonte)

    payload = create_payload(historico_conversa, message, contexto, fontes)
    answer = chat_with_thought_limit(payload)
    assistant_reply = answer['message']['content']

    historico_conversa.append({"role": "user", "content": message})
    historico_conversa.append({"role": "assistant", "content": assistant_reply})

    if (verbose or debug_model):
        print("\n\nPayload sent to the model:\n", payload)
        print("\nPayload received by the model:\n", answer)

    return {
        "user": message,
        "assistant": assistant_reply,
        "historico_conversa": historico_conversa
    }


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    print("Conexão WebSocket estabelecida.")
    historico_conversa = []
    try:
        while True:
            data_raw = await websocket.receive_text()
            if not data_raw:
                continue

            try:
                data = json.loads(data_raw)
                message = data.get("message", "")
                if "historico_conversa" in data and isinstance(data["historico_conversa"], list):
                    historico_conversa = data["historico_conversa"]
            except Exception:
                message = data_raw

            if not message.strip():
                continue

            result = process_chat(
                message=message,
                historico_conversa=historico_conversa,
                verbose=args.verbose,
                debug_rag=args.debug_rag,
                debug_model=args.debug_model
            )
            historico_conversa = result["historico_conversa"]

            await websocket.send_text(json.dumps(result, ensure_ascii=False))

    except WebSocketDisconnect:
        print("Conexão WebSocket encerrada pelo cliente.")
    except Exception as e:
        print(f"Erro no WebSocket: {e}")


@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
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


def run_local_agent():
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


if __name__ == "__main__":
    if (not args.local):
        uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True, reload_excludes=["*.db", "*.sqlite", "lancedb/*", "*.lancedb"])
    else:
        run_local_agent()
