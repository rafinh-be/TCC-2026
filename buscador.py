# buscador.py
from config import conectar_banco, DocumentoOBGYN, embedding_model


def _codificar_query(pergunta: str) -> list[float]:
    """Codifica a pergunta usando o paraphrase-multilingual-MiniLM-L12-v2.

    Usar o mesmo modelo de embeddings do índice garante que o vetor da query
    esteja no mesmo espaço vetorial dos documentos armazenados, maximizando
    a precisão da busca semântica.
    """
    # compute_query_embeddings retorna list[list[float]] — já é Python puro, sem .tolist()
    return embedding_model.compute_query_embeddings(pergunta)[0]


def buscar_contexto_expandido(pergunta: str) -> tuple[str, set[str]]:
    db = conectar_banco()

    # Verifica se a tabela já existe no disco
    if "notas_medicas" not in db.table_names():
        return "", set()

    table = db.open_table("notas_medicas")

    vetor_query = _codificar_query(pergunta)

    # Busca híbrida retorna _relevance_score via RRF (Reciprocal Rank Fusion):
    # quanto MAIOR o score, mais relevante. Diferente de _distance (menor = melhor),
    # que é exclusivo da busca vetorial pura.
    # Scores RRF típicos ficam entre 0.01 e 0.07 — ajuste conforme a densidade da base.
    SCORE_MINIMO = 0.02

    # Executa a busca híbrida: vetor explícito (semântica) + texto original (BM25/FTS)
    resultados = (
        table.search(query_type="hybrid")
        .vector(vetor_query)
        .text(pergunta)
        .metric("l2")
        .limit(10)
        .to_list()
    )

    blocos_validos = []
    fontes_validas = set()

    for res in resultados:
        score = res.get("_relevance_score", 0.0)
        
        if score < SCORE_MINIMO:
            continue

        nome_documento = res.get("nome_arquivo", "Documento Sem Título")
        #print(f"Metadados encontrados -> Arquivo: {nome_documento} | Score: {score:.4f}")

        blocos_validos.append(res["text"])
        if (nome_documento not in fontes_validas):
            fontes_validas.add(nome_documento)
        
    # 3. Retorna apenas se encontrou algo realmente relevante
    if not blocos_validos:
        return None, []
        
    contexto_unificado = "\n\n---\n\n".join(blocos_validos)
    return contexto_unificado, list(fontes_validas)