# backend/src/app/deps.py
from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.base import session_scope
from app.db.models.users import User
from app.core.oidc import verify_jwt_and_get_claims

# ---- DB session dependency (unchanged behavior) ----
def get_db() -> Generator[Session, None, None]:
    # Same pattern you already use: one SQLAlchemy Session per request,
    # closed automatically after the response.
    with session_scope() as s:
        yield s

# ---- Auth boundary: Bearer token -> claims -> user_id ----
bearer = HTTPBearer(auto_error=True)  # standard FastAPI security helper

async def get_current_user_id(
    creds: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db),
) -> int:
    """
    Verify the incoming Bearer JWT against your IdP (Okta) via JWKS,
    then map OIDC `sub`/`email` to your internal user and return user_id.
    """
    token = creds.credentials
    try:
        claims = await verify_jwt_and_get_claims(token)
    except Exception:
        # Token missing/invalid/expired, wrong issuer/audience, bad signature, etc.
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    sub = claims.get("sub")
    if not sub:
        raise HTTPException(status_code=401, detail="Missing sub")

    # Minimal auto-provision: prefer email if present; fall back to sub
    email = claims.get("email", f"sub:{sub}")
    user = db.scalar(select(User).where(User.email == email))
    if not user:
        user = User(email=email, username=claims.get("name", sub))
        db.add(user)
        db.flush()

    return user.user_id