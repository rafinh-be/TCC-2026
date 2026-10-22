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

- `backend/` — FastAPI app (`main.py`) exposing `POST /chat` (stateless: the client sends the message history, accumulated context and sources) and `WS /ws/chat`. Talks to a local Ollama model.
  - `database_utility.py` — indexes `database/data_files/*.md` into LanceDB (paragraph chunks, multilingual sentence-transformers embeddings) and retrieves context. Re-indexes when file mtimes differ from `database/index_memory.json`.
  - `ollama_interaction.py` — builds the prompt payload and calls the model with a thinking-token limit and a fallback synthesis step.
  - `user_prompt_proccessing.py` / `functions.py` — slash commands (`/clear`, `/reset`) and message I/O.
  - `config.ini` — model names, all LLM prompts (system, critique, refinement, tool validation) and database paths. `config_agent.md` overrides the system prompt when present.
- `frontend/` — Next.js (App Router) + React + TypeScript, Tailwind CSS v4 + daisyUI, `react-markdown` for rendering answers. Chat page at `src/app/chat/page.tsx`, components under `src/app/components/`.
- `database/data_files/` — knowledge base: Markdown files with YAML frontmatter (`id`, `titulo`, `tags`).
- Root-level Python files (`app.py`, `buscador.py`, `indexador.py`, `memoria.py`, `ferramentas.py`, `config.py`) are an earlier version of the backend; current work happens in `backend/`.

## Setup & Commands

Prerequisites: Python, Node.js, and [Ollama](https://ollama.com) with the model configured in `backend/config.ini` pulled (e.g. `ollama pull qwen3.5:9b`).

Backend (must run from `backend/` — config and data paths are relative):

```bash
pip install -r requirements.txt
cd backend
python main.py            # flags: -v/--verbose, --debug_rag, --debug_model, --local (CLI mode)
```

Frontend (expects the backend at `http://127.0.0.1:8000`):

```bash
cd frontend
npm install
npm run dev               # http://localhost:3000
npm run lint
npm run build
```

There is no automated test suite yet.

## Conventions

- Commits follow Conventional Commits (`feat: ...`, `fix: ...`).
- User-facing text, LLM prompts and knowledge-base content are in Portuguese (pt-BR).
- LLM prompts live in `backend/config.ini`, not hardcoded in Python.
- Backend modules read `config.ini` via `configparser`; new settings go there.
- Frontend components live in `src/app/components/<feature>/` with camelCase file names (`chatInput.tsx`) and PascalCase exports (`ChatInput`). Style with Tailwind/daisyUI classes.
- Frontend visual style: simple and elegant. Avoid generic AI-generated looks: no unnecessary text or decoration, and no high-contrast or saturated colour blocks (soft tints and hairline borders instead; text must still meet WCAG AA).
- Take inspiration from Brazil's Sistema Único de Saúde (SUS) palette and the gov.br design philosophy: plain language, accessibility, consistency, sober radii, calm institutional blue.
- Colours come from theme tokens in `frontend/src/app/globals.css` (selected with `NEXT_PUBLIC_THEME`); never hardcode colour values in components.
- New knowledge-base documents go in `database/data_files/` as Markdown with `id`, `titulo` and `tags` frontmatter; paragraphs are separated by blank lines, since indexing splits on them.
