import sqlite3
from pathlib import Path

from app.core.config import settings


def database_path() -> Path:
    if not settings.database_url.startswith("sqlite:///"):
        raise ValueError("The local MVP supports sqlite URLs only.")
    return Path(settings.database_url.removeprefix("sqlite:///"))


def connect(read_only: bool = False) -> sqlite3.Connection:
    path = database_path()
    if read_only:
        connection = sqlite3.connect(f"file:{path.resolve()}?mode=ro", uri=True)
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    return connection
