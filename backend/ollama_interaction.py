import configparser, ollama

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

def create_payload(historico_conversa, message, contexto, agent_file="config_agent.md", citations=False):
    payload = []

    # Prompt inicial
    try:
        with open(agent_file, "r", encoding="utf-8") as f:
            prompt_sistema = f.read()
    except FileNotFoundError:
        prompt_sistema = config.get('prompts', 'prompt_sistema')
    
    payload.append({"role": "system", "content": prompt_sistema})    
    
    # Mensagens do historico
    for mensagem in historico_conversa:
        payload.append({"role": mensagem["role"], "content": mensagem["content"]})
    
    # Contexto
    if contexto:
        payload.append({"role": "system", "content": f"Contexto adicional: <contexto_local>{contexto}</contexto_local>"})
    else:
        payload.append({"role": "system", "content": f"Contexto adicional: <contexto_local>Não ha contexto local, responda apenas com a frase 'Não encontrei dados ou critérios suficientes para esta conduta específica na minha base local de evidências.'</contexto_local>"})
    
    if citations and contexto:
        payload.append({"role": "system", "content": config.get('prompts', 'prompt_citacoes')})
    
    # Mensagem nova
    payload.append({"role": "user", "content": message})

    return payload


FALLBACK_ATTEMPTS = 2


def plain_answer(response):
    message = {"role": "assistant", "content": response["message"]["content"]}
    thinking = response["message"].get("thinking")
    if (thinking):
        message["thinking"] = thinking
    return {"message": message}


def chat_with_thought_limit(payload, MAX_THINK_TOKENS=config.getint("model", "max_think_tokens", fallback=300), verbose=False, debug_model=False):
    messages = payload.copy()
    
    # Safely retrieve model name with explicit fallback syntax
    model_name = config.get("model", "model_test", fallback="qwen3.5:9b")
    
    if (debug_model):
        print("Starting model", model_name)
        
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
    
    if (stream['message']['content'].strip() == "" or stream["done_reason"] != 'stop'):
        if (verbose or debug_model):
            print("Loop detected. Fetching non-streaming final response...")
        
        accumulated_thought = stream['message'].get('thinking', '')
        if not accumulated_thought.startswith("<think>"):
            accumulated_thought = "<think>\n" + accumulated_thought
            
        forced_context = accumulated_thought.strip() + "\n</think>\n"
        if (debug_model):
            print("Final thought matrix before loop detection:\n", forced_context)
        
        answer_messages = payload.copy()
        answer_messages.append({'role': 'assistant', 'content': forced_context})
        answer_messages.append({'role': 'user', 'content': 'Dado o raciocinio do agente acima, continue a resposta e gere uma sintese com base na ultima mensagem do usuario, sistema e o raciocinio'})

        for attempt in range(FALLBACK_ATTEMPTS):
            final_response = ollama.chat(
                model=model_name,
                messages=answer_messages,
                options={"temperature": 0.6},
                stream=False,
                think=False,
            )
            if (final_response['message']['content'].strip()):
                break
            if (verbose or debug_model):
                print("Empty final response. Retrying..." if attempt < FALLBACK_ATTEMPTS - 1 else "Empty final response after retry.")
        
        final_response['message']['thinking'] = accumulated_thought
        return plain_answer(final_response)
    else:
        return plain_answer(stream)
    


chat = chat_with_thought_limit


def chat_stream(payload, verbose=False, debug_model=False):
    yield {"type": "answer", "answer": chat_with_thought_limit(payload, verbose=verbose, debug_model=debug_model)}
