# Feature & Improvement – API Change Implementation and Validation

## Overview
This experiment evaluates how AI-assisted code evolves an API from a deprecated `/v1/user` endpoint (Project A) to a refactored `/v2/profile` endpoint (Project B). The focus is on correctness, schema alignment, performance, resilience, and backwards compatibility.

- **Project A – Pre-Change** (`Project_A_Outdated/`): Simulates the legacy implementation with brittle schema validation, blocking latency, and poor error handling.
- **Project B – Post-Change** (`Project_B_Updated/`): Provides a unified schema, graceful error responses, batch support, and improved latency while maintaining compatibility via an upgrade helper.

## API Change Scenario
| Aspect | Legacy `/v1/user` | Updated `/v2/profile` |
| --- | --- | --- |
| Primary Identifier | `userId` | `userId` |
| Status Type | String (e.g., "200") | Integer (e.g., `200`) |
| History | Serialized JSON string or "disabled" | Concrete list limited by `historyDepth` |
| Contact Schema | `emailAddress`, `phoneNumber` | Nested `contact.primary` with structured fields |
| Error Handling | Raises runtime errors on invalid tokens | Returns structured `payload.error` payloads |
| Latency Simulation | 85–130 ms sleep | In-memory operations (<80 ms) |

## Getting Started
All commands assume a POSIX-compatible shell (e.g. Git Bash, WSL, macOS). Windows users can run the scripts through Git Bash or adapt them to PowerShell manually.

### Project A – Pre-Change (Outdated)
1. `cd Project_A_Outdated`
2. Run setup: `bash setup_original.sh`
3. Execute tests and gather metrics: `bash run_original.sh`
   - Produces `log_original.txt` and `time_original.txt`

### Project B – Post-Change (Updated)
1. `cd Project_B_Updated`
2. Run setup: `bash setup_optimized.sh`
3. Execute tests and gather metrics: `bash run_optimized.sh`
   - Produces `log_optimized.txt` and `time_optimized.txt`

### One-Click Experiment
At the repository root:
```
bash run_all.sh
```
This orchestrates both projects, aggregates logs/metrics, and regenerates `compare_report.md`.

## Test Data
`test_data.json` consolidates five scenarios: standard success, legacy compatibility, large history boundary, malformed payload, and missing-user redirect. Each entry specifies the request payload, expected status, and result expectation.

## Environment & Reproducibility
- Each project has its own `requirements_*.txt` file and setup script that provisions an isolated virtual environment under the project directory.
- Tests rely only on the Python standard library and `pytest` (no network calls).
- Execution scripts log outputs for reproducibility and analysis.

## Limitations
- The APIs are simulated and do not expose HTTP servers; they model request/response contracts in-process.
- Performance metrics capture Python execution time on the local machine; values will vary by hardware.
- Shell scripts target POSIX shells; adapt to PowerShell if needed.

## Deliverables
- Project A deliverables under `Project_A_Outdated/`
- Project B deliverables under `Project_B_Updated/`
- Shared assets: `test_data.json`, `compare_report.md`, `run_all.sh`, and this `README.md`
