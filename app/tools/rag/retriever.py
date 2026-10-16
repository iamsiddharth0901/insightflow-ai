import re
from dataclasses import asdict, dataclass
from pathlib import Path

from app.core.config import settings


@dataclass(frozen=True)
class Passage:
    doc_id: str
    chunk_id: str
    title: str
    page: int
    text: str
    score: int

    def as_dict(self) -> dict:
        return asdict(self)


def _document(path: Path) -> Passage | None:
    raw = path.read_text(encoding="utf-8")
    fields, _, body = raw.partition("\n\n")
    metadata = dict(line.split(": ", 1) for line in fields.splitlines() if ": " in line)
    if not body:
        return None
    return Passage(path.stem, f"{path.stem}_c1", metadata.get("title", path.stem), int(metadata.get("page", 1)), body.strip(), 0)


def retrieve(query: str, region: str | None = None, top_k: int = 3) -> list[Passage]:
    terms = set(re.findall(r"[a-z]{3,}", query.lower()))
    results: list[Passage] = []
    for path in settings.documents_dir.glob("*.txt"):
        passage = _document(path)
        if not passage:
            continue
        haystack = f"{passage.title} {passage.text}".lower()
        score = len(terms.intersection(re.findall(r"[a-z]{3,}", haystack)))
        if region and region.lower() in haystack:
            score += 2
        if score:
            results.append(Passage(**{**passage.as_dict(), "score": score}))
    return sorted(results, key=lambda item: item.score, reverse=True)[:top_k]


def ingest_text(filename: str, content: str) -> Passage:
    safe_name = re.sub(r"[^A-Za-z0-9_.-]", "_", filename)
    path = settings.documents_dir / safe_name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    parsed = _document(path)
    if not parsed:
        raise ValueError("Document must include a body after a blank line.")
    return parsed
