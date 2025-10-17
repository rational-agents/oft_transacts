from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from app.core.config import get_settings

# ADD THIS IMPORT so all models are registered
import app.db.models  # noqa: F401

settings = get_settings()

# Connection pool settings for PostgreSQL to prevent aborted transaction errors
pool_kwargs = {}
if not settings.database_url.startswith("sqlite"):
    pool_kwargs = {
        "pool_pre_ping": True,          # Test connections before using them
        "pool_recycle": 3600,           # Recycle connections after 1 hour
        "pool_reset_on_return": "rollback",  # Always rollback when returning to pool
    }

engine = create_engine(
    settings.database_url,
    future=True,
    connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {},
    **pool_kwargs
)

# Enable FK constraints in SQLite
@event.listens_for(engine, "connect")
def _sqlite_pragma(dbapi_connection, _):
    try:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()
    except Exception:
        pass

# For PostgreSQL: ensure aborted transactions are rolled back when connection returns to pool
@event.listens_for(engine, "checkin")
def _on_checkin(dbapi_connection, connection_record):
    """Rollback any aborted transactions before returning connection to pool."""
    if not settings.database_url.startswith("sqlite"):
        try:
            # Check if transaction is in failed state and rollback
            dbapi_connection.rollback()
        except Exception:
            pass

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, future=True)

@contextmanager
def session_scope() -> Session:
    s = SessionLocal()
    try:
        yield s
        s.commit()
    except:
        s.rollback()
        raise
    finally:
        s.close()