from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from functions import clear
import json

async def get_message(local=True, websocket: WebSocket = None):
    if (local):
        message = input("Digite sua mensagem: ")
        return message
    else:
        message = await websocket.receive_text()
        return message

commands = {
    "0": "/clear",
    "1": "/reset",
}

functions = {
    "0": clear,
    "1": clear,
}

def get_command(message, verbose=False):
    execute = ""
    for key, value in commands.items():
        if (value in message):
            if (verbose):
                print("Comando encontrado:", value, "- Na mensagem:", message)
                print("Executando apenas o comando.")
            execute = key
            break
    
    return execute

def execute_command(execute, historico_conversas, verbose=False):
    result = functions.get(execute)(historico_conversas)
    if (verbose):
        print("Resultado da execução do comando:", result)    
    return result

async def complete_step(historico_conversa, message, answer, local=True, websocket: WebSocket = None):
    historico_conversa.append({"role": "user", "content": message})
    historico_conversa.append({"role": "assistant", "content": answer})
    if (local):
        print(answer)
    else:
        await websocket.send_text(json.dumps({"user": message, "assistant": answer}, ensure_ascii=False))
    
    return