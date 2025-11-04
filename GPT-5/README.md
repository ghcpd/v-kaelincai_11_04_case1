# Feature & Improvement – API Change Implementation and Validation

## Scenario Overview
Old endpoint: `/v1/user` (Project A – outdated)
New endpoint: `/v2/profile` (Project B – updated)
Backward compatibility: `/v1/user` still routable; legacy format available via `Accept: application/vnd.legacy+json`.

### Core Differences
| Aspect | Outdated (/v1/user) | Updated (/v2/profile) |
|--------|---------------------|------------------------|
| Schema | `{id,name,[email?],latency_ms}` | `{status,data{ id,name,email?,preferences?,nested? },meta{version,latency_ms}}` |
| Errors | Inconsistent strings & leaked internals | Unified JSON error objects |
| Validation | None | Pydantic enforced + sanitization |
| Performance | Artificial delay + redundant expansion | Direct processing; no artificial latency |
| Security | Allows script tags in `name` | Strips script tags |
| Compatibility | N/A | Legacy negotiation header |

### Intended Improvements
- Unified schema & consistent error envelope.
- Reduced latency (remove sleeps & inefficiencies).
- Robust validation for malformed payloads.
- Backward compatible responses when explicitly requested.
- Sanitization of potentially unsafe user input.

## Repository Structure
```
Project_A_Outdated/
  original_api.py
  input_data.json
  requirements_original.txt
  setup_original.sh
  test_original.py
  run_original.sh
  log_original.txt
  time_original.txt
Project_B_Updated/
  updated_api.py
  requirements_optimized.txt
  setup_optimized.sh
  test_optimized.py
  run_optimized.sh
  log_optimized.txt
  time_optimized.txt
test_data.json
compare_results.py
run_all.sh
compare_report.md
README.md
```

## Running Projects Individually
### Project A (Outdated)
Requires Python 3.10+.
```bash
cd Project_A_Outdated
bash setup_original.sh
bash run_original.sh
```
Artifacts: `log_original.txt`, `time_original.txt`.

### Project B (Updated)
```bash
cd Project_B_Updated
bash setup_optimized.sh
bash run_optimized.sh
```
Artifacts: `log_optimized.txt`, `time_optimized.txt`.

## Full Experiment (Both + Comparison)
From repository root:
```bash
bash run_all.sh
```
Generates `compare_report.md` summarizing success rate, latency, schema improvements, and edge-case handling.

## Test Data
`test_data.json` contains five structured test cases (normal, legacy, missing auth, large nested, malformed). Each entry lists expected status and required output keys.

## Reproducibility
- Each project has isolated requirements file and setup script.
- Tests use only local functions (no network calls).
- Comparison script aggregates logs and timing metrics.

## Limitations
- Simulated latency & inefficiencies rather than real network delay.
- Pydantic validation covers structural correctness; deeper semantic rules omitted for brevity.
- Shell scripts assume a POSIX-compatible environment (use Git Bash on Windows).

## Extending
- Add more security validation (e.g., email format, rate limiting).
- Integrate actual HTTP framework (Flask/FastAPI) if network simulation needed.
- Add pagination & filtering for batch profile listings.

## Performance Measurement
Time files record average milliseconds and per-case latencies to quantify improvements.

## Backward Compatibility
Legacy clients can continue using `/v1/user` with minimal changes; tolerance for old schema maintained when Accept header supplied.
