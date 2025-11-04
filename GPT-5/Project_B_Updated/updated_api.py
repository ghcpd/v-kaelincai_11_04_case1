"""Updated API implementation.
Endpoints:
- /v2/profile  (primary)
- /v1/user      (backward compatible alias -> transformed output when Accept: application/vnd.legacy+json)
Improvements:
- Unified schema: {"status": "ok", "data": {...}, "meta": {"version": "v2", "latency_ms": int}}
- Consistent JSON error objects {"status": "error", "error": {"code": int, "message": str}}
- Pydantic validation for input payload
- Sanitization of name (strip script tags)
- Performance: removed artificial sleeps & inefficient expansions
- Backward compatibility: legacy shape preserved when requested
"""
from __future__ import annotations
from typing import Optional, Dict, Any, Tuple
from pydantic import BaseModel, Field, ValidationError
import time
import re

PROFILE_ENDPOINT = "/v2/profile"
LEGACY_ENDPOINT = "/v1/user"  # still routable
VALID_TOKENS = {"token-123", "legacy-abc", "token-new"}
SCRIPT_TAG_RE = re.compile(r"<script.*?>.*?</script>", re.IGNORECASE | re.DOTALL)


class ProfileIn(BaseModel):
    id: int = Field(ge=0)
    name: str = Field(min_length=1, max_length=200)
    email: Optional[str] = Field(default=None)
    preferences: Optional[Dict[str, Any]] = Field(default=None)
    nested: Optional[Dict[str, Any]] = Field(default=None)

    def sanitize(self) -> "ProfileIn":
        clean_name = SCRIPT_TAG_RE.sub("", self.name)
        object.__setattr__(self, "name", clean_name)
        return self


def _build_response(data: dict, latency_ms: int) -> dict:
    return {
        "status": "ok",
        "data": data,
        "meta": {"version": "v2", "latency_ms": latency_ms},
    }


def _error(code: int, message: str) -> Tuple[int, dict]:
    return code, {"status": "error", "error": {"code": code, "message": message}}


def _to_legacy(data: dict) -> dict:
    # Flatten unified schema into legacy form
    legacy = {
        "id": data["id"],
        "name": data["name"],
    }
    if data.get("email") is not None:
        legacy["email"] = data["email"]
    return legacy


def handle_request(path: str, payload: dict, headers: dict) -> Tuple[int, dict]:
    start = time.time()
    if path not in {PROFILE_ENDPOINT, LEGACY_ENDPOINT}:
        return _error(404, "not_found")

    token = headers.get("Authorization")
    if not token or token not in VALID_TOKENS:
        return _error(401, "unauthorized")

    # Validate & sanitize
    try:
        model = ProfileIn(**payload).sanitize()
    except ValidationError as ve:
        return _error(400, f"invalid_payload: {ve.errors()[0]['msg']}")

    data = model.dict()
    # Efficient: direct dict usage; potential heavy nested structures are passed through unchanged
    latency_ms = int((time.time() - start) * 1000)
    unified = _build_response(data, latency_ms)

    # Legacy Accept negotiation
    accept_header = headers.get("Accept", "")
    if path == LEGACY_ENDPOINT and "application/vnd.legacy+json" in accept_header:
        legacy_body = _to_legacy(data)
        legacy_body["latency_ms"] = latency_ms
        return 200, legacy_body
    if path == LEGACY_ENDPOINT:
        # Encourage upgrade: still serve unified wrapper
        return 200, unified
    return 200, unified


def batch(requests: list[dict]) -> list[dict]:
    return [
        {"status": handle_request(r.get("path", ""), r.get("payload", {}), r.get("headers", {}))[0],
         "body": handle_request(r.get("path", ""), r.get("payload", {}), r.get("headers", {}))[1]}
        for r in requests
    ]

if __name__ == "__main__":
    demo = {"path": PROFILE_ENDPOINT, "payload": {"id": 1, "name": "Alice", "email": "a@x"}, "headers": {"Authorization": "token-new"}}
    from pprint import pprint
    pprint(handle_request(**demo))
