from typing import Generator
from sqlalchemy.orm import Session
from app.db.base import session_scope

def get_db() -> Generator[Session, None, None]:
    with session_scope() as s:
        yield s