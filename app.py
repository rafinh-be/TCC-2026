# app.py
import sys
import json
import ollama
from buscador import buscar_contexto_expandido
from memoria import verificar_precisa_indexar
from indexador import indexar_repositorio

# Importa as ferramentas que criamos
import ferramentas

PROMPT_CRITICA = (
    "Você é um revisor médico sênior. Analise a RESPOSTA DO ASSISTENTE fornecida para a PERGUNTA DO USUÁRIO.\n"
    "Avalie se a mensagem do usuário necessita de uma resposta bem estruturada ou é apenas uma saudacao ou mensagem simples. Se for, nao critique a resposta"
    "Avalie se a resposta está clara, bem estruturada e se utilizou bem o CONTEXTO LOCAL fornecido.\n"
    "Identifique falhas, omissões ou pontos que podem ser melhorados.\n"
    "Lembre-se de que voce nao está falando com um médico, o usuário pode não entender termos técnicos, então clareza e explicação de termos técnicos são fundamentais.\n"
    "Responda APENAS com uma lista de pontos a melhorar ou diga 'PERFEITO' se não houver o que mudar. Não responda com a lista e com PERFEITO ao mesmo tempo"
)

PROMPT_REFINAMENTO = (
    "Você é um médico especialista. Com base na sua RESPOSTA ANTERIOR e na CRÍTICA recebida, "
    "reescreva a resposta final de forma aprimorada, corrigindo os pontos fracos apontados."
)

