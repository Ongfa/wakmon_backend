from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Wakmon Backend"

    # Security
    SECRET_KEY: str = "dev-secret-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ORCHESTRATE_API_KEY: str = ""

    # Database
    DATABASE_URL: str = "sqlite:///./wakmon.db"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:5173",
    ]

    # LLM providers — keys stay server-side
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-3-5-haiku-20241022"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "openai/gpt-oss-120b"
    MISTRAL_API_KEY: str = ""
    MISTRAL_MODEL: str = "mistral-small-latest"
    OLLAMA_ENABLED: bool = False
    OLLAMA_BASE_URL: str = "http://127.0.0.1:11434"
    OLLAMA_API_KEY: str = ""
    OLLAMA_MODEL: str = "llama3.1"
    ORCHESTRATE_MOCK: bool = False
    ORCHESTRATE_TIMEOUT_SECONDS: float = 45.0
    ORCHESTRATE_SYNTHESIS_PROVIDER: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
