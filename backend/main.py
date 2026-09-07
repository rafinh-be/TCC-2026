import configparser, sys, json, ollama, asyncio, uvicorn

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
    allow_origins=["http://localhost:3000"], # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws/chat")
async def start_agent(websocket: WebSocket):
    if needs_indexing():
        print("Updating LanceDB index...")
        index_data()
        
        
    #await websocket.accept()
    print("WebSocket connection established")
    
    contexto, fontes = "", []
    historico_conversa = []
    while True:
        try:
            # Recebe mensagem do usuario
            message = await get_message()
            # Verifica se foi digitado um comando e recebe o comando
            command = get_command(message)
            if command:
                # Executa o comando e envia a resposta para o usuario
                # Alguns comandos que "terminam" o processo devem usar 'continue' para nao encerrar o loop
                response = execute_command(command, historico_conversa)
                if (response == "continue"):
                    continue
                
            contexto_novo, fontes_novas = retrieve_context(message)
            if contexto_novo and contexto_novo not in contexto:
                contexto = (contexto + "\n\n---\n\n" + contexto_novo).strip()
            for fonte in fontes_novas:
                if fonte not in fontes:
                    fontes.append(fonte)

            payload = create_payload(historico_conversa, message, contexto, fontes)

            answer = chat_with_thought_limit(payload)
            
            await complete_step(historico_conversa, message, answer['message']['content'])
            
            print("Payload enviado para o modelo:\n", payload)
            print("\nResposta recebida pelo modelo:\n", answer)
                
            
        except KeyboardInterrupt:
            sys.exit(0)
        #except WebSocketDisconnect:
        #    print("WebSocket connection closed")
        #    break
                

if __name__ == "__main__":
    #uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
    asyncio.run(start_agent(websocket=None))  # For testing without WebSocket