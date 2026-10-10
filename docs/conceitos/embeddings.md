# Embeddings

Criado em: 2026-10-10 · Atualizado em: 2026-10-10

## O que são

Embeddings são representações de textos em vetores: listas de números produzidas por um modelo. Esses números permitem comparar textos pela proximidade de suas representações, ajudando a encontrar conteúdo relacionado mesmo quando a pergunta usa palavras diferentes das do documento.

Cada posição é uma dimensão do vetor. Não devemos interpretar uma posição isolada como uma palavra ou conceito específico. No projeto, cada vetor tem **768 dimensões**.

O modelo de embeddings produz os vetores usados na busca. O LLM recebe os trechos encontrados e escreve a resposta ao usuário. São duas etapas com modelos e chamadas de API diferentes.

## Como usamos no TCC

O fluxo implementado é:

1. Dividir os documentos Markdown em trechos menores, chamados *chunks*.
2. Gerar um embedding para cada trecho e armazená-lo com o texto no LanceDB.
3. Gerar um embedding para a pergunta do usuário.
4. Buscar trechos relevantes, combinando busca vetorial e busca textual.
5. Enviar os trechos recuperados ao Gemini para elaborar uma resposta ancorada na base.

```mermaid
flowchart TD
    subgraph Indexacao["Indexação dos documentos"]
        A["Documentos Markdown"] --> B["Divisão em trechos"]
        B --> C["API de embeddings: documentos"]
        C --> D["LanceDB: textos e vetores armazenados"]
    end
    subgraph Consulta["A cada pergunta"]
        E["Pergunta do usuário"] --> F["API de embeddings: consulta"]
        F --> G["Busca híbrida: vetorial e textual"]
        E --> G
        G --> H["Trechos recuperados"]
        H --> I["Gemini: avaliar contexto e gerar resposta"]
        E --> I
        I --> J["Resposta, esclarecimento ou recusa"]
    end
    D --> G
```

A indexação prepara os vetores dos documentos para reutilização. A consulta gera o vetor da pergunta e combina a busca semântica com a textual; o Gemini avalia se os trechos bastam para responder.

A configuração atual usa `gemini-embedding-001`, pela API do Google, com 768 dimensões. Antes da migração discutida no chat, os embeddings eram gerados localmente com Sentence Transformers; o LLM usava Ollama.

O adaptador em [google_embeddings.py](../../backend/google_embeddings.py) usa `RETRIEVAL_DOCUMENT` para os documentos e `RETRIEVAL_QUERY` para perguntas. Também normaliza os vetores, dividindo seus componentes pelo comprimento do vetor.

## Exemplo da conversa

Perguntamos: **“O que você sabe sobre pré-parto?”**

Uma busca semântica pode recuperar um trecho sobre preparação ou plano de parto mesmo sem repetir exatamente “pré-parto”. Porém, a representação vetorial não garante que todos os resultados respondam à pergunta: pré-parto, parto prematuro e pós-parto são assuntos distintos.

No teste realizado, a busca encontrou um trecho sobre plano de parto, mas um filtro descartou esse resultado antes de enviá-lo ao LLM. O agente então recusou a pergunta por contexto insuficiente. Corrigimos o filtro: o score de fusão por ranking (RRF) ordena os resultados das buscas; não é uma probabilidade de que um trecho seja correto ou suficiente.

Esse caso mostra que uma resposta ruim pode vir da recuperação e da seleção dos trechos, mesmo quando a API de embeddings funciona.

## Indexação, compatibilidade e cotas

Os embeddings dos documentos são calculados durante a indexação e reutilizados nas consultas seguintes. A pergunta exige um vetor próprio para realizar a busca.

Ao trocar o modelo de embeddings ou a quantidade de dimensões, precisamos reindexar os documentos. Vetores produzidos por modelos diferentes não devem ser comparados como se pertencessem ao mesmo espaço, mesmo quando têm o mesmo número de dimensões. O projeto registra a configuração do embedding para detectar essa mudança.

Durante a migração, a API retornou `429 RESOURCE_EXHAUSTED`, identificando um limite de **100 por minuto** para embeddings no projeto Google usado naquele teste. Esse erro era de cota por minuto, não de autenticação nem de limite diário. O valor é uma observação daquele teste, não uma garantia para toda conta ou modelo.

Adicionamos lotes menores, espaçamento entre chamadas e espera baseada no `RetryInfo` retornado pelo Google. A primeira indexação pode demorar; consultas posteriores reutilizam os vetores armazenados. Em um teste real após a correção SSL, a API retornou um vetor com 768 dimensões.

## Limitações importantes

- Proximidade vetorial não comprova correção médica nem suficiência da evidência.
- A qualidade da busca depende dos documentos, da divisão em trechos, da pergunta e da seleção dos resultados.
- Usar a API evita carregar o modelo de embeddings localmente, mas exige internet e envia os textos ao provedor. O LanceDB continua local.

## Referências

- [Documentação de embeddings do Gemini](https://ai.google.dev/gemini-api/docs/embeddings).
- [Limites de uso da Gemini API](https://ai.google.dev/gemini-api/docs/rate-limits).
- [Configuração dos modelos no projeto](../../backend/config.ini).
- [Indexação e recuperação no LanceDB](../../backend/database_utility.py).
