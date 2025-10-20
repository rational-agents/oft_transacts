# backend/src/app/main.py
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings

# at top
import logging
from pathlib import Path
from app.db.base import engine

settings = get_settings()
app = FastAPI(title="OFT Transacts API")

# --- CORS: config-driven allow-list (keeps localhost:5173 by default) ---
allow_origins = [
    o.strip()
    for o in getattr(settings, "allowed_origins", "http://localhost:5173").split(",")
    if o.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"], # allow all headers
)

@app.post("/logout")
def logout():
    resp = Response(status_code=204)
    resp.headers["Clear-Site-Data"] = '"cache", "cookies", "storage", "executionContexts"'
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return resp

# Log DB URL on startup (after app is created)
@app.on_event("startup")
async def log_db_url():
    logger = logging.getLogger("uvicorn.error")
    url = str(engine.url)
    logger.info(f"DB URL in use: {url}")
    if engine.url.drivername.startswith("sqlite"):
        db_path = engine.url.database  # absolute path
        logger.info(f"SQLite path exists? {Path(db_path).exists()} path={db_path}")

# --- Security headers (CSP, etc.) ---
OIDC_ISSUER = getattr(settings, "oidc_issuer", "")
# Default CSP for the API
CSP_DEFAULT = (
    "default-src 'self'; "
    "script-src 'self'; "
    "style-src 'self'; "
    "img-src 'self' data:; "
    f"connect-src 'self' {OIDC_ISSUER}; "
    "frame-ancestors 'none'; "
    "base-uri 'none'; "
    "object-src 'none'"
)
# Relaxed CSP for Swagger UI (/docs) to allow CDN assets
CSP_DOCS = (
    "default-src 'self'; "
    "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
    "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
    "img-src 'self' data: https://fastapi.tiangolo.com; "
    "font-src 'self' data: https://cdn.jsdelivr.net; "
    f"connect-src 'self' {OIDC_ISSUER}; "
    "frame-ancestors 'none'; "
    "base-uri 'none'; "
    "object-src 'none'"
)

@app.middleware("http")
async def security_headers(req, call_next):
    resp: Response = await call_next(req)
    # Apply a relaxed CSP only for the docs UI
    if req.url.path.startswith("/docs"):
        resp.headers["Content-Security-Policy"] = CSP_DOCS
    else:
        resp.headers["Content-Security-Policy"] = CSP_DEFAULT
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["Referrer-Policy"] = "no-referrer"
    resp.headers["Permissions-Policy"] = "geolocation=()"
    return resp

# --- Include routers AFTER app is created/configured ---
from app.api import accounts, users, transacts
app.include_router(accounts.router)
app.include_router(users.router)
app.include_router(transacts.router)