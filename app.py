# app.py
import sys
import json
import ollama
from buscador import buscar_contexto_expandido
from memoria import verificar_precisa_indexar
from indexador import indexar_repositorio

# Importa as ferramentas que criamos
import ferramentas

BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"
BOLD = "\033[1m"

def iniciar_terminal():
    print(f"{BOLD}{BLUE}==================================================")
    print("  AGENTE OBGYN AVANÇADO - OPERADOR DE FERRAMENTAS ")
    print(f"=================================================={RESET}")
    
    # Sincronização automática
    if verificar_precisa_indexar():
        print(f"{YELLOW}⚠️ Atualizando LanceDB...{RESET}")
        indexar_repositorio()
    
    historico_conversas = []
    
    try:
        with open("config_agente.md", "r", encoding="utf-8") as f:
            system_prompt = f.read()
    except FileNotFoundError:
        system_prompt = "Você é um médico especialista."

    print(f"\n{GREEN}Modo de Ferramentas Ativo!{RESET}")
    print("Você pode pedir coisas como: 'Crie um arquivo chamado resumo_caso.md com os dados...'")
    print("-" * 50)

    while True:
        try:
            pergunta = input(f"{BOLD}👤 Usuário > {RESET}").strip()
            if not pergunta: continue
            if pergunta.lower() == '/sair': break

            contexto, fontes = buscar_contexto_expandido(pergunta)
            
            if not contexto:
                # 💡 EM VEZ DE TRAVAR O PROGRAMA, apenas avisa que vai responder sem usar o banco de dados local
                instrucao_sistema = f"{system_prompt}\n\nNota: O usuário fez uma pergunta geral ou saudação. Responda apenas com texto comum de forma educada, sem inventar dados médicos ou ferramentas."
                
                payload_atual = [{"role": "system", "content": instrucao_sistema}]
                for msg in historico_conversas:
                    if msg["role"] != "system": payload_atual.append(msg)
                payload_atual.append({"role": "user", "content": pergunta})
                
                print(f"\n{BOLD}🤖 Agente OBGYN (Conversa Geral) > {RESET}", end="", flush=True)
                resposta_geral = ollama.chat(model="qwen2.5:7b", messages=payload_atual)
                print(resposta_geral['message'].get('content', ''))
                print("-" * 50 + "\n")
                
                # Salva no histórico e pula para a próxima pergunta
                historico_conversas.append({"role": "user", "content": pergunta})
                historico_conversas.append(resposta_geral['message'])
                continue
            
            instrucao_sistema = f"{system_prompt}\n\nAlém de responder perguntas, você tem acesso a ferramentas para criar e editar arquivos caso o usuário ordene explicitamente.\nCONTEXTO LOCAL:\n{contexto}"
            
            mensagens_payload = [{"role": "system", "content": instrucao_sistema}]
            for interacao in historico_conversas:
                mensagens_payload.append({"role": "user", "content": interacao["user"]})
                mensagens_payload.append({"role": "assistant", "content": interacao["assistant"]})
            mensagens_payload.append({"role": "user", "content": pergunta})

            print(f"\n{BOLD}🤖 Agente OBGYN > {RESET}", end="", flush=True)
            
            # Executa a chamada passando o parâmetro 'tools'
            resposta = ollama.chat(
                model="qwen2.5:7b", 
                messages=mensagens_payload,
                tools=ferramentas.DEFINICAO_FERRAMENTAS
            )
            
            texto_resposta = resposta['message'].get('content', '')
            chamadas_ferramentas = resposta['message'].get('tool_calls', [])

            # SE O MODELO DECIDIR CHAMAR UMA FERRAMENTA:
            if chamadas_ferramentas:
                for tool in chamadas_ferramentas:
                    nome_funcao = tool['function']['name']
                    argumentos = tool['function']['arguments']
                    
                    # 🛡️ TRAVA DE SEGURANÇA: Verifica se a ferramenta realmente existe
                    if nome_funcao not in ["criar_arquivo_markdown", "adicionar_conteudo_arquivo"]:
                        print(f"\n{YELLOW}⚙️ [Aviso]: O modelo tentou alucinar a ferramenta '{nome_funcao}'. Tratando como texto comum...{RESET}")
                        
                        # Força o modelo a responder normalmente convertendo a intenção em texto
                        prompt_correcao = f"Você tentou chamar uma função inválida chamada {nome_funcao}. Por favor, responda à minha pergunta anterior apenas com texto normal, sem usar ferramentas."
                        mensagens_payload.append({"role": "user", "content": prompt_correcao})
                        
                        resposta_segura = ollama.chat(model="llama3.2:3b", messages=mensagens_payload)
                        texto_resposta = resposta_segura['message'].get('content', '')
                        print(texto_resposta)
                        break
                    
                    # Se for uma ferramenta real, segue o fluxo normal
                    print(chamadas_ferramentas)
                    print(f"\n{YELLOW}⚙️ [Ação do Agente]: Executando ferramenta '{nome_funcao}'...{RESET}")
                    
                    if nome_funcao == "criar_arquivo_markdown":
                        resultado_acao = ferramentas.criar_arquivo_markdown(
                            nome_arquivo=argumentos['nome_arquivo'],
                            conteudo=argumentos['conteudo']
                        )
                    elif nome_funcao == "adicionar_conteudo_arquivo":
                        resultado_acao = ferramentas.adicionar_conteudo_arquivo(
                            nome_arquivo=argumentos['nome_arquivo'],
                            conteudo_adicional=argumentos['conteudo_adicional']
                        )
                        
                    print(f"{GREEN}➔ {resultado_acao}{RESET}")
                    texto_resposta = f"Entendido. Executei a ferramenta para você. {resultado_acao}"

            else:
                # Fluxo normal de texto se nenhuma ferramenta foi chamada
                print(texto_resposta)
                if fontes:
                    print(f"\n{BLUE}📂 Evidências extraídas de: {', '.join(fontes)}{RESET}")
            
            print("-" * 50 + "\n")
            
            # Atualiza histórico de memória de curto prazo
            historico_conversas.append({"user": pergunta, "assistant": texto_resposta})
            if len(historico_conversas) > 3: historico_conversas.pop(0)
            
        except KeyboardInterrupt:
            sys.exit(0)

if __name__ == "__main__":
    iniciar_terminal()