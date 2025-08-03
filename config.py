import os
from pathlib import Path
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field

# Optional: CUDA availability check
try:
    import torch
except ImportError:
    torch = None


class Settings(BaseSettings):
    """App settings loaded from environment variables or defaults"""

    # API Keys
    openrouter_api_key: Optional[str] = Field(default=None, env="OPENROUTER_API_KEY")

    # LLM Configuration
    openrouter_base_url: str = Field(default="https://openrouter.ai/api/v1", env="OPENROUTER_BASE_URL")
    llm_model: str = Field(default="anthropic/claude-3-haiku", env="LLM_MODEL")
    llm_temperature: float = Field(default=0.1, env="LLM_TEMPERATURE")
    llm_max_tokens: int = Field(default=150, env="LLM_MAX_TOKENS")

    # Embedding Model
    embedding_model: str = Field(default="intfloat/e5-small", env="EMBEDDING_MODEL")
    embedding_device: str = Field(default="cpu", env="EMBEDDING_DEVICE")  # "cuda" or "cpu"

    # Document Processing
    chunk_size: int = Field(default=500, env="CHUNK_SIZE")
    chunk_overlap: int = Field(default=50, env="CHUNK_OVERLAP")
    max_docs_for_context: int = Field(default=2, env="MAX_DOCS_FOR_CONTEXT")

    # Caching
    enable_cache: bool = Field(default=True, env="ENABLE_CACHE")
    cache_dir: str = Field(default="cache", env="CACHE_DIR")
    cache_ttl_hours: int = Field(default=24, env="CACHE_TTL_HOURS")

    # File Upload
    max_file_size_mb: int = Field(default=10, env="MAX_FILE_SIZE_MB")
    allowed_file_types: List[str] = Field(default=[".pdf", ".txt", ".md", ".docx"], env="ALLOWED_FILE_TYPES")

    # Server Config
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    debug: bool = Field(default=True, env="DEBUG")

    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_dir: str = Field(default="logs", env="LOG_DIR")

    # Project Directory
    base_dir: Path = Path(__file__).parent

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "allow"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.create_directories()

    def create_directories(self):
        for directory in [self.cache_dir, self.log_dir]:
            Path(directory).mkdir(parents=True, exist_ok=True)

    @property
    def cache_path(self) -> Path:
        return Path(self.cache_dir)

    @property
    def log_path(self) -> Path:
        return Path(self.log_dir)


# Load settings
settings = Settings()

# Safety checks
if not settings.openrouter_api_key:
    print("⚠️  WARNING: OPENROUTER_API_KEY not found!")
    print("   Running with HuggingFace models only.")
else:
    print(f"✅ OpenRouter key loaded: {settings.openrouter_api_key[:5]}...{settings.openrouter_api_key[-5:]}")

if settings.embedding_device == "cuda":
    if torch and not torch.cuda.is_available():
        print("⚠️  WARNING: CUDA selected but no GPU found. Switching to CPU.")
        settings.embedding_device = "cpu"
    elif not torch:
        print("⚠️  WARNING: CUDA selected but torch not installed. Switching to CPU.")
        settings.embedding_device = "cpu"
