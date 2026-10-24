import configparser, sys, json, os, ollama, asyncio, uvicorn, argparse

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel
from pathlib import Path

from database_utility import needs_indexing, index_data, retrieve_context, fetch_chunks, merge_chunks, format_context, embed_sources, load_documents

from documents_logic import summarize, find_by_id
from ollama_interaction import create_payload
from attribution_logic import split_sentences, similar_chunks, extract_citations, cited_chunks, intersect_chunks
import providers
from user_prompt_proccessing import get_message, get_command, execute_command, complete_step

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

prompt_critica = config.get('prompts', 'prompt_critica')
prompt_refinamento = config.get('prompts', 'prompt_refinamento')
prompt_validacao_ferramenta = config.get('prompts', 'prompt_validacao_ferramenta')
frase_sem_dados = config.get('prompts_termino', 'prompt_restricao_1')

allowed_origins = [origin.strip() for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",") if origin.strip()]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

parser = argparse.ArgumentParser("main")
parser.add_argument("--provider", required=True, choices=providers.PROVIDERS, help="LLM provider used for chat")
parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output for debugging")
parser.add_argument("--debug_rag", action="store_true", help="Enables extra verbose output for the RAG sections of the code")
parser.add_argument("--debug_model", action="store_true", help="Enables extra verbose output for the LLM Model processing sections of the code")
parser.add_argument("--chunking", choices=["paragraph", "window"], default="paragraph", help="Strategy used to split notes into chunks when indexing")
parser.add_argument("--clean_latex", action="store_true", help="Strip LaTeX from math spans in notes before chunking")
parser.add_argument("--min_score", type=float, default=None, help="Minimum relevance score for retrieved chunks (0 disables the filter; default from config.ini)")
parser.add_argument("--label_chunks", action="store_true", help="Prefix each retrieved chunk with its source document title")
parser.add_argument("--source_attribution", nargs="*", choices=["similarity", "citations"], default=[], help="Methods used to keep only the sources that answered the question; combine both to require agreement (default: show every retrieved source)")
parser.add_argument("--attribution_threshold", type=float, default=None, help="Minimum cosine similarity between an answer sentence and a chunk for similarity attribution (default from config.ini)")
parser.add_argument("--local", action="store_true", help="Outputs program to CLI for quick testing")
parser.add_argument("--reload", action="store_true", help="Enable auto reload on code changes (development only)")
parser.add_argument("--agent_prompt", action="store", default="config_agent.md", help="Path to the agent system prompt file")
parser.add_argument("--host", action="store", default="127.0.0.1", help="Configure host address")
parser.add_argument("--port", action="store", type=int, default=8000, help="Configure host port")

args = parser.parse_args()
providers.set_provider(args.provider)

def handle_indexing(verbose, debug_rag):
    if needs_indexing((verbose or debug_rag), args.chunking, args.clean_latex):
        if (verbose or debug_rag):
            print("Updating LanceDB index...")
        index_data((verbose or debug_rag), args.chunking, args.clean_latex)

class Source(BaseModel):
    title: str
    chunk_ids: list[str]

class ChatMessage(BaseModel):
    sender: str
    content: str
    sources: list[Source] = []

class ChatRequest(BaseModel):
    messages: list[ChatMessage]

def attribute_sources(answer, candidates):
    content = answer["message"]["content"]
    selected = candidates

    if "citations" in args.source_attribution:
        if args.debug_model:
            answer["message"]["raw_content"] = content
        content, cited_indexes = extract_citations(content, len(candidates))
        answer["message"]["content"] = content
        selected = intersect_chunks(selected, cited_chunks(candidates, cited_indexes))

    if "similarity" in args.source_attribution:
        threshold = args.attribution_threshold
        if threshold is None:
            threshold = config.getfloat("attribution", "SIMILARITY_THRESHOLD")
        sentences = split_sentences(content)
        sentence_vectors = embed_sources(sentences) if sentences else []
        selected = intersect_chunks(selected, similar_chunks(sentence_vectors, candidates, threshold))

    return selected

