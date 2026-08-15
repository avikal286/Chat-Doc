import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "Document QnA RAG API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Google Gemini Settings
    GEMINI_API_KEY: str = ""
    LLM_MODEL: str = "gemini-2.0-flash"
    EMBEDDING_MODEL: str = "text-embedding-004"

    # RAG Settings
    CHUNK_SIZE: int = 600
    CHUNK_OVERLAP: int = 120
    TOP_K_RESULTS: int = 4

    # Storage Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    CHROMA_PERSIST_DIR: str = str(BASE_DIR / "data" / "chroma_db")
    UPLOAD_DIR: str = str(BASE_DIR / "data" / "uploads")

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parent.parent / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

# Ensure directories exist
os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
