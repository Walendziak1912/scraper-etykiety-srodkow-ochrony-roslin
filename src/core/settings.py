from functools import lru_cache
from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from src.utils.env_variables import get_env_variable_value

class Settings(BaseSettings):
    version: str = "1.0.3"
    logger_name: str = Field(validation_alias=AliasChoices("LOGGER_NAME"),default="FB")
    http_connect_timeout_sec: int = Field(validation_alias=AliasChoices("HTTP_CONNECT_TIMEOUT_SEC"),default=5)
    http_total_timeout_sec: int = Field(validation_alias=AliasChoices("HTTP_TOTAL_TIMEOUT_SEC"),default=30)

    console_log_level: str = Field(
        default="INFO",
        validation_alias=AliasChoices("CONSOLE_LOG_LEVEL"),
    ) 
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        frozen=True
    )

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
