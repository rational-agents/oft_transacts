from __future__ import annotations
import time
from typing import Any, Dict
import httpx
from jose import jwt
from app.core.config import get_settings

settings = get_settings()
DISCOVERY_URL = f"{settings.oidc_issuer}/.well-known/openid-configuration"
_cache: Dict[str, Dict[str, Any]] = {}

async def _get_openid_config() -> Dict[str, Any]:
    now = time.time()
    if (c := _cache.get("openid")) and c["exp"] > now:
        return c["val"]
    async with httpx.AsyncClient(timeout=5.0) as c:
        r = await c.get(DISCOVERY_URL)
        r.raise_for_status()
        data = r.json()
    _cache["openid"] = {"val": data, "exp": now + 3600}
    return data

async def _get_jwks() -> Dict[str, Any]:
    now = time.time()
    if (c := _cache.get("jwks")) and c["exp"] > now:
        return c["val"]
    cfg = await _get_openid_config()
    async with httpx.AsyncClient(timeout=5.0) as c:
        r = await c.get(cfg["jwks_uri"])
        r.raise_for_status()
        data = r.json()
    _cache["jwks"] = {"val": data, "exp": now + 3600}
    return data

async def verify_jwt_and_get_claims(token: str) -> Dict[str, Any]:
    cfg = await _get_openid_config()
    jwks = await _get_jwks()
    header = jwt.get_unverified_header(token)
    kid = header.get("kid")
    key = next((k for k in jwks["keys"] if k.get("kid") == kid), None)
    if not key:
        raise ValueError("Signing key not found")
    claims = jwt.decode(
        token,
        key,                         # python-jose accepts JWK dicts
        algorithms=[key.get("alg", "RS256")],
        audience=(settings.oidc_audience or None),
        issuer=cfg["issuer"],
        options={"verify_at_hash": False},
    )
    # OIDC defines `sub` (subject) as the stable end-user id
    return claims