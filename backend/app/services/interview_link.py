import base64
import hashlib
import hmac
import json
import time
from typing import Any, Dict

from fastapi import HTTPException
from app.config.config import Settings


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def _get_secret() -> str:
    secret = Settings.INTERVIEW_LINK_SECRET or Settings.SUPABASE_KEY
    if not secret:
        raise HTTPException(status_code=500, detail="Interview link secret is not configured")
    return secret


def generate_interview_token(payload: Dict[str, Any], ttl_seconds: int | None = None) -> str:
    expires_at = int(time.time()) + int(ttl_seconds or Settings.INTERVIEW_LINK_TTL_SECONDS)

    body = dict(payload)
    body["exp"] = expires_at

    body_bytes = json.dumps(body, separators=(",", ":"), ensure_ascii=False).encode()
    body_b64 = _b64url_encode(body_bytes)

    signature = hmac.new(_get_secret().encode(), body_b64.encode(), hashlib.sha256).digest()
    signature_b64 = _b64url_encode(signature)

    return f"{body_b64}.{signature_b64}"


def verify_interview_token(token: str) -> Dict[str, Any]:
    try:
        body_b64, signature_b64 = token.split(".", 1)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid interview link")

    expected_signature = hmac.new(_get_secret().encode(), body_b64.encode(), hashlib.sha256).digest()
    expected_b64 = _b64url_encode(expected_signature)

    if not hmac.compare_digest(expected_b64, signature_b64):
        raise HTTPException(status_code=401, detail="Invalid interview link signature")

    try:
        payload = json.loads(_b64url_decode(body_b64).decode())
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid interview link payload")

    expires_at = int(payload.get("exp", 0))
    if expires_at < int(time.time()):
        raise HTTPException(status_code=410, detail="Interview link expired")

    return payload
