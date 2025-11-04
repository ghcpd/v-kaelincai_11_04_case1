import json
import os
import time
import pytest
from original_api import handle_request, LEGACY_ENDPOINT

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
TEST_DATA_PATH = os.path.join(ROOT, 'test_data.json')

with open(TEST_DATA_PATH, 'r', encoding='utf-8') as f:
    CASES = json.load(f)

# Map v2 paths to legacy to expose mismatch behavior
LEGACY_CASES = []
for c in CASES:
    mapped = dict(c)
    if mapped['path'] != LEGACY_ENDPOINT:
        mapped['path'] = LEGACY_ENDPOINT  # force legacy endpoint usage
    LEGACY_CASES.append(mapped)

@pytest.mark.parametrize('case', LEGACY_CASES)
def test_legacy_cases(case):
    start = time.time()
    status, body = handle_request(case['path'], case['payload'], case['headers'])
    duration_ms = int((time.time() - start) * 1000)
    # Original implementation expected to be inconsistent; we only assert status matches basic expectations except for validation failures not handled
    expected_status = case['expected_status']
    # For missing name (case id 5), original wrongly returns 200; mark as known failure
    if case['id'] == 5:
        assert status != expected_status, 'Outdated API should fail this validation scenario'
    else:
        assert status == expected_status, f"Status mismatch for case {case['id']}"
    # Basic logging artifact
    log_line = json.dumps({
        'case_id': case['id'],
        'expected_status': expected_status,
        'actual_status': status,
        'duration_ms': duration_ms,
        'legacy_shape': isinstance(body, dict) and 'meta' not in body
    })
    with open(os.path.join(os.path.dirname(__file__), 'log_original.txt'), 'a', encoding='utf-8') as lf:
        lf.write(log_line + '\n')

