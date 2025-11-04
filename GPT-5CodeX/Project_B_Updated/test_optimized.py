"""Pytest suite validating the updated API implementation."""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from updated_api import UpdatedAPI

ROOT = Path(__file__).resolve().parent
LOG_PATH = ROOT / "log_optimized.txt"
TEST_DATA_PATH = ROOT.parent / "test_data.json"

LOG_PATH.write_text("UPDATED API TEST RUN\n", encoding="utf-8")


def _append(event: str) -> None:
    LOG_PATH.write_text(LOG_PATH.read_text(encoding="utf-8") + event + "\n", encoding="utf-8")


def _load_case(case_id: str) -> dict:
    return next(
        case
        for case in json.loads(TEST_DATA_PATH.read_text(encoding="utf-8"))
        if case["id"] == case_id
    )


@pytest.fixture()
def api() -> UpdatedAPI:
    return UpdatedAPI()


def test_profile_schema_and_preferences(api: UpdatedAPI) -> None:
    case = _load_case("TC01")
    response = api.call({"endpoint": case["endpoint"], "payload": case["input_payload"]})
    assert response.status_code == 200
    body = response.body
    assert "profile" in body
    assert body["profile"]["user_id"] == case["input_payload"]["user_id"]
    assert "preferences" in body["profile"]
    assert response.metadata["latency_ms"] < 25
    _append("ok: TC01 profile schema matches and latency within target")


def test_large_payload_boundary_handled(api: UpdatedAPI) -> None:
    case = _load_case("TC02")
    response = api.call({"endpoint": case["endpoint"], "payload": case["input_payload"]})
    assert response.status_code == 200
    assert "metadata" in response.body
    assert len(response.body["metadata"]["history"]) == 2
    _append("ok: TC02 boundary payload accepted and trimmed")


def test_missing_token_rejected(api: UpdatedAPI) -> None:
    case = _load_case("TC03")
    response = api.call({"endpoint": case["endpoint"], "payload": case["input_payload"]})
    assert response.status_code == 400
    assert response.body["error"]["code"] == "MISSING_TOKEN"
    _append("ok: TC03 missing token rejected with 400")


def test_compatibility_redirect(api: UpdatedAPI) -> None:
    case = _load_case("TC04")
    response = api.call({"endpoint": case["endpoint"], "payload": case["input_payload"]})
    assert response.status_code == 301
    assert response.body["redirect"] == "/v2/profile"
    assert response.metadata.get("deprecated") is True
    _append("ok: TC04 redirected from legacy endpoint")


def test_invalid_token_rejected(api: UpdatedAPI) -> None:
    case = _load_case("TC05")
    response = api.call({"endpoint": case["endpoint"], "payload": case["input_payload"]})
    assert response.status_code == 401
    assert response.body["error"]["code"] == "INVALID_TOKEN"
    _append("ok: TC05 invalid token blocked")


def test_latency_consistently_below_threshold(api: UpdatedAPI) -> None:
    case = _load_case("TC01")
    start = time.perf_counter()
    api.call({"endpoint": case["endpoint"], "payload": case["input_payload"]})
    elapsed_ms = (time.perf_counter() - start) * 1000
    assert elapsed_ms < 20
    _append(f"ok: latency measured at {elapsed_ms:.2f} ms for TC01 re-run")
