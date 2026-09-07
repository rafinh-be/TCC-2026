import configparser, sys, json, ollama, asyncio, uvicorn, argparse

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel
from pathlib import Path

from database_utility import needs_indexing, index_data, retrieve_context

from ollama_interaction import create_payload, chat_with_thought_limit  
from user_prompt_proccessing import get_message, get_command, execute_command, complete_step

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

prompt_critica = config.get('prompts', 'prompt_critica')
prompt_refinamento = config.get('prompts', 'prompt_refinamento')
prompt_validacao_ferramenta = config.get('prompts', 'prompt_validacao_ferramenta')

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
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

@app.websocket("/ws/chat")
async def start_agent(websocket: WebSocket = None):
    global args
    local = args.local
    verbose = args.verbose
    debug_model = args.debug_model
    debug_rag = args.debug_rag
    
    if (not local):    
        await websocket.accept()
        print("WebSocket connection established")
        print(websocket)
        
    if needs_indexing((verbose or debug_rag)):
        if (verbose or debug_rag):
            print("Updating LanceDB index...")
        index_data((verbose or debug_rag))
    
    contexto, fontes = "", []
    historico_conversa = []
    while True:
        try:
            # Recebe mensagem do usuario
            message = await get_message(local, websocket)
            # Verifica se foi digitado um comando e recebe o comando
            command = get_command(message, verbose)
            if command:
                # Executa o comando e envia a resposta para o usuario
                # Alguns comandos que "terminam" o processo devem usar 'continue' para nao encerrar o loop
                response = execute_command(command, historico_conversa)
                if (response == "continue"):
                    continue
                
            contexto_novo, fontes_novas = retrieve_context(message, debug_rag)
            if contexto_novo and contexto_novo not in contexto:
                contexto = (contexto + "\n\n---\n\n" + contexto_novo).strip()
            for fonte in fontes_novas:
                if fonte not in fontes:
                    fontes.append(fonte)

            # Debatendo ainda se deveria passar contexto total ou apenas contexto novo. Nao decidi ainda. Vou deixar contexto total por enquanto
            payload = create_payload(historico_conversa, message, contexto, fontes)

            answer = chat_with_thought_limit(payload)
            
            await complete_step(historico_conversa, message, answer['message']['content'], local, websocket)
            
            if (verbose or debug_model):
                print("\n\nPayload sent to the model:\n", payload)
                print("\nPayload received by the model:\n", answer)
                
            
        except KeyboardInterrupt:
            if (verbose):
                print("Program finish triggered by KeyboardInterrupt")
            sys.exit(0)

        except Exception as e:
            if (not local):
                if (type(e) == WebSocketDisconnect):
                    print("WebSocket connection closed")
                    break
                

if __name__ == "__main__":
    if (not args.local):
        uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True, reload_excludes=["*.db", "*.sqlite", "lancedb/*", "*.lancedb"])
    else:
        asyncio.run(start_agent(websocket=None))  # For testing without WebSocket