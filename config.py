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

    # Model Configuration - Using free models
    # Free models available on OpenRouter:
    # - "openai/gpt-3.5-turbo" (free tier)
    # - "anthropic/claude-3-haiku" (free tier)
    # - "meta-llama/llama-2-7b-chat" (free)
    # - "mistralai/mistral-7b-instruct" (free)
    llm_model: str = "anthropic/claude-3-haiku"  # Free model
    llm_temperature: float = 0.1  # Lower for faster responses
    llm_max_tokens: int = 150  # Reduced for speed

    # Embedding Configuration (Free HuggingFace model)
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_device: str = "cpu"  # Change to "cuda" if you have GPU

    # Document Processing - Optimized for speed
    chunk_size: int = 500  # Reduced for faster processing
    chunk_overlap: int = 50  # Minimal overlap
    max_docs_for_context: int = 2  # Reduced for speed

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
    log_level: str = os.environ.get("LOG_LEVEL", "INFO")  # Added default value
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
        # Create necessary directories
        self.create_directories()

    def create_directories(self):
        """Create necessary directories if they don't exist"""
        directories = [self.cache_dir, self.log_dir]
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)

    @property
    def cache_path(self) -> Path:
        """Get the cache directory path"""
        return Path(self.cache_dir)

    @property
    def log_path(self) -> Path:
        """Get the log directory path"""
        return Path(self.log_dir)

# Global settings instance
settings = Settings()

# Validate OpenRouter API key
if not settings.openrouter_api_key:
    print("⚠️  WARNING: OPENROUTER_API_KEY not found in environment variables!")
    print("   The system will work with HuggingFace models only.")
    print("   For better performance, get a free API key from https://openrouter.ai")
else:
    print(f"✅ OpenRouter API key found: {settings.openrouter_api_key[:5]}...{settings.openrouter_api_key[-5:]}")
    # For testing, we'll use a mock response instead of calling the actual API
    # This will prevent errors when the API key is invalid or the API is unavailable

# Validate embedding device
if settings.embedding_device == "cuda" and torch and not torch.cuda.is_available():
    print("⚠️  WARNING: CUDA selected as embedding device, but no GPU found.")
    print("   Changing embedding device to CPU.")
    settings.embedding_device = "cpu"
elif settings.embedding_device == "cuda" and not torch:
    print("⚠️  WARNING: CUDA selected but torch not installed.")
    print("   Changing embedding device to CPU.")
    settings.embedding_device = "cpu"