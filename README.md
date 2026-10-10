Projeto de TCC da Escola Politécnica da USP para o departamento de PSI

Membros: Rafa Bertão de Sousa; Victor Roselli Moracca
https://www.hu.usp.br/maternidade

## Modelos remotos do Google

O chat e o gerador de testes usam `gemini-3.8-flash`; os embeddings usam
`gemini-embedding-001` (768 dimens?es). Os modelos executam pela API do Google;
o backend e o LanceDB continuam locais.

1. Instale: `python -m pip install -r requirements.txt`.
2. Obtenha uma chave em https://aistudio.google.com/apikey.
3. Copie `backend/.env.example` para `backend/.env` e preencha `GEMINI_API_KEY`.
   Tamb?m ? poss?vel usar `GOOGLE_API_KEY` no ambiente.
4. Ajuste os modelos em `backend/config.ini` ou nas vari?veis de `.env.example`.

O Gemini 3.8 Flash oferece cota gratuita para entrada e sa?da de texto:
https://ai.google.dev/gemini-api/docs/pricing#gemini-3.8-flash
A gratuidade depende do projeto estar no Free Tier e de seus limites de uso;
selecionar o modelo n?o altera o faturamento da conta Google.

A primeira consulta reindexa a base com os embeddings do Google. Altera??es no
modelo de embeddings ou nas dimens?es tamb?m provocam reindexa??o. ? necess?rio
acesso ? internet e quota para indexar e consultar. Documentos s?o enviados ao
Google para embeddings; perguntas, hist?rico e contexto s?o enviados ao Gemini.

O script `python gerar_testset.py` usa a mesma configura??o da API.


# Rodar backend
- Instalar python e pip
- Instalar dependencias
- cd backend
- python main.py 

# Rodar frontend
- Instalar Node.js
- cd frontend
- npm install
- npm run dev