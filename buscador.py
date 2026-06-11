# buscador.py
from config import conectar_banco, DocumentoOBGYN

def buscar_contexto_expandido(pergunta: str) -> tuple[str, set[str]]:
    db = conectar_banco()
    
    # Verifica se a tabela já existe no disco
    if "notas_medicas" not in db.table_names():
        return "", set()
        
    table = db.open_table("notas_medicas")
    
    # 1. Busca Semântica Inicial para identificar o assunto principal e capturar a Tag
    # ... código de conexão com o banco e tabela ...
    
    # 1. Defina um limite de corte (Threshold)
    # No LanceDB (usando distância L2/Euclidiana), quanto MENOR a distância, mais parecido é o texto.
    # Valores entre 0.7 e 1.1 costumam ser ideais. Ajuste conforme seu modelo de embedding.
    LIMITE_DISTANCIA_MAXIMA = 0.95 
    
    # 2. Executa a busca trazendo a distância
    # Certifique-se de que sua busca não está usando apenas .to_list(), mas inspecionando os metadados
    resultados = (
        table.search(pergunta)
        .metric("l2") # ou "cosine", dependendo de como criou
        .limit(3)
        .to_list()
    )
    
    blocos_validos = []
    fontes_validas = set()
    
    for res in resultados:
        # O LanceDB injeta o campo '_distance' automaticamente no dicionário de retorno
        distancia = res.get("_distance", 0.0)
        
        # 🛡️ TRAVA VETORIAL: Se a distância for maior que o limite, ignora o bloco
        if distancia > LIMITE_DISTANCIA_MAXIMA:
            # Imprime no terminal em modo debug se quiser rastrear o que foi bloqueado:
            # print(f"DEBUG: Bloco descartado. Distância muito alta: {distancia:.2f}")
            continue
            
        blocos_validos.append(res["text"])
        fontes_validas.add(res.get("metadata", {}).get("titulo", "Documento Sem Título"))
        
    # 3. Retorna apenas se encontrou algo realmente relevante
    if not blocos_validos:
        return None, []
        
    contexto_unificado = "\n\n---\n\n".join(blocos_validos)
    return contexto_unificado, list(fontes_validas)