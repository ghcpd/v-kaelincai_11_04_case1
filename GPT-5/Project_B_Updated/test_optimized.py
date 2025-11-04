import json
import os
import time
import pytest
from updated_api import handle_request, PROFILE_ENDPOINT, LEGACY_ENDPOINT

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
TEST_DATA_PATH = os.path.join(ROOT, 'test_data.json')

with open(TEST_DATA_PATH, 'r', encoding='utf-8') as f:
    CASES = json.load(f)

@pytest.mark.parametrize('case', CASES)
def test_updated_cases(case):
    start = time.time()
    status, body = handle_request(case['path'], case['payload'], case['headers'])
    duration_ms = int((time.time() - start) * 1000)
    assert status == case['expected_status'], f"Status mismatch case {case['id']}"
    # Validate schema presence
    for key in case['expected_output_contains']:
        if status >= 400:
            # Error schema
            assert 'error' in body or key == 'error', 'Error structure missing'
        else:
            if case['path'] == LEGACY_ENDPOINT and 'application/vnd.legacy+json' in case['headers'].get('Accept', ''):
                # Legacy negotiated shape
                assert key in body or key == 'status', 'Legacy field missing'
            else:
                if key == 'status':
                    assert body.get('status') == 'ok'
                else:
                    assert key in body or key in body.get('data', {}) or key in body.get('meta', {}), f"Field {key} not found"
    # Log
    log_line = json.dumps({'case_id': case['id'], 'status': status, 'duration_ms': duration_ms})
    with open(os.path.join(os.path.dirname(__file__), 'log_optimized.txt'), 'a', encoding='utf-8') as lf:
        lf.write(log_line + '\n')
