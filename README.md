# InsightFlow AI

InsightFlow is an evidence-first commercial-intelligence demo. It explains performance changes using a safe, read-only analytics query plus retrieved business-document evidence, while keeping verified facts separate from hypotheses.

## Quick start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
python -m app.db.seed
uvicorn app.api.main:app --reload
# In another terminal
streamlit run ui/app.py
```

Open `http://127.0.0.1:8501`, then ask: **Why did South revenue decline in Q3 2026?**

The API is available at `http://127.0.0.1:8000/docs`.

## What is included

- FastAPI `/ask`, document management/ingestion, seed-data ingestion, evaluation, and health endpoints
- a Streamlit chat/evidence UI
- SQLite demo dataset with planted South-region Q3 causes and matching reports
- strict read-only SQL validation and curated views
- deterministic pandas analytics and chart specifications
- lightweight local retrieval with source/page/chunk citations (no model download required)
- numeric, citation, injection, and output guardrails
- pytest tests, Docker Compose, and GitHub Actions

## Design choices

The default local profile deliberately uses SQLite and TF-IDF-style lexical retrieval so the demo starts immediately. The API boundaries (`app/tools/sql`, `app/tools/rag`, and `app/models`) are kept separate so PostgreSQL, FAISS/Qdrant, and Hugging Face clients can replace those adapters without changing the response contract.

## Safety boundary

The query layer accepts only one `SELECT`/`WITH … SELECT` statement, rejects comments and unsafe keywords, applies a row limit, and is executed on a read-only SQLite connection. Retrieved documents are treated as evidence, never as instructions.
