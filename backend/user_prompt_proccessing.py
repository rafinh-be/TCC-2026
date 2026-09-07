from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from functions import clear

async def get_message(local=True, websocket: WebSocket = None):
    if (local):
        message = input("Digite sua mensagem: ")
        return message
    else:
        message = await websocket.accept()
        return message

commands = {
    "0": "/clear",
    "1": "/reset",
}

functions = {
    "0": clear,
    "1": clear,
}

def get_command(message):
    execute = ""
    for key, value in commands.items():
        if (value in message):
            execute = key
            break
    
    return execute

def execute_command(execute, historico_conversas):
    result = functions.get(execute)(historico_conversas)
        
    return result

def complete_step(historico_conversa, message, answer):
    historico_conversa.append({"role": "user", "content": message})
    historico_conversa.append({"role": "assistant", "content": answer})
    
    return