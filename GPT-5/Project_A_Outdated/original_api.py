"""Outdated API implementation.
Endpoint: /v1/user
Issues demonstrated:
- Inconsistent schema (sometimes missing 'email', no versioning metadata)
- Inefficient processing (unnecessary list expansions, sleeps)
- Poor error handling (generic exceptions, unclear status codes)
- No input validation (accepts malicious name strings)
- Mismatched response types for errors (string vs JSON)
"""
from __future__ import annotations
import time
import json
import re

LEGACY_ENDPOINT = "/v1/user"
VALID_TOKENS = {"token-123", "legacy-abc"}

SCRIPT_TAG_RE = re.compile(r"<script.*?>.*?</script>", re.IGNORECASE | re.DOTALL)


def _simulate_latency(payload: dict) -> None:
    # Artificial latency: scale with nested keys count
    nested_factor = sum(isinstance(v, dict) for v in payload.values())
    time.sleep(0.01 + 0.01 * nested_factor)


def _inefficient_expand(data: dict) -> list:
    # Wasteful expansion just to show inefficiency
    expanded = []
    for k, v in data.items():
        expanded.append((k, v))
        expanded.extend([(k, v) for _ in range(3)])  # redundant
    return expanded


def sanitize_name(name: str) -> str:
    # In outdated version we do NOT sanitize properly (bug) - leaving potential script fragments.
    return name


def handle_request(path: str, payload: dict, headers: dict) -> tuple[int, dict | str]:
    start = time.time()
    if path != LEGACY_ENDPOINT:
        return 404, {"error": "not_found"}

    token = headers.get("Authorization")
    if not token or token not in VALID_TOKENS:
        return 401, "unauthorized"  # Inconsistent error (string)

    # Missing required field handling: assumes 'name' exists
    try:
        name = payload.get("name")  # could be None
        email = payload.get("email")  # optional; may be missing causing downstream mismatch
        # Inefficient processing
        _simulate_latency(payload)
        _inefficient_expand(payload)
    except Exception as e:
        return 500, f"server_error:{e}"  # Leaks internal details

    # Build inconsistent response (sometimes missing email key entirely)
    response = {
        "id": payload.get("id", "unknown"),
        "name": sanitize_name(name if name is not None else "(none)"),
    }
    if email is not None:
        response["email"] = email
    # No version metadata, no uniform wrapper
    latency_ms = int((time.time() - start) * 1000)
    response["latency_ms"] = latency_ms
    return 200, response


def legacy_batch(requests: list[dict]) -> list[dict]:
    results = []
    for r in requests:
        status, body = handle_request(r.get("path", ""), r.get("payload", {}), r.get("headers", {}))
        results.append({"status": status, "body": body})
    return results

if __name__ == "__main__":
    # Simple manual run example
    demo = {"path": LEGACY_ENDPOINT, "payload": {"id": 1, "name": "Alice", "email": "a@x"}, "headers": {"Authorization": "token-123"}}
    print(json.dumps(handle_request(**demo), indent=2))
