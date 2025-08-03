import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional

# Import torch for CUDA availability check
try:
    import torch
except ImportError:
    torch = None

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # API Configuration
    openrouter_api_key: Optional[str] = None
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    # Model Configuration
    llm_model: str = "anthropic/claude-3-haiku"
    llm_temperature: float = 0.1
    llm_max_tokens: int = 150

    # Embedding Configuration
    embedding_model: str = "intfloat/e5-small"  # ✅ Switched for lower memory usage
    embedding_device: str = "cpu"  # Set to "cuda" if GPU available

    # Document Processing
    chunk_size: int = 500
    chunk_overlap: int = 50
    max_docs_for_context: int = 2

    # Caching
    enable_cache: bool = True
    cache_dir: str = "cache"
    cache_ttl_hours: int = 24

    # File Upload Limits
    max_file_size_mb: int = 10
    allowed_file_types: list = [".pdf", ".txt", ".md", ".docx"]

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True

    # Logging
    log_level: str = os.environ.get("LOG_LEVEL", "INFO")
    log_dir: str = "logs"

    # Directories
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
        directories = [self.cache_dir, self.log_dir]
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)

    @property
    def cache_path(self) -> Path:
        return Path(self.cache_dir)

    @property
    def log_path(self) -> Path:
        return Path(self.log_dir)

# Global settings instance
settings = Settings()

# Check OpenRouter key
if not settings.openrouter_api_key:
    print("⚠️  WARNING: OPENROUTER_API_KEY not found!")
    print("   Running with HuggingFace models only.")
else:
    print(f"✅ OpenRouter API key loaded: {settings.openrouter_api_key[:5]}...{settings.openrouter_api_key[-5:]}")

# Check CUDA availability
if settings.embedding_device == "cuda" and torch and not torch.cuda.is_available():
    print("⚠️  WARNING: CUDA selected but no GPU found. Switching to CPU.")
    settings.embedding_device = "cpu"
elif settings.embedding_device == "cuda" and not torch:
    print("⚠️  WARNING: CUDA selected but torch not installed. Switching to CPU.")
    settings.embedding_device = "cpu"
