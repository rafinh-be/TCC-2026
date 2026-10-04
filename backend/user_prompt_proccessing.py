"""
Módulo de Processamento de Prompts do Usuário e Comandos do Sistema.

Este módulo lida com a captura de mensagens do usuário (seja via CLI ou WebSocket),
mapeamento de comandos especiais iniciados com barra (ex: /clear, /reset) e finalização
de etapas do fluxo de conversa.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from functions import clear
import json

async def get_message(local=True, websocket: WebSocket = None):
    """
    Captura a mensagem do usuário dependendo do ambiente de execução.
    
    :param local: Se True, obtém entrada do terminal (CLI via input). Se False, aguarda via WebSocket.
    :param websocket: Instância da conexão WebSocket (usado se local=False).
    :return: String contendo a mensagem do usuário.
    """
    if (local):
        message = input("Digite sua mensagem: ")
        return message
    else:
        message = await websocket.receive_text()
        return message

# Dicionário de comandos reconhecidos pelo assistente
commands = {
    "0": "/clear",
    "1": "/reset",
}

# Dicionário mapeando os IDs de comandos para suas respectivas funções executáveis
functions = {
    "0": clear,
    "1": clear,
}

def get_command(message, verbose=False):
    """
    Verifica se a mensagem enviada pelo usuário contém um comando especial (ex: /clear).
    
    :param message: Texto digitado pelo usuário.
    :param verbose: Se True, exibe logs de depuração no terminal.
    :return: Chave do comando encontrado (ex: "0") ou string vazia caso nenhum comando seja detectado.
    """
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
    """
    Executa a função associada a um comando do sistema.
    
    :param execute: Chave do comando a ser executado.
    :param historico_conversas: Lista com o histórico atual da conversa (pode ser modificado pela função).
    :param verbose: Se True, exibe logs de depuração.
    :return: Retorno da função executada (ex: "continue").
    """
    result = functions.get(execute)(historico_conversas)
    if (verbose):
        print("Resultado da execução do comando:", result)    
    return result

async def complete_step(historico_conversa, message, answer, local=True, websocket: WebSocket = None):
    """
    Finaliza uma etapa do diálogo registrando a pergunta e a resposta no histórico
    e enviando os dados de volta ao cliente (terminal ou WebSocket).
    """
    historico_conversa.append({"role": "user", "content": message})
    historico_conversa.append({"role": "assistant", "content": answer})
    if (local):
        print(answer)
    else:
        await websocket.send_text(json.dumps({"user": message, "assistant": answer}, ensure_ascii=False))
    
    return