def select_sources(answer, chunks_contexto, chunks_novos):
    if frase_sem_dados in answer["message"]["content"]:
        return []
    if args.source_attribution:
        return attribute_sources(answer, chunks_contexto)
    return chunks_novos

def group_by_title(chunks):
    grouped = {}
    for chunk in chunks:
        grouped.setdefault(chunk["title"], []).append(chunk["chunk_id"])
    return [{"title": title, "chunk_ids": chunk_ids} for title, chunk_ids in grouped.items()]

@app.post("/ping")
async def hello_world(item: ChatRequest):
    return {"answer": "hello world!",
           "sources": []}

@app.get("/documents")
async def list_documents():
    return [summarize(document) for document in load_documents()]

@app.get("/documents/{document_id}")
async def read_document(document_id: str):
    document = find_by_id(load_documents(), document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Documento não encontrado")
    return document

@app.post("/chat")
async def process_message(item: ChatRequest):
    global args
    local = args.local
    verbose = args.verbose
    debug_model = args.debug_model
    debug_rag = args.debug_rag
    
    handle_indexing(verbose, debug_rag)

    historico_conversa = []
    if (len(item.messages) > 1):
        for message in item.messages[:-1]:
            historico_conversa.append({"role": message.sender, "content": message.content})

    chunk_ids_anteriores = [chunk_id for message in item.messages[:-1] for source in message.sources for chunk_id in source.chunk_ids]

    message = item.messages.pop().content

    command = get_command(message, verbose)
    if command:
        # Executa o comando e envia a resposta para o usuario
        # Alguns comandos que "terminam" o processo devem usar 'continue' para nao encerrar o loop
        return command
            
    chunks_novos = retrieve_context(message, debug_rag, args.min_score)
    chunks_anteriores = fetch_chunks(chunk_ids_anteriores)
    chunks_contexto = merge_chunks(chunks_anteriores, chunks_novos)
    citations = "citations" in args.source_attribution
    contexto = format_context(chunks_contexto, args.label_chunks, citations)

    payload = create_payload(historico_conversa, message, contexto, args.agent_prompt, citations)

    answer = providers.chat(payload, verbose=verbose, debug_model=debug_model)

    fontes = group_by_title(select_sources(answer, chunks_contexto, chunks_novos))

    return {"answer": answer,
            "sources": fontes}

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
        
    if needs_indexing((verbose or debug_rag), args.chunking, args.clean_latex):
        if (verbose or debug_rag):
            print("Updating LanceDB index...")
        index_data((verbose or debug_rag), args.chunking, args.clean_latex)
    
    chunks_acumulados = []
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
                    print("Continuando...")
                    continue
            
            chunks_novos = retrieve_context(message, debug_rag, args.min_score)
            chunks_acumulados = merge_chunks(chunks_acumulados, chunks_novos)
            citations = "citations" in args.source_attribution

            payload = create_payload(historico_conversa, message, format_context(chunks_acumulados, args.label_chunks, citations), args.agent_prompt, citations)

            answer = providers.chat(payload, verbose=verbose, debug_model=debug_model)

            fontes_usadas = group_by_title(select_sources(answer, chunks_acumulados, chunks_novos))
            
            await complete_step(historico_conversa, message, answer['message']['content'], local, websocket)

            if (local and (verbose or debug_rag)):
                print("\nFontes usadas:", ", ".join(fonte["title"] for fonte in fontes_usadas) or "nenhuma")
            
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
        uvicorn.run("main:app", host=args.host, port=args.port, reload=args.reload, reload_excludes=["*.db", "*.sqlite", "lancedb/*", "*.lancedb"])
    else:
        asyncio.run(start_agent(websocket=None))  # For testing without WebSocket
