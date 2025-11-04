import json
from pathlib import Path
from typing import Dict, List

import pytest

from updated_api import (
    NotFoundError,
    ProfilePayload,
    ProfileRequest,
    UnauthorizedError,
    UpdatedProfileAPI,
    collect_latency_profile,
    load_shared_test_data,
)


ROOT_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = Path(__file__).resolve().parent
LOG_PATH = PROJECT_DIR / "log_optimized.txt"
TIME_PATH = PROJECT_DIR / "time_optimized.txt"
INPUT_PATH = PROJECT_DIR / ".." / "test_data.json"


@pytest.fixture(scope="session", autouse=True)
def initialise_log_file():
    LOG_PATH.write_text("Updated API verification log\n")
    TIME_PATH.write_text("Updated API latency metrics\n")
    yield
    with LOG_PATH.open("a", encoding="utf-8") as stream:
        stream.write("--- end session ---\n")


@pytest.fixture
def profile_api():
    return UpdatedProfileAPI(base_latency=0.005, cache_ttl_seconds=10.0)


def create_case_table(metrics: Dict[str, float]) -> str:
    header = "Latency Metrics (/v2)"
    lines = [header, "Metric | Seconds", "------------------"]
    for key in ("avg", "min", "max"):
        lines.append(f"{key:<5} | {metrics[key]:.4f}")
    table = "\n".join(lines)
    print(table)
    return table


def test_schema_alignment(profile_api):
    payload = {"user_id": "1001", "token": "token_v2", "include_history": True}
    profile = profile_api.fetch_profile(payload)
    validated = ProfilePayload(**profile)
    assert validated.user["id"] == 1001
    assert "history" in validated.activity
    with LOG_PATH.open("a", encoding="utf-8") as stream:
        stream.write("schema_alignment=pass\n")


def test_backward_compatibility_accepts_legacy_contract(profile_api):
    payload = {"user_id": "1002", "token": "token_v1"}
    profile = profile_api.fetch_profile(payload)
    assert profile["user"]["tier"] == "gold"
    assert profile["contact"]["email"].endswith("@example.com")
    with LOG_PATH.open("a", encoding="utf-8") as stream:
        stream.write("legacy_contract_supported=1\n")


def test_invalid_token_rejected(profile_api):
    with pytest.raises(UnauthorizedError):
        profile_api.fetch_profile({"user_id": "1001", "token": "tampered"})
    with LOG_PATH.open("a", encoding="utf-8") as stream:
        stream.write("unauthorized_error=1\n")


def test_unknown_user_returns_404(profile_api):
    with pytest.raises(NotFoundError) as exc_info:
        profile_api.fetch_profile({"user_id": "9999", "token": "token_v2"})
    assert exc_info.value.status.value == 404
    with LOG_PATH.open("a", encoding="utf-8") as stream:
        stream.write("not_found=1\n")


def test_latency_profile_improves(profile_api):
    data = load_shared_test_data(INPUT_PATH)
    metrics = collect_latency_profile(profile_api, [case["input"] for case in data])
    assert metrics["avg"] <= 0.01
    pretty = create_case_table(metrics)
    with TIME_PATH.open("a", encoding="utf-8") as stream:
        stream.write(pretty + "\n")
        stream.write(
            f"avg={metrics['avg']:.4f},min={metrics['min']:.4f},max={metrics['max']:.4f}\n"
        )


def test_shared_cases_all_pass(profile_api):
    cases = load_shared_test_data(INPUT_PATH)
    passed = 0
    for case in cases:
        payload = case["input"]
        expected_status = case["expected_status"]
        expected_outcome = case["expected_outcome"]
        if expected_status == 401:
            with pytest.raises(UnauthorizedError):
                profile_api.fetch_profile(payload)
        elif expected_status == 404:
            with pytest.raises(NotFoundError):
                profile_api.fetch_profile(payload)
        else:
            response = profile_api.fetch_profile(payload)
            ProfilePayload(**response)
            passed += 1
    assert passed >= 3
    with LOG_PATH.open("a", encoding="utf-8") as stream:
        stream.write(f"shared_cases_success={passed}\n")
