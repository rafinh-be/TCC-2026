"""
Módulo de Interação com a LLM via Ollama.

Este módulo é responsável por:
1. Construir a estrutura de payload (mensagens do sistema, histórico da conversa, contexto RAG e nova mensagem).
2. Interagir com a API local do Ollama, lidando com modelos de raciocínio (Reasoning/Thinking)
   e aplicando fallback caso haja travamentos ou detecção de loops de geração.
"""

import configparser, ollama
from pathlib import Path

BASE_DIR = Path(__file__).parent


# Carrega as configurações do arquivo ini
config = configparser.ConfigParser()
config.read(BASE_DIR / 'config.ini', encoding='utf-8')

def create_payload(historico_conversa, message, contexto, fontes):
    """
    Constrói o payload no formato esperado pela API do Ollama (lista de mensagens com papeis).
    
    :param historico_conversa: Lista de dicionários contendo mensagens anteriores da conversa.
    :param message: Pergunta/mensagem atual enviada pelo usuário.
    :param contexto: Trechos de texto recuperados da base de dados local (LanceDB).
    :param fontes: Nomes dos arquivos de referência de onde o contexto foi extraído.
    :return: Lista de mensagens formatada para envio à LLM.
    """
    payload = []
    
    # 1. Carrega o prompt do sistema (prioriza config_agent.md se existir, senão usa config.ini)
    try:
        with open(BASE_DIR / "config_agent.md", "r", encoding="utf-8") as f:
            prompt_sistema = f.read()
    except FileNotFoundError:
        prompt_sistema = config.get('prompts', 'prompt_sistema')

    
    payload.append({"role": "system", "content": prompt_sistema})    
    
    # 2. Adiciona as mensagens anteriores do histórico da conversa
    for mensagem in historico_conversa:
        payload.append({"role": mensagem["role"], "content": mensagem["content"]})
    
    # 3. Injeta o contexto médico recuperado via RAG e as fontes de evidência
    if contexto:
        payload.append({"role": "system", "content": f"Contexto adicional: <contexto_local>{contexto}</contexto_local>"})
    else:
        payload.append({"role": "system", "content": f"Contexto adicional: <contexto_local>Não ha contexto local, responda apenas com a frase 'Não encontrei dados ou critérios suficientes para esta conduta específica na minha base local de evidências.'</contexto_local>"})
    if fontes:
        payload.append({"role": "system", "content": f"Fontes adicionais: {', '.join(fontes)}"})
    
    # 4. Adiciona a pergunta atual do usuário ao final do payload
    payload.append({"role": "user", "content": message})
    
    return payload


def chat_with_thought_limit(payload, MAX_THINK_TOKENS=300, verbose=False, debug_model=False):
    """
    Executa a chamada ao modelo no Ollama, controlando tokens de raciocínio (thinking/reasoning).
    
    Caso o modelo não encerre a resposta adequadamente ou entre em loop de pensamento, 
    esta função força o modelo a gerar a resposta final com base no raciocínio acumulado.
    
    :param payload: Lista de mensagens a enviar ao modelo.
    :param MAX_THINK_TOKENS: Limite máximo de tokens previstos.
    :param verbose: Se True, exibe informações detalhadas no terminal.
    :param debug_model: Se True, exibe logs de depuração do modelo LLM.
    :return: Dicionário com a resposta completa do modelo Ollama.
    """
    messages = payload.copy()
    
    # Obtém o nome do modelo configurado no config.ini (fallback padrão: qwen3.5:9b)
    model_name = config.get("model", "model_test", fallback="qwen3.5:9b")
    
    if (debug_model):
        print("Iniciando modelo Ollama:", model_name)
        
    # Primeira chamada ao Ollama
    stream = ollama.chat(
        model=model_name,
        messages=messages,
        options={
            "num_predict": MAX_THINK_TOKENS,
            "presence_penalty": 1.6, 
            "temperature": 0.6,
        },
        stream=False
    )
    
    # Tratamento para modelos com etapa de pensamento (thinking) que não concluíram a resposta final
    if (stream['message']['content'].strip() == "" or stream["done_reason"] != 'stop'):
        if (verbose or debug_model):
            print("Loop ou resposta incompleta detectada. Solicitando resposta final direta...")
        
        accumulated_thought = stream['message'].get('thinking', '')
        if not accumulated_thought.startswith("<think>"):
            accumulated_thought = "<think>\n" + accumulated_thought
            
        forced_context = accumulated_thought.strip() + "\n</think>\n"
        if (debug_model):
            print("Matriz de pensamento acumulada:\n", forced_context)
        
        # Cria novo histórico forçando a entrega da resposta conclusiva
        answer_messages = payload.copy()
        answer_messages.append({'role': 'assistant', 'content': forced_context})
        answer_messages.append({'role': 'user', 'content': 'Based on your reasoning above, provide your direct final answer now.'})

        final_response = ollama.chat(
            model=model_name,
            messages=answer_messages,
            options={"temperature": 0.6},
            stream=False,
            think=False,
        )
        
        final_response['message']['thinking'] = accumulated_thought
        return final_response
    else:
        return stream

    