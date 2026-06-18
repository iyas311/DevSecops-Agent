"""
Configuration module for CISA using pydantic-settings.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    AWS_REGION: str = "us-east-1"
    BEDROCK_MODEL_ID: str = "amazon.nova-pro-v1:0"
    BEDROCK_KNOWLEDGE_BASE_ID: str | None = None
    
    BACKEND_PORT: int = 8000
    BACKEND_HOST: str = "0.0.0.0"
    
    MAX_TOOL_ITERATIONS: int = 5
    BEDROCK_TEMPERATURE: float = 0.3
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
