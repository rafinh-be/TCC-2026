# app.py
import sys
import json
from pathlib import Path

from pydantic import BaseModel
import ollama
from buscador import buscar_contexto_expandido
from memoria import verificar_precisa_indexar
from indexador import indexar_repositorio

import ferramentas

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio

# Fix 5: single constant — change the model in one place, not six
MODEL = "qwen2.5:7b"

# ---------------------------------------------------------------------------
# Prompts do pipeline interno de qualidade
# ---------------------------------------------------------------------------

# Fix 4: critério 1 agora embute a frase exata de segurança, para que o revisor
# saiba distinguir a resposta correta de recusa de uma resposta fraca.
PROMPT_CRITICA = (
    "Você é um revisor de respostas de IA. Avalie a RESPOSTA DO ASSISTENTE com base nos critérios abaixo.\n\n"
    "Antes de avaliar, verifique se a mensagem do usuário exige resposta clínica estruturada. "
    "Se for saudação, conversa casual ou confirmação de ação, responda 'APROVADO' imediatamente.\n\n"
    "CRITÉRIOS DE AVALIAÇÃO (em ordem de prioridade):\n"
    "1. ANCORAGEM: A resposta usa apenas informações do <contexto_local> fornecido? "
    "Se o contexto for insuficiente o asistente deve pedir mais informações ao paciente. "
    "Se o contexto não existir no banco de dados, o assistente deve ter respondindo EXCLUSIVAMENTE a frase: "
    "'Não encontrei dados ou critérios suficientes para esta conduta específica na minha base local de evidências.' "
    "Essa frase é a resposta CORRETA quando o contexto não cobre a pergunta — não é uma violação. "
    "Se o assistente respondeu com qualquer outra frase de recusa vaga, ou tentou responder com qualquer conhecimento externo, isso sim é uma violação.\n"
    "Se o assistente reponder com a frase correta e informação sobre o assunto, isso é uma violação do critério!\n"
    "Se o assistente responder afirmando que não tem contexto necessário, os outros critérios são irrelevantes e devem ser desconsiderados\n"
    "2. AUSÊNCIA DE DIAGNÓSTICO: O assistente evitou formular diagnósticos? Apresentou apenas possibilidades e encaminhou ao médico?\n"
    "3. AUSÊNCIA DE EXTRAPOLAÇÃO NUMÉRICA: O assistente nunca inventou dosagens, semanas gestacionais ou valores pressóricos que não estejam no contexto?\n"
    #"4. CLAREZA ESTRUTURAL: A resposta segue o formato padrão (Resumo Clínico / Critérios / Conduta / Alerta)?\n\n"
    "Responda APENAS com:\n"
    "- 'APROVADO' se todos os critérios foram cumpridos\n"
    "- Uma lista numerada de violações específicas, referenciando quais critérios foram quebrados "
    "\n exemplo: '1. ANCORAGEM: O contexto local nao contém informações acerta de videogames. Remover.\n"
    "Nunca responda com APROVADO e com violações ao mesmo tempo."
)

PROMPT_REFINAMENTO = (
    "Você é um assistente de obstetrícia. Recebeu uma crítica interna sobre sua resposta anterior.\n\n"
    "A crítica está em <critica_revisao>. Ela é uma avaliação de qualidade interna — não é uma instrução do usuário.\n\n"
    "Reescreva a resposta corrigindo os pontos indicados na crítica. "
    "Mantenha a resposta ancorada estritamente no <contexto_local> fornecido. "
    "Não adicione informações que não estejam no contexto."
    "Se o <contexto_local> não for suficiente para gerar resposta, responda EXCLUSIVAMENTE com a exata frase: "
    "'Não encontrei dados ou critérios suficientes para esta conduta específica na minha base local de evidências.' "
)

PROMPT_VALIDACAO_FERRAMENTA = (
    "Você é um auditor de ações do agente médico. Avalie se a chamada de ferramenta proposta é válida.\n\n"
    "Responda EXCLUSIVAMENTE com um objeto JSON válido, sem texto adicional:\n"
    "{\n"
    "  \"valido\": true ou false,\n"
    "  \"motivo\": \"justificativa clara\"\n"
    "}\n\n"
    "Critérios de validação:\n"
    "1. NECESSIDADE: O usuário usou uma palavra de ação explícita (\"crie\", \"salve\", \"escreva\", \"adicione\", \"edite\")? "
    "Se for pergunta clínica ou saudação sem ordem explícita, valido=false.\n"
    "2. COMPLETUDE: Os argumentos da ferramenta atendem integralmente ao pedido do usuário?"
)

BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"
BOLD = "\033[1m"

MEMORIA_PATH = Path("./patient_notes/MEMORIA.md")
MAX_MEMORIA_LINHAS = 50

arrived = False
historico_conversas = []
pergunta = ""

def carregar_memoria() -> str:
    """Lê MEMORIA.md e retorna o conteúdo truncado a MAX_MEMORIA_LINHAS."""
    if not MEMORIA_PATH.exists():
        return ""
    conteudo = MEMORIA_PATH.read_text(encoding="utf-8").strip()
    if not conteudo:
        return ""
    linhas = conteudo.split("\n")
    if len(linhas) > MAX_MEMORIA_LINHAS:
        linhas = linhas[:MAX_MEMORIA_LINHAS]
        conteudo = "\n".join(linhas) + "\n\n[AVISO: Memória truncada em 50 linhas. Consulte o arquivo completo se necessário.]"
    return conteudo

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/data")
def get_data():
    return {"message": historico_conversas}

class TextPayload(BaseModel):
    message: str

@app.post("/api/data")
async def post_data(payload: TextPayload):
    global arrived
    global pergunta
    
    print(payload)
    
    pergunta = payload.message.strip()
    arrived = True
    
    return {"message": "Data received successfully."}

@app.post("/api/")


@app.websocket("/ws/chat")
async def iniciar_terminal(websocket: WebSocket):
    print(f"{BOLD}{BLUE}==================================================")
    print("  AGENTE OBGYN AVANÇADO - OPERADOR DE FERRAMENTAS ")
    print(f"=================================================={RESET}")

    #global arrived
    #global historico_conversas
    #global pergunta
    
    await websocket.accept()
    print(f"{GREEN}Conexão WebSocket estabelecida com o frontend.{RESET}")
    
    if verificar_precisa_indexar():
        print(f"{YELLOW}⚠️ Atualizando LanceDB...{RESET}")
        indexar_repositorio()

    # Carrega system prompt estático — não é modificado por contexto ou memória
    try:
        with open("config_agente.md", "r", encoding="utf-8") as f:
            system_prompt = f.read()
    except FileNotFoundError:
        system_prompt = "Você é um médico especialista em obstetrícia."

    # Fix 8: memória carregada uma vez por sessão. Injetada diretamente na
    # mensagem do usuário como <aviso_sistema> — sem turno fake de assistant.
    memoria_sessao = carregar_memoria()

    print(f"\n{GREEN}Modo de Ferramentas Ativo!{RESET}")
    print("Você pode pedir coisas como: 'Crie um arquivo chamado resumo_caso.md com os dados...'")
    print("-" * 50)

    contexto, fontes = "", []
    while True:
        try:
            #pergunta = input(f"{BOLD}👤 Usuário > {RESET}").strip()
            pergunta = await websocket.receive_text()
            if not pergunta:
                continue
            if pergunta.lower() == '/sair':
                break

            contexto_novo, fontes_novas = buscar_contexto_expandido(pergunta)
            if contexto_novo and contexto_novo not in contexto:
                contexto = (contexto + "\n\n---\n\n" + contexto_novo).strip()
            for fonte in fontes_novas:
                if fonte not in fontes:
                    fontes.append(fonte)
            # --- Monta o payload base (system prompt estático + histórico) ---
            mensagens_payload = [{"role": "system", "content": system_prompt}]

            for interacao in historico_conversas:
                mensagens_payload.append({"role": "user", "content": interacao["user"]})
                mensagens_payload.append({"role": "assistant", "content": interacao["assistant"]})

            # Fix 8: memória injetada como aviso_sistema na mensagem atual do usuário,
            # não como um turno separado com resposta fabricada de assistant.
            prefixo_memoria = (
                f"<aviso_sistema>\n<memoria_paciente>\n{memoria_sessao}\n</memoria_paciente>\n</aviso_sistema>\n\n"
                if memoria_sessao else ""
            )

            # --- Caminho sem contexto local (saudações, perguntas gerais) ---
            if not contexto:
                mensagens_payload.append({
                    "role": "user",
                    "content": (
                        f"{prefixo_memoria}"
                        f"<aviso_sistema>Nenhum conteúdo relevante encontrado na base local para esta pergunta. "
                        f"Responda apenas informando o usuário que não encontrou informações sobre este assunto E NADA MAIS.</aviso_sistema>\n\n"
                        f"{pergunta}"
                    )
                })

                print(f"\n{BOLD}🤖 Agente OBGYN (Conversa Geral) > {RESET}", end="", flush=True)
                # Fix 7: ferramentas disponíveis também neste caminho. A política de
                # quando chamá-las já está em config_agente.md (seção 2, regra 5).
                resposta_geral = ollama.chat(
                    model=MODEL,
                    messages=mensagens_payload,
                    tools=ferramentas.DEFINICAO_FERRAMENTAS,
                )

                texto_resposta = resposta_geral['message'].get('content', '')

                print(f"\n{YELLOW}🔍 Revisando qualidade da resposta...{RESET}")

                MAX_REFINAMENTOS = 3

                for i in range(MAX_REFINAMENTOS):
                    payload_critica = [{"role": "system", "content": PROMPT_CRITICA}]
                    for interacao in historico_conversas:
                        payload_critica.append({"role": "user", "content": interacao["user"]})
                        payload_critica.append({"role": "assistant", "content": interacao["assistant"]})
                    payload_critica.append({"role": "user", "content": (
                        f"<contexto_local>\n{contexto}\n</contexto_local>\n\n"
                        f"PERGUNTA: {pergunta}\n\n"
                        f"RESPOSTA DO ASSISTENTE:\n{texto_resposta}"
                    )})

                    print(f"  ↳ Análise de qualidade (passo {i + 1})...")
                    resposta_critica = ollama.chat(model=MODEL, messages=payload_critica)
                    critica = resposta_critica['message'].get('content', '').strip()

                    if "APROVADO" in critica.upper():
                        print(f"  {GREEN}✓ Resposta aprovada.{RESET}")
                        break

                    print(f"  {YELLOW}✗ Crítica: {critica}{RESET}")

                    payload_refinamento = [{"role": "system", "content": f"{system_prompt}\n\n{PROMPT_REFINAMENTO}"}]
                    for interacao in historico_conversas:
                        payload_refinamento.append({"role": "user", "content": interacao["user"]})
                        payload_refinamento.append({"role": "assistant", "content": interacao["assistant"]})
                    payload_refinamento.append({"role": "user", "content": (
                        f"<contexto_local>\n{contexto}\n</contexto_local>\n\n"
                        f"PERGUNTA: {pergunta}\n\n"
                        f"RESPOSTA ANTERIOR:\n{texto_resposta}\n\n"
                        f"<critica_revisao>\n{critica}\n</critica_revisao>"
                    )})

                    print(f"  ↳ Aplicando melhorias...")
                    resposta_refinada = ollama.chat(model=MODEL, messages=payload_refinamento)
                    texto_resposta = resposta_refinada['message'].get('content', '')

                print(f"\n{BOLD}🤖 Agente OBGYN (Resposta Final) > {RESET}")
                print(texto_resposta)

                #print(texto_geral)
                print("-" * 50 + "\n")

                historico_conversas.append({"user": pergunta, "assistant": texto_resposta})
                
                await websocket.send_text(json.dumps({"user": pergunta, "assistant": texto_resposta}, ensure_ascii=False))

                if len(historico_conversas) > 10:
                    historico_conversas.pop(0)
                continue

            # --- Caminho com contexto local ---
            mensagens_payload.append({
                "role": "user",
                "content": (
                    f"{prefixo_memoria}"
                    f"<contexto_local>\n{contexto}\n</contexto_local>\n\n"
                    f"{pergunta}"
                )
            })

            print(f"\n{BOLD}🤖 Agente OBGYN > {RESET}", end="", flush=True)

            resposta = ollama.chat(
                model=MODEL,
                messages=mensagens_payload,
                tools=ferramentas.DEFINICAO_FERRAMENTAS
            )

            texto_resposta = resposta['message'].get('content', '')
            chamadas_ferramentas = resposta['message'].get('tool_calls', [])

            # --- Validação de chamadas de ferramenta ---
            if chamadas_ferramentas:
                print(f"\n{YELLOW}🔍 Validando necessidade e completude da ferramenta...{RESET}")

                payload_validacao = [{"role": "system", "content": PROMPT_VALIDACAO_FERRAMENTA}]
                for interacao in historico_conversas:
                    payload_validacao.append({"role": "user", "content": interacao["user"]})
                    payload_validacao.append({"role": "assistant", "content": interacao["assistant"]})
                payload_validacao.append({"role": "user", "content": (
                    f"<contexto_local>\n{contexto}\n</contexto_local>\n\n"
                    f"PERGUNTA DO USUÁRIO: {pergunta}\n\n"
                    f"CHAMADAS PROPOSTAS:\n{json.dumps(chamadas_ferramentas, ensure_ascii=False)}"
                )})

                resposta_validacao = ollama.chat(model=MODEL, messages=payload_validacao)
                conteudo_validacao = resposta_validacao['message'].get('content', '').strip()

                if conteudo_validacao.startswith("```json"):
                    conteudo_validacao = conteudo_validacao.split("```json")[1].split("```")[0].strip()
                elif conteudo_validacao.startswith("```"):
                    conteudo_validacao = conteudo_validacao.split("```")[1].split("```")[0].strip()

                try:
                    dados_validacao = json.loads(conteudo_validacao)
                    ferramenta_valida = dados_validacao.get("valido", False)
                    motivo_validacao = dados_validacao.get("motivo", "Sem justificativa.")
                except Exception:
                    ferramenta_valida = False
                    motivo_validacao = "Falha na formatação do JSON de validação."

                if not ferramenta_valida:
                    print(f"  {YELLOW}✗ Ferramenta Recusada: {motivo_validacao}{RESET}")
                    print(f"{YELLOW}🔄 Convertendo intenção em resposta de texto...{RESET}")

                    chamadas_ferramentas = []
                    mensagens_payload.append({
                        "role": "user",
                        "content": (
                            f"<aviso_sistema>Ação de ferramenta abortada. Motivo: '{motivo_validacao}'. "
                            f"Responda à pergunta anterior utilizando APENAS texto estruturado padrão.</aviso_sistema>"
                        )
                    })

                    # Retry sem tools= — modelo não pode retornar tool calls neste passo.
                    # chamadas_ferramentas zerado incondicionalmente: qualquer call aqui
                    # não passou pelo validador e não deve ser executado.
                    resposta = ollama.chat(model=MODEL, messages=mensagens_payload)
                    texto_resposta = resposta['message'].get('content', '')
                    chamadas_ferramentas = []
                else:
                    print(f"  {GREEN}✓ Ferramenta Aprovada: {motivo_validacao}{RESET}")

            # --- Execução física das ferramentas aprovadas ---
            if chamadas_ferramentas:
                resultados_execucao = []

                for tool in chamadas_ferramentas:
                    nome_funcao = tool['function']['name']
                    argumentos = tool['function']['arguments']
                    resultado_acao = ""

                    funcoes_validas = {"criar_arquivo_markdown", "adicionar_conteudo_arquivo", "salvar_memoria_paciente"}
                    if nome_funcao not in funcoes_validas:
                        print(f"\n{YELLOW}⚙️ [Aviso]: Função inválida '{nome_funcao}'. Tratando como texto...{RESET}")
                        mensagens_payload.append({
                            "role": "user",
                            "content": f"<aviso_sistema>Função inválida '{nome_funcao}' bloqueada. Responda apenas com texto.</aviso_sistema>"
                        })
                        resposta_segura = ollama.chat(model=MODEL, messages=mensagens_payload)
                        texto_resposta = resposta_segura['message'].get('content', '')
                        print(texto_resposta)
                        break

                    print(f"\n{YELLOW}⚙️ [Ação do Agente]: Executando '{nome_funcao}'...{RESET}")

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
                    elif nome_funcao == "salvar_memoria_paciente":
                        resultado_acao = ferramentas.salvar_memoria_paciente(
                            tipo=argumentos['tipo'],
                            conteudo=argumentos['conteudo']
                        )
                        memoria_sessao = carregar_memoria()

                    print(f"{GREEN}➔ {resultado_acao}{RESET}")

                    # Fix 3: inclui nome da função E argumentos-chave no registro,
                    # para que o histórico permita ao modelo raciocinar sobre o que
                    # foi feito em turnos posteriores (ex: "adicione nesse arquivo").
                    arg_resumo = ", ".join(
                        f"{k}={str(v)[:50]}{'...' if len(str(v)) > 50 else ''}"
                        for k, v in argumentos.items()
                        if k != "conteudo"  # conteúdo completo omitido para não inflar o histórico
                    )
                    resultados_execucao.append(f"[{nome_funcao}({arg_resumo})]: {resultado_acao}")

                if resultados_execucao:
                    texto_resposta = "Ações executadas:\n" + "\n".join(resultados_execucao)

            else:
                # --- Loop de refinamento para respostas de texto ---
                print(f"\n{YELLOW}🔍 Revisando qualidade da resposta...{RESET}")

                MAX_REFINAMENTOS = 3

                for i in range(MAX_REFINAMENTOS):
                    payload_critica = [{"role": "system", "content": PROMPT_CRITICA}]
                    for interacao in historico_conversas:
                        payload_critica.append({"role": "user", "content": interacao["user"]})
                        payload_critica.append({"role": "assistant", "content": interacao["assistant"]})
                    payload_critica.append({"role": "user", "content": (
                        f"<contexto_local>\n{contexto}\n</contexto_local>\n\n"
                        f"PERGUNTA: {pergunta}\n\n"
                        f"RESPOSTA DO ASSISTENTE:\n{texto_resposta}"
                    )})

                    print(f"  ↳ Análise de qualidade (passo {i + 1})...")
                    resposta_critica = ollama.chat(model=MODEL, messages=payload_critica)
                    critica = resposta_critica['message'].get('content', '').strip()

                    if "APROVADO" in critica.upper():
                        print(f"  {GREEN}✓ Resposta aprovada.{RESET}")
                        break

                    print(f"  {YELLOW} Resposta: {texto_resposta}")
                    print(f"  {YELLOW}✗ Crítica: {critica}{RESET}")

                    payload_refinamento = [{"role": "system", "content": f"{system_prompt}\n\n{PROMPT_REFINAMENTO}"}]
                    for interacao in historico_conversas:
                        payload_refinamento.append({"role": "user", "content": interacao["user"]})
                        payload_refinamento.append({"role": "assistant", "content": interacao["assistant"]})
                    payload_refinamento.append({"role": "user", "content": (
                        f"<contexto_local>\n{contexto}\n</contexto_local>\n\n"
                        f"PERGUNTA: {pergunta}\n\n"
                        f"RESPOSTA ANTERIOR:\n{texto_resposta}\n\n"
                        f"<critica_revisao>\n{critica}\n</critica_revisao>"
                    )})

                    print(f"  ↳ Aplicando melhorias...")
                    resposta_refinada = ollama.chat(model=MODEL, messages=payload_refinamento)
                    texto_resposta = resposta_refinada['message'].get('content', '')

                print(f"\n{BOLD}🤖 Agente OBGYN (Resposta Final) > {RESET}")
                print(texto_resposta)

            # Fix 6: exibe as fontes consultadas para transparência clínica
            if fontes:
                print(f"\n{BLUE}📚 Fontes: {', '.join(fontes)}{RESET}")

            print("-" * 50 + "\n")

            historico_conversas.append({"user": pergunta, "assistant": texto_resposta})
            
            # ENVIAR MENSAGEM AQUI EU ACHO
            await websocket.send_text(json.dumps({"user": pergunta, "assistant": texto_resposta}, ensure_ascii=False))
            
            if len(historico_conversas) > 10:
                historico_conversas.pop(0)


        except KeyboardInterrupt:
            sys.exit(0)
            
        except WebSocketDisconnect:
            print(f"{YELLOW}⚠️ Conexão WebSocket encerrada pelo frontend.{RESET}")
            break

#if __name__ == "__main__":    
    #print("oi!@")
 #   iniciar_terminal()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
    iniciar_terminal()