import json
import pytest

from original_api import (
    LegacyAuthenticationError,
    LegacySchemaMismatch,
    LegacyUserAPI,
    load_sample_datastore,
)


@pytest.fixture()
def api():
    return LegacyUserAPI(load_sample_datastore())


def test_schema_validation_detects_mismatch(api):
    request = {
        "userId": "usr-1001",
        "token": "legacy-static-token",
        "includeHistory": "true",
        "historyDepth": 2,
        "apiVersion": "2020-09",
    }
    response = api.fetch_user(request)
    assert isinstance(response["payload"]["user"]["history"], str)
    with pytest.raises(LegacySchemaMismatch):
        api.validate_schema(response)


def test_invalid_token_rejected(api):
    with pytest.raises(LegacyAuthenticationError):
        api.fetch_user({
            "userId": "usr-1001",
            "token": "invalid",
            "apiVersion": "2020-09",
        })


def test_missing_user_returns_string_status(api):
    response = api.fetch_user({
        "userId": "usr-404",
        "token": "legacy-static-token",
        "apiVersion": "2020-09",
    })
    assert response["status"] == "404"
    assert "errorMessage" in response["payload"]
    assert json.loads(json.dumps(response))  # ensure serializable despite mismatch
