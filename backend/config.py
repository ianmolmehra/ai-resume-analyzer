from pydantic_settings import BaseSettings
from typing import Optional
import os


# SQLite DB file lives at the project root
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DB_PATH = os.path.join(_BASE_DIR, "resume_analyzer.db")


class Settings(BaseSettings):
    # App
    APP_NAME: str = "AI Resume Analyzer"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database — SQLite by default (no setup required)
    DATABASE_URL: str = f"sqlite:///{_DB_PATH}"

    @property
    def db_url(self) -> str:
        return self.DATABASE_URL

    # File Upload
    UPLOAD_DIR: str = os.path.join(_BASE_DIR, "uploads")
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: list = [".pdf", ".docx"]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
