"""Pytest suite that highlights weaknesses in the legacy API implementation."""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from original_api import OutdatedAPI

ROOT = Path(__file__).resolve().parent
LOG_PATH = ROOT / "log_original.txt"
TEST_DATA_PATH = ROOT.parent / "test_data.json"

# Reset log file to capture the latest run context.
LOG_PATH.write_text("LEGACY API TEST RUN\n", encoding="utf-8")


def _record(issue: str) -> None:
    LOG_PATH.write_text(LOG_PATH.read_text(encoding="utf-8") + issue + "\n", encoding="utf-8")


def _load_case(case_id: str) -> dict:
    data = json.loads(TEST_DATA_PATH.read_text(encoding="utf-8"))
    return next(item for item in data if item["id"] == case_id)


@pytest.fixture()
def api() -> OutdatedAPI:
    return OutdatedAPI()


def test_schema_mismatch(api: OutdatedAPI) -> None:
    case = _load_case("TC01")
    response = api.call({"endpoint": "/v1/user", "payload": case["input_payload"]})
    assert response["status"] == "ok"
    assert "profile" not in response, "Legacy schema unexpectedly matches new profile envelope"
    _record("schema_mismatch: missing profile envelope for TC01")


def test_missing_token_not_enforced(api: OutdatedAPI) -> None:
    case = _load_case("TC03")
    response = api.call({"endpoint": "/v1/user", "payload": case["input_payload"]})
    assert response["status"] == "error"
    assert response.get("http_status") == "400 Bad Request"
    _record("security_gap: token not validated for TC03")


def test_unknown_endpoint_returns_inconsistent_error(api: OutdatedAPI) -> None:
    case = _load_case("TC04")
    response = api.call({"endpoint": case["endpoint"], "payload": case["input_payload"]})
    assert response["status"] == "error"
    assert response.get("code") == "legacy-404"
    _record("routing_issue: TC04 returned legacy-404 instead of redirect")


def test_invalid_token_not_rejected(api: OutdatedAPI) -> None:
    case = _load_case("TC05")
    response = api.call({"endpoint": "/v1/user", "payload": case["input_payload"]})
    assert response["status"] == "ok"
    _record("security_gap: TC05 invalid token accepted by legacy endpoint")


def test_large_payload_not_trimmed(api: OutdatedAPI) -> None:
    case = _load_case("TC02")
    response = api.call({"endpoint": "/v1/user", "payload": case["input_payload"]})
    assert "metadata" not in response
    _record("performance_gap: TC02 history not trimmed, risking memory pressure")


def test_latency_above_threshold(api: OutdatedAPI) -> None:
    case = _load_case("TC02")
    start = time.perf_counter()
    api.call({"endpoint": "/v1/user", "payload": case["input_payload"]})
    elapsed_ms = (time.perf_counter() - start) * 1000
    assert elapsed_ms >= 25, "Legacy handler unexpectedly fast; check latency simulation"
    _record(f"latency_warning: TC02 handled in {elapsed_ms:.2f} ms")
