# Comparison Report: Legacy vs Updated API

## High-Level Summary
- Legacy /v1/user implementation exposes schema mismatches detected by validator.
- Updated /v2/profile implementation passes unified schema checks and standardizes error payloads.
- Batch processing and legacy payload upgrades are covered by targeted tests.

## Test Outcomes
| Metric | Project A (Legacy) | Project B (Updated) |
| --- | --- | --- |
| Tests Passed | 3 / 3 | 5 / 5 |
| Execution Time (s) | 0.739 | 0.5307 |
| Log File | Project_A_Outdated/log_original.txt | Project_B_Updated/log_optimized.txt |
| Schema Compliance | Fails validator (expected) | Passes unified validator |
| Error Handling | Raises runtime errors | Structured error payload |
| History Format | Serialized string | Strongly typed list |


## Performance
- Legacy duration: 0.739 seconds
- Updated duration: 0.5307 seconds
- Latency Improvement: 28.19%

## Schema & Response Diffs
- **Status field**: Legacy returns strings; updated API returns integers.
- **History**: Legacy serializes JSON strings or disables history; updated API returns trimmed lists governed by historyDepth.
- **Contact info**: Legacy uses flat keys (emailAddress); updated API nests them under contact.primary.
- **Error flow**: Legacy raises exceptions for invalid tokens; updated API returns 401 payload without throwing.

## Backward Compatibility
- `from_legacy_payload` upgrades /v1/user responses to /v2/profile schema.
- Batch processor accepts mixed requests and gracefully handles missing users.
- Tests cover malformed input, boundary depth, and mixed-version payloads.

## Observations
- Updated API removes artificial latency, reducing response time while preserving deterministic behavior.
- Unified schema ensures monitoring, logging, and consumers share consistent field names.
- Structured errors and validator checks improve resilience against malformed integrations.
