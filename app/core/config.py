from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="INSIGHTFLOW_")

    database_url: str = "sqlite:///data/insightflow.db"
    documents_dir: Path = Path("data/documents")
    row_limit: int = 500
    allowed_origins: str = "http://localhost:8501"


settings = Settings()
