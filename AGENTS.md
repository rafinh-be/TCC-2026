# Agent Instructions

Shared instructions for all AI coding agents working in this repository.
This file is the single source of truth — `CLAUDE.md` imports it.

## Principles

1. Keep commits focused and PRs short.
2. Do what the user asks and only what the user asks. Don't implement features based on your own interpretation of the prompt.
3. Don't leave explanatory comments in the code. If the user asks for an explanation, answer in the conversation instead of editing the code. Variable and function names should be self-explanatory; avoid function comments at all costs.
4. When details are missing for a feature or the prompt is ambiguous, ask. User interaction is wanted and encouraged.
5. Keep output text focused and concise.
6. Prefer additive editing. Instead of replacing a feature with another, keep both in the code and make them selectable with a `--` flag.

## Project Overview

Undergraduate thesis (TCC) project from Escola Politécnica da USP (PSI department), in partnership with the HU-USP maternity ward. It is a pt-BR obstetrics and gynecology assistant for patients that answers strictly from a local knowledge base (RAG) and never diagnoses or invents dosages.

- `backend/` — FastAPI app (`main.py`) exposing `POST /api/chat` (the client sends `message` and `historico_conversa`) and `WS /ws/chat`. Uses the Google Gemini API.
  - `database_utility.py` — indexes `database/data_files/*.md` into LanceDB using overlapping text chunks and Gemini embeddings, and retrieves context through hybrid vector and full-text search. Re-indexes when source files or the embedding configuration change, or the vector table is missing.
  - `gemini_interaction.py` — builds the prompt payload and calls Gemini with configured thinking and output limits.
  - `google_models.py` / `google_embeddings.py` — shared Gemini client, environment-based model settings and remote embeddings.
  - `user_prompt_proccessing.py` / `functions.py` — slash commands (`/clear`, `/reset`) and message I/O.
  - `config.ini` — model names, all LLM prompts (system, critique, refinement, tool validation) and database paths. `config_agent.md` overrides the system prompt when present.
- `frontend/` — Streamlit app (`app.py`) communicating with the backend through `ws://127.0.0.1:8000/ws/chat`. Keeps messages and conversation history in session state.
- `database/data_files/` — knowledge base: Markdown files with YAML frontmatter (`id`, `titulo`, `tags`).

## Setup & Commands

Prerequisites: Python and a Google Gemini API key configured as `GEMINI_API_KEY` or `GOOGLE_API_KEY` in the environment, root `.env`, or `backend/.env`. Model settings live in `backend/config.ini` and can be overridden by matching uppercase environment variables. Never commit API keys.

Backend (commands from the repository root; configuration and database paths resolve relative to the backend directory):

```bash
pip install -r requirements.txt
cd backend
python main.py            # flags: -v/--verbose, --debug_rag, --debug_model, --local (CLI mode)
```

Frontend (run in a separate terminal from the repository root; expects the backend at `127.0.0.1:8000`):

```bash
streamlit run frontend/app.py  # http://localhost:8501
```

There is no automated test suite yet.

## Conventions

- Commits follow Conventional Commits (`feat: ...`, `fix: ...`).
- User-facing text, LLM prompts and knowledge-base content are in Portuguese (pt-BR).
- LLM prompts live in `backend/config.ini`, not hardcoded in Python.
- Backend modules read `config.ini` via `configparser`; new settings go there.
- Frontend UI lives in `frontend/app.py`; use Streamlit and its session state for conversation state.
- New knowledge-base documents go in `database/data_files/` as Markdown with `id`, `titulo` and `tags` frontmatter. Chunk size and overlap are configured in `backend/config.ini`.
