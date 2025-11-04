"""Legacy API simulation exposing outdated endpoint and schema mismatches."""
from __future__ import annotations

import json
import random
import time
from typing import Any, Dict, Iterable, Tuple


class LegacySchemaMismatch(Exception):
    """Raised when the legacy API response does not match the expected schema."""


class LegacyAuthenticationError(Exception):
    """Raised when the legacy API receives an invalid token."""


class LegacyUserAPI:
    """Simulates a deprecated `/v1/user` endpoint with brittle schema handling."""

    BASE_PATH = "/v1/user"
    SUPPORTED_VERSIONS = {"2020-09"}

    def __init__(self, datastore: Dict[str, Dict[str, Any]]) -> None:
        self._datastore = datastore

    def fetch_user(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate a slow, schema-inconsistent response."""
        self._validate_headers(request)
        user_id = request.get("userId")
        include_history = request.get("includeHistory", "false")
        history_depth = int(request.get("historyDepth", 1))

        latency = random.uniform(0.085, 0.13)
        time.sleep(latency)

        record = self._datastore.get(user_id)
        if record is None:
            return {
                "status": "404",
                "payload": {
                    "errorMessage": "user not found",
                    "endpoint": self.BASE_PATH,
                },
                "elapsedMs": latency * 1000,
            }

        first, last = self._split_name(record.get("full_name", ""))
        body = {
            "status": "200",  # string instead of numeric value
            "payload": {
                "user": {
                    "first_name": first,
                    "last_name": last,
                    "last_seen": str(record.get("last_seen")),
                    "contact": {
                        "emailAddress": record.get("email", ""),
                        "phoneNumber": record.get("phone"),
                    },
                    # History flag returned as string even when caller expects array
                    "history": self._render_history(record.get("history", []), include_history, history_depth),
                }
            },
            "meta": {
                "schemaVersion": "legacy-1",
                "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "durationMs": latency * 1000,
            },
        }
        return body

    def _validate_headers(self, request: Dict[str, Any]) -> None:
        token = request.get("token")
        version = request.get("apiVersion", "2020-09")
        if token != "legacy-static-token":
            raise LegacyAuthenticationError("Unauthorized token for legacy endpoint")
        if version not in self.SUPPORTED_VERSIONS:
            raise LegacyAuthenticationError(f"Unsupported API version: {version}")

    def validate_schema(self, response: Dict[str, Any]) -> None:
        """Validate legacy response against the new unified schema.

        Raises: LegacySchemaMismatch when the structure deviates from `/v2/profile` expectations.
        """
        required_paths = [
            ("status", int),
            ("payload.profile.id", str),
            ("payload.profile.name.full", str),
            ("payload.profile.contact.primary.email", str),
            ("payload.profile.preferences.timezone", str),
        ]
        for dotted_path, expected_type in required_paths:
            value = self._dig(response, dotted_path)
            if value is None:
                raise LegacySchemaMismatch(f"Missing field `{dotted_path}` in legacy response")
            if not isinstance(value, expected_type):
                raise LegacySchemaMismatch(
                    f"Field `{dotted_path}` expected {expected_type.__name__} but received {type(value).__name__}"
                )

    @staticmethod
    def _dig(payload: Dict[str, Any], dotted_path: str) -> Any:
        parts = dotted_path.split(".")
        node: Any = payload
        for part in parts:
            if not isinstance(node, dict) or part not in node:
                return None
            node = node[part]
        return node

    @staticmethod
    def _split_name(full_name: str) -> Tuple[str, str]:
        if not full_name:
            return "", ""
        pieces = full_name.split(" ")
        if len(pieces) == 1:
            return pieces[0], ""
        return pieces[0], " ".join(pieces[1:])

    @staticmethod
    def _render_history(history: Iterable[Dict[str, Any]], include_flag: Any, depth: int) -> Any:
        if str(include_flag).lower() != "true":
            return "disabled"
        truncated = list(history)[:depth]
        return json.dumps(truncated)


def load_sample_datastore() -> Dict[str, Dict[str, Any]]:
    """Provide static dataset for tests and manual execution."""
    base_history = [
        {"ts": "2024-02-01T12:00:00Z", "action": "login"},
        {"ts": "2024-02-02T11:10:00Z", "action": "password_reset"},
    ]
    return {
        "usr-1001": {
            "full_name": "Harper Lee",
            "email": "harper@example.com",
            "phone": None,
            "last_seen": "2025-10-10T08:50:10Z",
            "history": base_history,
        },
        "usr-1002": {
            "full_name": "Colin Rivera",
            "email": "colin@example.com",
            "phone": "+15550001234",
            "last_seen": "2025-09-20T18:21:04Z",
            "history": base_history,
        },
    }
