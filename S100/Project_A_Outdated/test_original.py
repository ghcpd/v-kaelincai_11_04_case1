import json
import time
from pathlib import Path
from typing import Dict, List

import pytest
from pydantic import BaseModel, ValidationError

from original_api import LegacyAPIError, LegacyRequest, LegacyUserAPI, collect_latency_profile, load_requests


ROOT_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = Path(__file__).resolve().parent
LOG_PATH = PROJECT_DIR / "log_original.txt"
TIME_PATH = PROJECT_DIR / "time_original.txt"
SHARED_TEST_DATA = ROOT_DIR / "test_data.json"


class ProfileSchema(BaseModel):
    """Represents the unified `/v2/profile` contract the new API must satisfy."""

    user: Dict[str, object]
    contact: Dict[str, object]
    membership: Dict[str, object]
    activity: Dict[str, object]


@pytest.fixture(scope="session", autouse=True)
def initialise_log_file():
    LOG_PATH.write_text("Legacy API diagnostic log\n")
    TIME_PATH.write_text("Legacy API latency metrics\n")
    yield
    # ensure newline at end
    with LOG_PATH.open("a", encoding="utf-8") as stream:
        stream.write("--- end session ---\n")


@pytest.fixture
def legacy_api():
    return LegacyUserAPI(artificial_latency=0.045)


def load_shared_cases() -> List[Dict[str, object]]:
    data = json.loads(SHARED_TEST_DATA.read_text())
    return data


def test_schema_mismatch_detected(legacy_api):
    request = LegacyRequest(user_id="1001", token="token_v1")
    response = legacy_api.fetch_user(request)
    missing_keys = {"user", "contact", "membership", "activity"} - set(response.keys())
    assert missing_keys, "Legacy API unexpectedly satisfied the new schema"
    with LOG_PATH.open("a", encoding="utf-8") as stream:
        stream.write(f"schema_mismatch_missing={sorted(missing_keys)}\n")


def test_invalid_token_produces_generic_error(legacy_api):
    bad_request = LegacyRequest(user_id="1001", token="token_v2")
    with pytest.raises(LegacyAPIError):
        legacy_api.fetch_user(bad_request)
    with LOG_PATH.open("a", encoding="utf-8") as stream:
        stream.write("invalid_token_detected=1\n")


def test_nested_payload_is_flattened(legacy_api):
    nested_case = {
      "input": {
          "user_id": "1001",
          "token": "token_v1",
          "payload": {
              "profile": {"locale": "en-US"},
              "contact": {"emails": ["alicia.legacy@example.com"]}
          }
      }
    }
    request = LegacyRequest.from_dict(nested_case["input"])
    response = legacy_api.fetch_user(request)
    assert "metadata" in response
    assert "profile" not in response, "Legacy API should not automatically accept nested profile data"
    with LOG_PATH.open("a", encoding="utf-8") as stream:
        stream.write("nested_payload_flattened=1\n")


def test_latency_profile_is_degraded(legacy_api):
    input_requests = load_requests(Path(__file__).with_name("input_data.json"))
    metrics = collect_latency_profile(legacy_api, input_requests)
    assert metrics["max"] >= 0.04
    assert metrics["avg"] >= 0.015
    with TIME_PATH.open("a", encoding="utf-8") as stream:
        stream.write(
            f"avg={metrics['avg']:.4f},min={metrics['min']:.4f},max={metrics['max']:.4f}\n"
        )


def test_shared_edge_cases_trigger_failures(legacy_api):
    cases = load_shared_cases()
    problematic = 0
    for case in cases:
        inputs = case["input"]
        request = LegacyRequest(user_id=str(inputs.get("user_id")), token=str(inputs.get("token", "")))
        expected_status = case["expected_status"]
        if expected_status == 200 and case["expected_outcome"] == "pass" and request.token == "token_v1":
            response = legacy_api.fetch_user(request)
            assert isinstance(response["id"], str)
        else:
            with pytest.raises(LegacyAPIError):
                legacy_api.fetch_user(request)
            problematic += 1
    assert problematic >= 2  # ensure we exercised failure surfaces
    with LOG_PATH.open("a", encoding="utf-8") as stream:
        stream.write(f"shared_problematic_cases={problematic}\n")
