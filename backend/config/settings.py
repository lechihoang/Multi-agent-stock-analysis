from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    nvidia_api_key: str
    nvidia_base_url: str = "https://integrate.api.nvidia.com/v1"

    nvidia_model: str = "meta/llama-3.3-70b-instruct"

    tavily_api_key: str

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    vite_api_url: str = "http://localhost:8000"

    max_requests_per_minute: int = 40

    llm_temperature: float = 0.2
    llm_max_tokens: int = 8192
    llm_top_p: float = 0.9

    class Config:
        env_file = ".env"
        extra = "ignore"

    @property
    def crewai_model(self) -> str:
        return f"nvidia_nim/{self.nvidia_model}"

    @property
    def openai_model(self) -> str:
        return self.nvidia_model


settings = Settings()
