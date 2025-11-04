"""Updated API implementation for `/v2/profile` with unified schema and resiliency."""
from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional


class UnifiedSchemaError(Exception):
    """Raised when a response cannot comply with the unified schema."""


@dataclass
class RequestContext:
    user_id: str
    token: str
    request_id: str
    correlation_id: Optional[str]
    include_history: bool
    history_depth: int


class UnifiedProfileAPI:
    BASE_PATH = "/v2/profile"
    SCHEMA_VERSION = "2.0.0"
    SUPPORTED_TOKENS = {"rotating-service-token", "integration-test-token"}

    def __init__(self, datastore: Dict[str, Dict[str, Any]]) -> None:
        self._datastore = datastore

    def get_profile(self, request_payload: Dict[str, Any]) -> Dict[str, Any]:
        ctx = self._parse_context(request_payload)
        start = time.perf_counter()
        record = self._datastore.get(ctx.user_id)
        if record is None:
            return self._build_error(404, "profile not found", start, ctx.request_id)

        response = {
            "status": 200,
            "payload": {
                "profile": {
                    "id": ctx.user_id,
                    "name": {
                        "first": record.get("first_name"),
                        "last": record.get("last_name"),
                        "full": record.get("full_name"),
                    },
                    "contact": {
                        "primary": {
                            "email": record.get("email"),
                            "phone": record.get("phone"),
                        },
                        "secondary": record.get("secondary_contacts", []),
                    },
                    "preferences": {
                        "timezone": record.get("timezone", "UTC"),
                        "language": record.get("language", "en"),
                    },
                    "activity": {
                        "last_seen": record.get("last_seen"),
                        "history": self._recent_history(record.get("history", []), ctx),
                    },
                }
            },
            "meta": {
                "schemaVersion": self.SCHEMA_VERSION,
                "endpoint": self.BASE_PATH,
                "requestId": ctx.request_id,
                "correlationId": ctx.correlation_id,
                "elapsedMs": round((time.perf_counter() - start) * 1000, 3),
            },
        }
        return response

    def process_batch(self, requests: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [self.get_profile(payload) for payload in requests]

    def from_legacy_payload(self, legacy_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Upgrade a legacy `/v1/user` response to the new schema."""
        try:
            user = legacy_payload["payload"]["user"]
        except KeyError as exc:  # pragma: no cover - defensive guard
            raise UnifiedSchemaError("Missing user payload") from exc

        history_raw = user.get("history", "[]")
        history_list: List[Dict[str, Any]]
        if isinstance(history_raw, str):
            history_list = json.loads(history_raw or "[]")
        else:
            history_list = list(history_raw)

        upgraded = {
            "status": int(legacy_payload.get("status", 200)),
            "payload": {
                "profile": {
                    "id": legacy_payload.get("payload", {}).get("user", {}).get("id", "unknown"),
                    "name": {
                        "first": user.get("first_name"),
                        "last": user.get("last_name"),
                        "full": " ".join(filter(None, [user.get("first_name"), user.get("last_name")])),
                    },
                    "contact": {
                        "primary": {
                            "email": user.get("contact", {}).get("emailAddress"),
                            "phone": user.get("contact", {}).get("phoneNumber"),
                        },
                        "secondary": [],
                    },
                    "preferences": {
                        "timezone": "UTC",
                        "language": "en",
                    },
                    "activity": {
                        "last_seen": user.get("last_seen"),
                        "history": history_list,
                    },
                }
            },
            "meta": {
                "schemaVersion": self.SCHEMA_VERSION,
                "endpoint": self.BASE_PATH,
                "requestId": None,
                "correlationId": None,
                "elapsedMs": float(legacy_payload.get("meta", {}).get("durationMs", 0)),
            },
        }
        self.validate_against_reference_schema(upgraded)
        return upgraded

    @staticmethod
    def validate_against_reference_schema(payload: Dict[str, Any]) -> None:
        required_paths = {
            "status": int,
            "payload": dict,
            "payload.profile.id": str,
            "payload.profile.name.full": str,
            "payload.profile.contact.primary.email": (str, type(None)),
            "payload.profile.activity.history": list,
            "meta.elapsedMs": (int, float),
        }
        for dotted_path, expected_type in required_paths.items():
            value = _dig(payload, dotted_path)
            if value is None:
                raise UnifiedSchemaError(f"Missing `{dotted_path}`")
            if isinstance(expected_type, tuple):
                if not isinstance(value, expected_type):
                    allowed = ", ".join(t.__name__ for t in expected_type)
                    raise UnifiedSchemaError(f"`{dotted_path}` expected one of ({allowed}) but got {type(value).__name__}")
            elif not isinstance(value, expected_type):
                raise UnifiedSchemaError(f"`{dotted_path}` expected {expected_type.__name__} but got {type(value).__name__}")

    def _parse_context(self, payload: Dict[str, Any]) -> RequestContext:
        token = payload.get("token", "")
        if token not in self.SUPPORTED_TOKENS:
            raise UnifiedSchemaError("Missing or invalid authentication token")
        include_history = bool(payload.get("includeHistory", True))
        history_depth = int(payload.get("historyDepth", 5))
        if history_depth <= 0:
            history_depth = 1
        return RequestContext(
            user_id=payload.get("userId", ""),
            token=token,
            request_id=payload.get("requestId", f"req-{int(time.time()*1000)}"),
            correlation_id=payload.get("correlationId"),
            include_history=include_history,
            history_depth=history_depth,
        )

    def _recent_history(self, history: Iterable[Dict[str, Any]], ctx: RequestContext) -> List[Dict[str, Any]]:
        if not ctx.include_history:
            return []
        filtered: List[Dict[str, Any]] = []
        for item in history:
            normalized = {
                "timestamp": item.get("ts") or item.get("timestamp"),
                "action": item.get("action"),
                "metadata": item.get("metadata", {}),
            }
            filtered.append(normalized)
            if len(filtered) >= ctx.history_depth:
                break
        return filtered

    def _build_error(self, status_code: int, message: str, start: float, request_id: str) -> Dict[str, Any]:
        elapsed = round((time.perf_counter() - start) * 1000, 3)
        return {
            "status": status_code,
            "payload": {
                "error": {
                    "code": status_code,
                    "message": message,
                }
            },
            "meta": {
                "schemaVersion": self.SCHEMA_VERSION,
                "endpoint": self.BASE_PATH,
                "requestId": request_id,
                "elapsedMs": elapsed,
            },
        }


def load_enhanced_datastore() -> Dict[str, Dict[str, Any]]:
    base_history = [
        {"ts": "2025-10-10T08:50:10Z", "action": "login", "metadata": {"ip": "203.0.113.1"}},
        {"ts": "2025-10-11T04:11:00Z", "action": "profile_update", "metadata": {"field": "email"}},
        {"ts": "2025-10-12T13:22:35Z", "action": "mfa_challenge", "metadata": {"status": "passed"}},
    ]
    return {
        "usr-1001": {
            "full_name": "Harper Lee",
            "first_name": "Harper",
            "last_name": "Lee",
            "email": "harper@example.com",
            "phone": None,
            "secondary_contacts": [
                {"type": "slack", "handle": "@harper"}
            ],
            "timezone": "America/New_York",
            "language": "en",
            "last_seen": "2025-10-10T08:50:10Z",
            "history": base_history,
        },
        "usr-1002": {
            "full_name": "Colin Rivera",
            "first_name": "Colin",
            "last_name": "Rivera",
            "email": "colin@example.com",
            "phone": "+15550001234",
            "secondary_contacts": [],
            "timezone": "America/Los_Angeles",
            "language": "en",
            "last_seen": "2025-09-20T18:21:04Z",
            "history": base_history,
        },
    }


def _dig(payload: Dict[str, Any], dotted_path: str) -> Any:
    node: Any = payload
    for part in dotted_path.split("."):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node
