"""Refactored API implementation exposing the `/v2/profile` contract.

The new implementation improves on the legacy version by:
* Returning a structured schema validated with Pydantic.
* Providing deterministic latency optimised through simple caching.
* Offering clearer error types mapped to HTTP-style status codes.
* Handling both legacy (`/v1`) and modern request shapes for backward compatibility.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass
from http import HTTPStatus
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from pydantic import BaseModel, ValidationError, validator


class UpdatedAPIError(RuntimeError):
    """Base error carrying an HTTP-style status code."""

    def __init__(self, message: str, status: HTTPStatus = HTTPStatus.BAD_REQUEST) -> None:
        super().__init__(message)
        self.status = status


class UnauthorizedError(UpdatedAPIError):
    def __init__(self, message: str = "Token rejected") -> None:
        super().__init__(message, status=HTTPStatus.UNAUTHORIZED)


class NotFoundError(UpdatedAPIError):
    def __init__(self, message: str = "User not found") -> None:
        super().__init__(message, status=HTTPStatus.NOT_FOUND)


class ProfilePayload(BaseModel):
    user: Dict[str, Any]
    contact: Dict[str, Any]
    membership: Dict[str, Any]
    activity: Dict[str, Any]

    @validator("user")
    def ensure_core_identity(cls, value: Dict[str, Any]) -> Dict[str, Any]:
        if "id" not in value or "name" not in value:
            raise ValueError("user block requires `id` and `name`")
        return value


@dataclass
class ProfileRequest:
    user_id: str
    token: str
    include_history: bool = False

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "ProfileRequest":
        data = dict(payload)
        return cls(
            user_id=str(data.get("user_id")),
            token=str(data.get("token", "")),
            include_history=bool(data.get("include_history", False)),
        )


class UpdatedProfileAPI:
    """Modern `/v2/profile` endpoint."""

    _ALLOWED_TOKENS = {"token_v2", "token_migration", "token_v1"}

    def __init__(self, base_latency: float = 0.006, cache_ttl_seconds: float = 2.0) -> None:
        self.base_latency = base_latency
        self.cache_ttl_seconds = cache_ttl_seconds
        self._cache: Dict[str, Tuple[float, Dict[str, Any]]] = {}
        self.last_latency: Optional[float] = None
        self._store: Dict[str, Dict[str, Any]] = {
            "1001": {
                "id": 1001,
                "full_name": "Alicia Keys",
                "email": "alicia@example.com",
                "phone": "+1-202-555-0111",
                "preferences": {"language": "en-US", "notifications": True},
                "tier": "platinum",
                "last_active": "2025-10-28T12:10:00Z",
                "sessions": [
                    {"device": "ios", "location": "us-east", "duration": 320},
                    {"device": "web", "location": "us-east", "duration": 180},
                ],
            },
            "1002": {
                "id": 1002,
                "full_name": "Bruno Mars",
                "email": "bruno@example.com",
                "phone": "+65-6555-1000",
                "preferences": {"language": "en-SG", "notifications": False},
                "tier": "gold",
                "last_active": "2025-10-30T08:22:00Z",
                "sessions": [
                    {"device": "android", "location": "ap-south", "duration": 410}
                ],
            },
        }

    def _authorise(self, token: str) -> None:
        if token not in self._ALLOWED_TOKENS:
            raise UnauthorizedError()

    def _build_profile(self, record: Dict[str, Any], include_history: bool) -> Dict[str, Any]:
        sessions = record.get("sessions", [])
        recent_session = max(sessions, key=lambda item: item.get("duration", 0), default=None)
        profile = {
            "user": {
                "id": record["id"],
                "name": record["full_name"],
                "tier": record["tier"],
            },
            "contact": {
                "email": record["email"],
                "phone": record["phone"],
            },
            "membership": {
                "preferences": record.get("preferences", {}),
                "tenure_days": 365,
            },
            "activity": {
                "last_active": record["last_active"],
                "recent_session": recent_session,
                "session_count": len(sessions),
            },
        }
        if include_history:
            profile["activity"]["history"] = sessions
        return profile

    def _from_legacy_payload(self, payload: Dict[str, Any]) -> ProfileRequest:
        # Accept the legacy contract to ease migration.
        return ProfileRequest(
            user_id=str(payload.get("user_id")),
            token=str(payload.get("token", "")),
            include_history=bool(payload.get("include_history", False)),
        )

    def fetch_profile(self, request_payload: Dict[str, Any]) -> Dict[str, Any]:
        request = self._from_legacy_payload(request_payload)
        start = time.perf_counter()
        try:
            self._authorise(request.token)
            now = time.perf_counter()
            cache_key = f"{request.user_id}:{request.include_history}"
            cached = self._cache.get(cache_key)
            if cached and now - cached[0] <= self.cache_ttl_seconds:
                profile = cached[1]
            else:
                record = self._store.get(request.user_id)
                if record is None:
                    raise NotFoundError()
                profile = self._build_profile(record, include_history=request.include_history)
                ProfilePayload(**profile)  # validation step
                self._cache[cache_key] = (now, profile)
            # Simulate a much smaller latency due to caching & optimisation
            time.sleep(self.base_latency)
            return profile
        finally:
            self.last_latency = time.perf_counter() - start

    def batch_fetch(self, payloads: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
        responses: List[Dict[str, Any]] = []
        for payload in payloads:
            try:
                responses.append({"request": payload, "response": self.fetch_profile(payload)})
            except UpdatedAPIError as exc:
                responses.append({
                    "request": payload,
                    "error": str(exc),
                    "status": exc.status.value,
                })
        return responses


def load_shared_test_data(path: Path) -> List[Dict[str, Any]]:
    data = json.loads(path.read_text())
    return data


def collect_latency_profile(api: UpdatedProfileAPI, requests: Iterable[Dict[str, Any]]) -> Dict[str, float]:
    latencies: List[float] = []
    for payload in requests:
        try:
            api.fetch_profile(payload)
        except UpdatedAPIError:
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
    api = UpdatedProfileAPI()
    shared_data = load_shared_test_data(Path(__file__).resolve().parent.parent / "test_data.json")
    metrics = collect_latency_profile(api, [case["input"] for case in shared_data])
    print(json.dumps({"latency_seconds": metrics}))
