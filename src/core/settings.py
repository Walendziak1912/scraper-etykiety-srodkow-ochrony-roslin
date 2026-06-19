from functools import lru_cache
from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    version: str = "1.0.3"
    logger_name: str = Field(validation_alias=AliasChoices("LOGGER_NAME"),default="FB")
    http_connect_timeout_sec: int = Field(validation_alias=AliasChoices("HTTP_CONNECT_TIMEOUT_SEC"),default=5)
    http_total_timeout_sec: int = Field(validation_alias=AliasChoices("HTTP_TOTAL_TIMEOUT_SEC"),default=30)

    console_log_level: str = Field(
        default="INFO",
        validation_alias=AliasChoices("CONSOLE_LOG_LEVEL"),
    )

    download_dir: Path = Field(
        default=Path(".artifacts/downloads"),
        validation_alias=AliasChoices("DOWNLOAD_DIR"),
    )
    scrapy_concurrent_requests: int = Field(
        default=8,
        validation_alias=AliasChoices("SCRAPY_CONCURRENT_REQUESTS"),
    )
    scrapy_download_delay: float = Field(
        default=0.25,
        validation_alias=AliasChoices("SCRAPY_DOWNLOAD_DELAY"),
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
