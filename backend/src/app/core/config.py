# backend/src/app/core/config.py
from functools import lru_cache
from pydantic import BaseSettings
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[3]  # bullet proof reference to the .env file location

class Settings(BaseSettings):
    # existing
    database_url: str = f"sqlite:///{BACKEND_DIR / 'var' / 'oft.sqlite3'}" # more bullet proofing

    # new for OIDC + PKCE
    oidc_issuer: str    # e.g., https://integrator-1280701.okta.com/oauth2/default
    oidc_audience: str = "" # set if your API enforces a specific 'aud' claim
    allowed_origins: str = "http://localhost:5173"  # comma-separated list
    # Pagination settings
    transacts_page_size: int = 10  # number of transactions per page

    class Config:
        # keep your original behavior: read from a .env in backend/ working dir
        env_prefix = ""
        case_sensitive = False
        env_file = str(BACKEND_DIR / ".env")
        env_file_encoding = "utf-8"

    @property
    def allowed_origins_list(self) -> list[str]:
        # FastAPI CORSMiddleware needs a list[str]
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

@lru_cache
def get_settings() -> Settings:
    return Settings()