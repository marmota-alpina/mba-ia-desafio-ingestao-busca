# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

RAG (Retrieval-Augmented Generation) system for ingesting PDF documents, storing them in a PostgreSQL database with pgvector extension, and enabling semantic search and chat functionality using LangChain. Built for the Full Cycle MBA in Software Engineering with AI challenge.

## Architecture

The system consists of three main components:

1. **Ingestion Pipeline** (`src/ingest.py`): Loads PDF documents and stores embeddings in PostgreSQL with pgvector
2. **Search Module** (`src/search.py`): Retrieves relevant context from the vector database based on user queries, with a strict prompt template that only answers based on provided context
3. **Chat Interface** (`src/chat.py`): Interactive chat using the search_prompt chain for user interactions

**Database**: PostgreSQL 17 with pgvector extension for vector similarity search, managed via Docker Compose.

**LLM Integration**: Supports both Google Generative AI (Gemini) and OpenAI models for embeddings and generation, configured via environment variables.

**LangChain Stack**: Uses `langchain-postgres` for vector storage, `langchain-google-genai` or `langchain-openai` for LLM access, and `pypdf` for PDF processing.

## Development Setup

1. Copy environment configuration:
   ```bash
   cp .env.example .env
   ```

2. Configure required environment variables in `.env`:
   - `GOOGLE_API_KEY` or `OPENAI_API_KEY` (choose one provider)
   - `DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/rag` (default)
   - `PG_VECTOR_COLLECTION_NAME=pdf_embeddings` (default)
   - `PDF_PATH=./document.pdf` (default)
   - Embedding model names (pre-configured for Google: `models/embedding-001`, OpenAI: `text-embedding-3-small`)

3. Start PostgreSQL with pgvector:
   ```bash
   docker compose up -d
   ```

4. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

**Ingest PDF documents**:
```bash
python src/ingest.py
```

**Run interactive chat**:
```bash
python src/chat.py
```

**Quick test without interactive interface**:
```bash
python src/search.py "Your question here"
```

**Clean and re-ingest PDF**:
```bash
python src/ingest.py
```
The ingestion script automatically drops the existing collection before creating a new one.

**Database management**:
```bash
# Stop database
docker compose down

# Stop and remove all data
docker compose down -v

# View PostgreSQL logs
docker compose logs postgres
```

## Key Implementation Notes

- The `PROMPT_TEMPLATE` in `src/search.py:15-40` enforces strict context-based responses: the system will only answer questions based on the provided context and will respond "Não tenho informações necessárias para responder sua pergunta." for out-of-scope queries.

- LLM provider priority in `src/search.py:64-84` and `src/ingest.py:16-36`: OpenAI is prioritized if both API keys are configured.

- The `search_prompt()` function in `src/search.py:87-147` returns either a configured chain (if no question provided) or the answer (if question provided), enabling both reusable chain creation and one-off queries.

- Text chunking parameters in `src/ingest.py:61-64`: chunk_size=1000 characters with chunk_overlap=150 for context preservation.

- Retriever configuration in `src/search.py:116-119`: Uses similarity search with k=10 to retrieve the top 10 most relevant document chunks.

- Vector database collection is managed through the `PG_VECTOR_COLLECTION_NAME` environment variable, allowing multiple collections in the same database.

- The docker-compose.yml includes a `bootstrap_vector_ext` service that automatically creates the pgvector extension on first run via healthcheck dependency.

## Python Environment

Project uses Python 3.13 with virtual environment in `.venv/`. The requirements.txt includes the full LangChain ecosystem with async support (aiohappyeyeballs, aiohttp, asyncpg).

## Chat Interface Commands

When running `src/chat.py`, the following special commands are available:
- `sair`, `exit`, `quit` - Exit the chat
- `limpar`, `clear` - Clear the terminal screen
