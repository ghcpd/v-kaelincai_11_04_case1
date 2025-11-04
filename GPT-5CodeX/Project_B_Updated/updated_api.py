"""Updated API simulation with unified schema and stricter validation."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class ApiResponse:
    status_code: int
    body: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> str:
        return json.dumps(
            {
                "status_code": self.status_code,
                "body": self.body,
                "metadata": self.metadata,
            },
            indent=2,
        )


class UpdatedAPI:
    """Implements `/v2/profile` with compatibility routing and validation."""

    def __init__(self) -> None:
        self._profiles = {
            "user-001": {
                "user_id": "user-001",
                "name": "Legacy User",
                "email": "legacy.user@example.com",
                "preferences": {
                    "locale": "en-US",
                    "notifications": {"email": True, "sms": False},
                },
            },
            "user-999": {
                "user_id": "user-999",
                "name": "High Volume User",
                "email": "volume.user@example.com",
                "preferences": {
                    "locale": "en-GB",
                    "notifications": {"email": False, "sms": True},
                },
            },
        }

    def call(self, request: Dict[str, Any]) -> ApiResponse:
        start = time.perf_counter()
        endpoint = request.get("endpoint")
        payload: Dict[str, Any] = request.get("payload", {})

        if endpoint == "/v1/user":
            latency_ms = self._elapsed_ms(start)
            return ApiResponse(
                status_code=301,
                body={"redirect": "/v2/profile", "message": "Endpoint deprecated"},
                metadata={"latency_ms": latency_ms, "deprecated": True},
            )

        if endpoint != "/v2/profile":
            latency_ms = self._elapsed_ms(start)
            return ApiResponse(
                status_code=404,
                body={"error": {"code": "NOT_FOUND", "message": "Endpoint not found"}},
                metadata={"latency_ms": latency_ms},
            )

        validation_error = self._validate(payload)
        if validation_error:
            latency_ms = self._elapsed_ms(start)
            return ApiResponse(
                status_code=validation_error["status_code"],
                body={"error": validation_error["error"]},
                metadata={"latency_ms": latency_ms},
            )

        user_id = payload["user_id"]
        profile = self._profiles.get(user_id)
        if not profile:
            latency_ms = self._elapsed_ms(start)
            return ApiResponse(
                status_code=404,
                body={"error": {"code": "USER_NOT_FOUND", "message": f"No profile for {user_id}"}},
                metadata={"latency_ms": latency_ms},
            )

        include_preferences = bool(payload.get("include_preferences", True))
        response_body = {
            "profile": {
                "user_id": profile["user_id"],
                "name": profile["name"],
                "email": profile["email"],
            }
        }
        if include_preferences:
            response_body["profile"]["preferences"] = profile["preferences"]

        if payload.get("history"):
            response_body["metadata"] = {"history": payload["history"][:50]}

        latency_ms = self._elapsed_ms(start)
        return ApiResponse(
            status_code=200,
            body=response_body,
            metadata={
                "latency_ms": latency_ms,
                "schema_version": "2025.11",
                "cache": False,
            },
        )

    @staticmethod
    def _validate(payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        token = payload.get("token")
        if not token:
            return {
                "status_code": 400,
                "error": {"code": "MISSING_TOKEN", "message": "Authentication token is required"},
            }
        if not token.startswith("valid-"):
            return {
                "status_code": 401,
                "error": {"code": "INVALID_TOKEN", "message": "Provided token is invalid"},
            }

        user_id = payload.get("user_id")
        if not isinstance(user_id, str):
            return {
                "status_code": 400,
                "error": {"code": "INVALID_PAYLOAD", "message": "user_id must be provided"},
            }

        if payload.get("pagination"):
            page_size = payload["pagination"].get("page_size", 100)
            if page_size > 5000:
                return {
                    "status_code": 400,
                    "error": {"code": "PAGE_LIMIT_EXCEEDED", "message": "page_size too large"},
                }
        return None

    @staticmethod
    def _elapsed_ms(start: float) -> float:
        return (time.perf_counter() - start) * 1000


def run_from_cli(payload_path: str) -> None:
    api = UpdatedAPI()
    with open(payload_path, "r", encoding="utf-8") as handle:
        requests = json.load(handle)

    responses = [api.call(request).body for request in requests]
    print(json.dumps(responses, indent=2))


if __name__ == "__main__":
    run_from_cli("../test_data.json")
