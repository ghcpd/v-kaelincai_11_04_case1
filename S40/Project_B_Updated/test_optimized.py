import json
import pytest

from updated_api import (
    UnifiedProfileAPI,
    UnifiedSchemaError,
    load_enhanced_datastore,
)


@pytest.fixture()
def api():
    return UnifiedProfileAPI(load_enhanced_datastore())


def test_profile_uses_unified_schema(api):
    request = {
        "userId": "usr-1001",
        "token": "rotating-service-token",
        "includeHistory": True,
        "historyDepth": 2,
        "requestId": "req-test-1",
        "correlationId": "corr-abc",
    }
    response = api.get_profile(request)
    UnifiedProfileAPI.validate_against_reference_schema(response)
    assert response["status"] == 200
    assert response["payload"]["profile"]["activity"]["history"]
    assert response["meta"]["elapsedMs"] < 80  # latency improved vs legacy sleep


def test_batch_processing_handles_multiple_users(api):
    requests = [
        {
            "userId": "usr-1001",
            "token": "rotating-service-token",
            "includeHistory": False,
        },
        {
            "userId": "usr-1002",
            "token": "rotating-service-token",
            "includeHistory": True,
            "historyDepth": 1,
        },
    ]
    responses = api.process_batch(requests)
    assert len(responses) == 2
    assert responses[0]["payload"]["profile"]["activity"]["history"] == []
    assert len(responses[1]["payload"]["profile"]["activity"]["history"]) == 1


def test_from_legacy_payload_migration(api):
    legacy_payload = {
        "status": "200",
        "payload": {
            "user": {
                "first_name": "Harper",
                "last_name": "Lee",
                "contact": {"emailAddress": "harper@example.com", "phoneNumber": None},
                "history": json.dumps([
                    {"ts": "2024-02-01T12:00:00Z", "action": "login"}
                ]),
                "last_seen": "2025-10-10T08:50:10Z",
            }
        },
        "meta": {"durationMs": 115.5},
    }
    upgraded = api.from_legacy_payload(legacy_payload)
    UnifiedProfileAPI.validate_against_reference_schema(upgraded)
    assert upgraded["payload"]["profile"]["name"]["full"] == "Harper Lee"


def test_invalid_token_rejected_with_schema_error(api):
    with pytest.raises(UnifiedSchemaError):
        api.get_profile({
            "userId": "usr-1001",
            "token": "legacy-static-token",
        })


def test_missing_user_returns_structured_error(api):
    request = {
        "userId": "usr-missing",
        "token": "rotating-service-token",
        "requestId": "req-missing",
    }
    response = api.get_profile(request)
    assert response["status"] == 404
    assert response["payload"]["error"]["code"] == 404