PROMPT_VALIDACAO_FERRAMENTA = (
    "Você é um auditor de integridade de sistemas de IA médica. Sua função é avaliar se a chamada de ferramenta (TOOL CALL) "
    "proposta pelo assistente é estritamente necessária e se cumpre INTEGRALMENTE todos os requisitos do usuário.\n\n"
    "Diretrizes de Avaliação:\n"
    "1. NECESSIDADE: O usuário ordenou explicitamente uma ação física (ex: criar, salvar, editar, adicionar)? Se for apenas uma dúvida teórica ou saudação, a ferramenta NÃO é necessária.\n"
    "2. COMPLETUDE: O conteúdo gerado dentro dos argumentos da ferramenta atende a tudo o que o usuário pediu? Se o usuário pediu para salvar um resumo e o conteúdo omitir dados críticos passados no contexto ou na pergunta, ela está incompleta.\n\n"
    "Responda EXCLUSIVAMENTE com um objeto JSON válido no formato abaixo, sem explicações adicionais fora do JSON:\n"
    "{\n"
    "  \"valido\": true ou false,\n"
    "  \"motivo\": \"Sua justificativa clara indicando se é desnecessário ou se faltou algo\"\n"
    "}"
)

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
            
            # Executa a chamada inicial passando o parâmetro 'tools'
            resposta = ollama.chat(
                model="qwen2.5:7b", 
                messages=mensagens_payload,
                tools=ferramentas.DEFINICAO_FERRAMENTAS
            )
            
            texto_resposta = resposta['message'].get('content', '')
            chamadas_ferramentas = resposta['message'].get('tool_calls', [])

            # 🔍 --- NOVA CAMADA DE VERIFICAÇÃO DE FERRAMENTAS (Necessidade e Completude) ---
            if chamadas_ferramentas:
                print(f"\n{YELLOW}🔍 Analisando necessidade e completude da ferramenta...{RESET}")
                
                payload_validacao = [
                    {"role": "system", "content": PROMPT_VALIDACAO_FERRAMENTA},
                    {"role": "user", "content": f"CONTEXTO LOCAL:\n{contexto}\n\nPERGUNTA DO USUÁRIO: {pergunta}\n\nCHAMADAS PROPOSTAS:\n{json.dumps(chamadas_ferramentas, ensure_ascii=False)}"}
                ]
                
                resposta_validacao = ollama.chat(model="qwen2.5:7b", messages=payload_validacao)
                conteudo_validacao = resposta_validacao['message'].get('content', '').strip()
                
                # Limpeza de blocos de código Markdown que o LLM possa ter gerado por vício
                if conteudo_validacao.startswith("```json"):
                    conteudo_validacao = conteudo_validacao.split("```json")[1].split("```")[0].strip()
                elif conteudo_validacao.startswith("```"):
                    conteudo_validacao = conteudo_validacao.split("```")[1].split("```")[0].strip()
                
                try:
                    dados_validacao = json.loads(conteudo_validacao)
                    ferramenta_valida = dados_validacao.get("valido", False)
                    motivo_validacao = dados_validacao.get("motivo", "Sem justificativa.")
                except Exception:
                    # Fallback de segurança caso o modelo falhe em responder JSON puro
                    ferramenta_valida = False
                    motivo_validacao = "Falha crítica na formatação do JSON de validação."

                if not ferramenta_valida:
                    print(f"  {YELLOW}✗ Ferramenta Recusada: {motivo_validacao}{RESET}")
                    print(f"{YELLOW}🔄 Forçando o agente a converter a intenção em texto convencional...{RESET}")
                    
                    # Esvazia a chamada de ferramenta para não executar o código físico do Python
                    chamadas_ferramentas = []
                    
                    # Alimenta o payload instruindo o modelo a responder estritamente via texto
                    mensagens_payload.append({
                        "role": "user", 
                        "content": f"Ação de ferramenta abortada. O sistema de auditoria recusou a chamada pelo motivo: '{motivo_validacao}'. Por favor, responda à minha pergunta anterior utilizando APENAS texto estruturado padrão, garantindo que responda a todas as minhas necessidades."
                    })
                    
                    resposta = ollama.chat(
                        model="qwen2.5:7b", 
                        messages=mensagens_payload,
                        tools=ferramentas.DEFINICAO_FERRAMENTAS
                    )
                    texto_resposta = resposta['message'].get('content', '')
                    chamadas_ferramentas = resposta['message'].get('tool_calls', []) # Verifica se ele não insistiu no erro
                else:
                    print(f"  {GREEN}✓ Ferramenta Aprovada: {motivo_validacao}{RESET}")

            # 🛠️ --- EXECUÇÃO FÍSICA DA FERRAMENTA (Caso aprovada ou corrigida) ---
            if chamadas_ferramentas:                
                for tool in chamadas_ferramentas:
                    nome_funcao = tool['function']['name']
                    argumentos = tool['function']['arguments']
                    
                    # Trava de Segurança contra Alucinações de nomes de funções
                    if nome_funcao not in ["criar_arquivo_markdown", "adicionar_conteudo_arquivo"]:
                        print(f"\n{YELLOW}⚙️ [Aviso]: O modelo tentou alucinar a ferramenta '{nome_funcao}'. Tratando como texto...{RESET}")
                        prompt_correcao = f"Você tentou chamar uma função inválida chamada {nome_funcao}. Responda apenas com texto comum."
                        mensagens_payload.append({"role": "user", "content": prompt_correcao})
                        resposta_segura = ollama.chat(model="qwen2.5:7b", messages=mensagens_payload)
                        texto_resposta = resposta_segura['message'].get('content', '')
                        print(texto_resposta)
                        break
                    
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
                # 🔄 INÍCIO DO LOOP DE APRIMORAMENTO (Cai aqui se nunca foi ferramenta OU se a ferramenta foi convertida em texto)
                print(f"\n{YELLOW}🔍 Revisando e aprimorando a resposta de texto...{RESET}")
                
                MAX_INTERACOES_REFINAMENTO = 3
                for i in range(MAX_INTERACOES_REFINAMENTO):
                    payload_critica = [
                        {"role": "system", "content": PROMPT_CRITICA},
                        {"role": "user", "content": f"CONTEXTO LOCAL:\n{contexto}\n\nPERGUNTA: {pergunta}\n\nRESPOSTA DO ASSISTENTE:\n{texto_resposta}"}
                    ]
                    
                    print(f"  ↳ Rodando análise de qualidade (Passo {i+1})...")
                    resposta_critica = ollama.chat(model="qwen2.5:7b", messages=payload_critica)
                    critica = resposta_critica['message'].get('content', '').strip()
                    
                    if "PERFEITO" in critica.upper() and len(critica) < 20:
                        print(f"  {GREEN}✓ Resposta aprovada na revisão!{RESET}")
                        break
                        
                    print(f"  {YELLOW}✗ Crítica recebida: {critica}{RESET}")
                    
                    payload_refinamento = [
                        {"role": "system", "content": f"{system_prompt}\n\nCONTEXTO LOCAL:\n{contexto}\n\n{PROMPT_REFINAMENTO}"},
                        {"role": "user", "content": f"PERGUNTA: {pergunta}\n\nRESPOSTA ANTERIOR:\n{texto_resposta}\n\nCRÍTICA:\n{critica}"}
                    ]
                    
                    print(f"  ↳ Aplicando melhorias...")
                    resposta_refinada = ollama.chat(model="qwen2.5:7b", messages=payload_refinamento)
                    texto_resposta = resposta_refinada['message'].get('content', '')

                print(f"\n{BOLD}🤖 Agente OBGYN (Resposta Final) > {RESET}", end="")
                print(texto_resposta)
            
            print("-" * 50 + "\n")
            
            # Atualiza histórico de memória de curto prazo
            historico_conversas.append({"user": pergunta, "assistant": texto_resposta})
            if len(historico_conversas) > 3: historico_conversas.pop(0)
            
        except KeyboardInterrupt:
            sys.exit(0)

if __name__ == "__main__":
    iniciar_terminal()