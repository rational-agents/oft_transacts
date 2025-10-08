from fastapi import APIRouter
from sqlalchemy import text
from app.db.base import engine

@app.get("/healthz")
async def healthz():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return {"ok": True}