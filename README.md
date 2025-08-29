# Wiki RAG App (LangChain + FAISS + Gemini 2.5 Flash)

This project implements a retrieval-augmented generation (RAG) application over a Fandom wiki dump (Stormlight Archive). It combines OpenAI embeddings with a FAISS vector store for retrieval, Gemini 2.5 Flash for LLM-driven reasoning, and a simple Streamlit frontend for interaction.

---

## Features
- **Retrieval**: OpenAI `text-embedding-3-large` with FAISS
- **LLM**: Gemini 2.5 Flash for query rewriting and question answering
- **Frontend**: Streamlit web app
- **Backend**: FastAPI service with `/chat` endpoint
- **Environment variables**: loaded automatically from `.env` via `python-dotenv`

---

## Prerequisites
- Python 3.10+
- MediaWiki XML dump (e.g., `stormlightarchive_pages_current.xml`)
- API keys:
  - `OPENAI_API_KEY`
  - `GOOGLE_API_KEY` (or `GEMINI_API_KEY`)

---

## Environment Setup

Create a `.env` file at the project root with:

```ini
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...

XML_PATH=/absolute/path/to/stormlightarchive_pages_current.xml
INDEX_DIR=index

TOP_K=4
API_URL=http://localhost:8000
```

---

## Installation

### Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

### Frontend
```bash
cd ../frontend
python -m venv .venv && source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

---

## Build the Index

Run once, or whenever the XML changes:

```bash
cd backend
source .venv/bin/activate
python ingest_xml.py
```

This parses the MediaWiki XML, strips wiki markup, chunks into passages, embeds with OpenAI, and saves FAISS index files to `backend/index/`.

---

## Running the Web App

### Start the Backend (FastAPI)
```bash
cd backend
source .venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- Health check: `http://localhost:8000/health`  
- Chat endpoint: `POST /chat`

### Start the Frontend (Streamlit)
Open another terminal:

```bash
cd frontend
source .venv/bin/activate
streamlit run app.py
```

The web UI will be available at `http://localhost:8501`.

---

## Usage

1. Open the Streamlit app in a browser.
2. Enter a question, e.g., *Who is Kaladin’s spren?*
3. The system:
   - Rewrites follow-up questions to standalone queries
   - Uses MultiQueryRetriever to generate multiple retrieval variants
   - Answers only from retrieved context
   - Cites sources by wiki page title

---

## Configuration

- **Retrieval depth**: adjust `TOP_K` in `.env` or change slider in UI.
- **Chunking**: edit parameters in `backend/ingest_xml.py` and rebuild the index.
- **Data source**: point `XML_PATH` to another MediaWiki dump and re-ingest.

---

## Project Structure

```
wiki-rag-app/
  backend/
    main.py            # FastAPI app
    chains.py          # LLM chains for rewrite and QA
    ingest_xml.py      # Ingest MediaWiki XML into FAISS
    utils_wiki.py      # Wiki parsing/cleanup
    settings.py        # Load env variables
    requirements.txt
    index/             # FAISS index artifacts
  frontend/
    app.py             # Streamlit UI
    requirements.txt
  .env
  README.md
```

---

## Notes

- Answers are grounded in retrieved context. If insufficient, the system will return *"Insufficient context"* and suggest clarification.
- Conversation history is maintained in memory with a short rolling buffer.
- For production, deploy the backend with a process manager (e.g., gunicorn/uvicorn behind Nginx) and load secrets securely.