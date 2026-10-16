from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.agents.pipeline import answer
from app.api.schemas import AskRequest, IngestResult
from app.core.config import settings
from app.db.database import database_path
from app.db.seed import seed
from app.tools.rag.retriever import ingest_text

app = FastAPI(title="InsightFlow AI", version="0.1.0", description="Evidence-first commercial intelligence API")
app.add_middleware(CORSMiddleware, allow_origins=settings.allowed_origins.split(","), allow_methods=["*"], allow_headers=["*"])


@app.on_event("startup")
def initialize() -> None:
    if not database_path().exists():
        seed()


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "database": database_path().exists(), "documents": len(list(settings.documents_dir.glob("*.txt")))}


@app.post("/ask")
def ask(request: AskRequest) -> dict:
    return answer(request.question)


@app.post("/ingest/data")
def ingest_data() -> dict:
    seed()
    return {"status": "seeded"}


@app.post("/ingest/documents", response_model=IngestResult)
async def ingest_document(file: UploadFile = File(...)) -> dict:  # noqa: B008
    if Path(file.filename or "document.txt").suffix.lower() not in {".txt", ".md"}:
        raise HTTPException(415, "MVP ingestion supports text and markdown files only.")
    passage = ingest_text(file.filename or "document.txt", (await file.read()).decode("utf-8"))
    return {"doc_id": passage.doc_id, "chunk_id": passage.chunk_id, "title": passage.title}


@app.get("/documents")
def documents() -> list[dict]:
    return [{"doc_id": path.stem, "filename": path.name} for path in settings.documents_dir.glob("*.txt")]


@app.delete("/documents/{doc_id}")
def delete_document(doc_id: str) -> dict:
    path = settings.documents_dir / f"{doc_id}.txt"
    if not path.exists():
        raise HTTPException(404, "Document not found.")
    path.unlink()
    return {"deleted": doc_id}


@app.post("/eval/run")
def run_eval() -> dict:
    result = answer("Why did South revenue decline in Q3 2026?")
    return {"routing_pass": "rag" in result["trace"]["plan"], "numeric_facts": len(result["verified_facts"]), "citations": len(result["citations"])}
