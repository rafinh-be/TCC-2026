# indexador.py
from pathlib import Path
import frontmatter
from config import conectar_banco, DocumentoOBGYN, NOTES_DIR

def indexar_repositorio():
    db = conectar_banco()
    path_dir = Path(NOTES_DIR)
    path_dir.mkdir(exist_ok=True)
    
    chunks_para_salvar = []
    
    print("📥 Lendo arquivos Markdown e extraindo metadados...")
    for arquivo_md in path_dir.glob("*.md"):
        # Carrega o arquivo interpretando o Front Matter (YAML no topo)
        post = frontmatter.load(arquivo_md)
        
        # Extrai as tags do YAML. Se não houver, usa uma lista vazia
        tags = post.get("tags", [])
        conteudo_limpo = post.content
        
        # Divide por parágrafos
        paragrafos = [p.strip() for p in conteudo_limpo.split("\n\n") if p.strip()]
        
        for para in paragrafos:
            chunks_para_salvar.append({
                "text": para,
                "nome_arquivo": post.get("titulo", arquivo_md.stem),  # Usa o título do YAML ou o nome do arquivo sem extensão
                "tags": tags
            })
            print(para, tags)
        
    if not chunks_para_salvar:
        print("⚠️ Nenhum arquivo ou parágrafo encontrado para indexar.")
        return

    # Salva persistindo no disco. Usamos overwrite para recriar o índice do zero se as notas mudarem
    table = db.create_table("notas_medicas", schema=DocumentoOBGYN, mode="overwrite")
    table.add(chunks_para_salvar)
    
    # Cria o índice de busca por palavra-chave (FTS)
    table.create_fts_index("text", replace=True)
    
    from memoria import atualizar_arquivo_memoria
    atualizar_arquivo_memoria()
    
    print(f"✅ Sucesso! {len(chunks_para_salvar)} blocos salvos e indexados localmente em '{db.uri}'")

if __name__ == "__main__":
    indexar_repositorio()