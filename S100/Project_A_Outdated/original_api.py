"""Legacy API module demonstrating outdated schema and inefficient behavior.

This module intentionally keeps the old `/v1/user` endpoint implementation to
highlight the kinds of problems the migration to `/v2/profile` is meant to fix.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


class LegacyAPIError(RuntimeError):
    """Raised when the legacy API cannot fulfill a request."""


@dataclass
class LegacyRequest:
    """Represents the legacy request contract.

    The historic `/v1/user` endpoint only accepts string identifiers and a static
    token value. Any deviation returns a vague error message."""

    user_id: str
    token: str

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "LegacyRequest":
        return cls(user_id=str(payload.get("user_id")), token=str(payload.get("token")))


class LegacyUserAPI:
    """Outdated `/v1/user` endpoint implementation.

    Notable issues that the new implementation must correct:
    * Returns flattened fields that do not match the unified profile schema.
    * Serialises integers as strings, causing downstream type mismatches.
    * Sleeps on every request to simulate heavy, blocking database calls.
    * Swallows domain-specific errors into coarse RuntimeErrors.
    """

    _RESPONSE_TEMPLATE = {"id", "name", "email", "lastActive", "metadata"}

    def __init__(self, artificial_latency: float = 0.045) -> None:
        self.artificial_latency = artificial_latency
        self.last_latency: Optional[float] = None
        # Simulated backing store illustrating the stale schema footprint.
        self._store: Dict[str, Dict[str, Any]] = {
            "1001": {
                "id": 1001,
                "name": "Alicia Keys",
                "email": "alicia.legacy@example.com",
                "last_active": "2025-10-18T10:50:00Z",
                "metadata": {"tier": "gold", "region": "us-east"},
            },
            "1002": {
                "id": 1002,
                "name": "Bruno Mars",
                "email": "bruno.legacy@example.com",
                "last_active": "2025-10-09T07:15:00Z",
                "metadata": {"tier": "silver", "region": "ap-south"},
            },
        }

    def _authorise(self, token: str) -> None:
        # Hard-coded token demonstrates the brittle security posture.
        if token != "token_v1":
            raise LegacyAPIError("Legacy authorization failed: token rejected")

    def fetch_user(self, request: LegacyRequest) -> Dict[str, Any]:
        start = time.perf_counter()
        try:
            self._authorise(request.token)
            record = self._store.get(request.user_id)
            if record is None:
                raise LegacyAPIError(f"User {request.user_id} is unavailable in /v1")

            # Simulate expensive synchronous IO.
            time.sleep(self.artificial_latency)

            # Return flattened schema with snake/camel case inconsistencies.
            return {
                "id": str(record["id"]),  # cast to str, breaking numeric expectations
                "name": record["name"],
                "email": record["email"],
                "lastActive": record["last_active"],
                # Metadata leaks internal keys without validation
                "metadata": record.get("metadata", {}),
            }
        finally:
            self.last_latency = time.perf_counter() - start

    def batch_fetch(self, requests: Iterable[LegacyRequest]) -> List[Dict[str, Any]]:
        responses: List[Dict[str, Any]] = []
        for req in requests:
            try:
                responses.append({"request": req.__dict__, "response": self.fetch_user(req)})
            except LegacyAPIError as exc:
                responses.append({"request": req.__dict__, "error": str(exc)})
        return responses


def load_requests(path: Path) -> List[LegacyRequest]:
    data = json.loads(path.read_text())
    return [LegacyRequest.from_dict(item) for item in data]


def collect_latency_profile(api: LegacyUserAPI, requests: Iterable[LegacyRequest]) -> Dict[str, float]:
    latencies: List[float] = []
    for req in requests:
        try:
            api.fetch_user(req)
        except LegacyAPIError:
            # Even failed lookups incur latency.
            pass
        if api.last_latency is not None:
            latencies.append(api.last_latency)
    if not latencies:
        return {"min": 0.0, "max": 0.0, "avg": 0.0}
    return {
        "min": min(latencies),
        "max": max(latencies),
        "avg": sum(latencies) / len(latencies),
    }


if __name__ == "__main__":
    input_path = Path(__file__).with_name("input_data.json")
    api = LegacyUserAPI()
    requests = load_requests(input_path)
    metrics = collect_latency_profile(api, requests)
    print(json.dumps({"latency_seconds": metrics}))
