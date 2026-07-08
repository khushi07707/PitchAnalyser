import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Augmented Pitch Analyser"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = "c8b0c8efc3545dfabf8c05769748682057d60613a07a167814db1ffb06e902fa"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 10080
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/pitch_analyser"
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE_MB: int = 100
    OPENAI_API_KEY: str = ""
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5500,http://127.0.0.1:5500"

    @property
    def cors_origins(self) -> List[str]:
        if not self.ALLOWED_ORIGINS:
            return []
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

    class Config:
        env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
        case_sensitive = True

settings = Settings()
