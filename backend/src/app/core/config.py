from functools import lru_cache
from pydantic import BaseSettings

class Settings(BaseSettings):
    database_url: str

    class Config:
        env_prefix = ""
        case_sensitive = False
@lru_cache
def get_settings() -> Settings:
    return Settings(_env_file=".env", _env_file_encoding="utf-8")