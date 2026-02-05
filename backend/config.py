from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Optional
import os


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    # Supabase
    supabase_url: str = ""
    supabase_key: str = ""
    supabase_service_key: str = ""
    
    # OpenAI
    openai_api_key: str = ""
    
    # App
    app_env: str = "development"
    debug: bool = True
    secret_key: str = "dev-secret-key"
    
    # Embedding
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536
    
    # Chat
    chat_model: str = "gpt-3.5-turbo"
    max_tokens: int = 2048
    temperature: float = 0.7
    
    # Chunking
    chunk_size: int = 1000
    chunk_overlap: int = 200


_settings = None

def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
