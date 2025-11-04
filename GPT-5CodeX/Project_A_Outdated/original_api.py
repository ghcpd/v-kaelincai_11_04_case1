"""Outdated API simulation demonstrating schema drift and brittle error handling."""

from __future__ import annotations

import json
import time
from typing import Any, Dict, List


class OutdatedAPI:
    """Simulates the deprecated `/v1/user` endpoint with a legacy schema."""

    def __init__(self) -> None:
        self._users = {
            "user-001": {
                "userId": "user-001",
                "name": "Legacy User",
                "mail": "legacy.user@example.com",
                "settings": {"locale": "en-US", "email": True, "sms": False},
            },
            "user-999": {
                "userId": "user-999",
                "name": "High Volume User",
                "settings": {"locale": "en-GB", "email": False, "sms": True},
            },
        }

    def call(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a synthetic API request with poor validation and unstable schema."""
        endpoint = request.get("endpoint")
        payload: Dict[str, Any] = request.get("payload", {})

        # Artificial latency to mimic slow legacy handler.
        time.sleep(0.03)

        if endpoint != "/v1/user":
            return {
                "status": "error",
                "message": "endpoint not supported",
                "code": "legacy-404",
            }

        user_id = payload.get("user_id")
        if not user_id:
            return {
                "status": "error",
                "message": "missing identifier",
                # Legacy implementation leaks HTTP details inside JSON string.
                "http_status": "400 Bad Request",
            }

        token = payload.get("token")
        if token is None:
            # Token validation is skipped entirely, causing security gaps.
            pass

        record = self._users.get(user_id)
        if not record:
            return {
                "status": "error",
                "message": "user not found",
                "code": 404,
            }

        # Legacy schema uses mixed casing and flattens preferences.
        response = {
            "status": "ok",
            "data": record,
        }

        if payload.get("include_preferences"):
            # Preferences appended inconsistently.
            response["preferences"] = {
                "prefLocale": record["settings"].get("locale"),
                "notify": [record["settings"].get("email"), record["settings"].get("sms")],
            }

        return response

    def bulk_call(self, requests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process a batch of requests, surfacing duplicated latency and error noise."""
        results: List[Dict[str, Any]] = []
        for request in requests:
            results.append(self.call(request))
        return results


def run_from_cli(payload_path: str) -> None:
    api = OutdatedAPI()
    try:
        with open(payload_path, "r", encoding="utf-8") as handle:
            requests = json.load(handle)
    except FileNotFoundError:
        raise SystemExit(f"Cannot open payload file: {payload_path}")

    responses = api.bulk_call(requests)
    print(json.dumps(responses, indent=2))


if __name__ == "__main__":
    run_from_cli("../test_data.json")
