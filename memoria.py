# memoria.py
import json
import os
from pathlib import Path
from config import NOTES_DIR

MEMORY_FILE = "./index_memory.json"

def verificar_precisa_indexar() -> bool:
    """
    Compara os arquivos na pasta my_notes com o arquivo de memória JSON.
    Retorna True se houver arquivos novos ou modificados.
    """
    path_dir = Path(NOTES_DIR)
    if not path_dir.exists():
        path_dir.mkdir(exist_ok=True)
        return False

    # 1. Mapeia o estado atual da pasta (Nome do arquivo -> Timestamp de modificação)
    estado_atual = {}
    for arquivo_md in path_dir.glob("*.md"):
        estado_atual[arquivo_md.name] = os.path.getmtime(arquivo_md)

    # 2. Se a pasta está vazia, não há o que indexar
    if not estado_atual:
        return False

    # 3. Se o arquivo de memória não existe, precisamos indexar tudo
    if not os.path.exists(MEMORY_FILE):
        return True

    # 4. Lê a memória salva anteriormente
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            memoria_salva = json.load(f)
    except Exception:
        return True  # Se o JSON estiver corrompido, força a reindexação

    # 5. Compara o estado atual com a memória salva
    # Se mudou o número de arquivos, precisa indexar
    if len(estado_atual) != len(memoria_salva):
        return True

    # Se algum arquivo foi modificado ou é novo, precisa indexar
    for nome_arq, mtime_atual in estado_atual.items():
        if nome_arq not in memoria_salva:
            return True  # Arquivo novo encontrado
        if mtime_atual > memoria_salva[nome_arq]:
            return True  # Arquivo foi editado

    return False

def atualizar_arquivo_memoria():
    """Salva o estado atual dos arquivos na memória JSON."""
    path_dir = Path(NOTES_DIR)
    estado_atual = {}
    for arquivo_md in path_dir.glob("*.md"):
        estado_atual[arquivo_md.name] = os.path.getmtime(arquivo_md)
        
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(estado_atual, f, indent=4)