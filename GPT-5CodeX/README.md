# Evaluation of GPT-5-Codex, GPT-5, Claude Sonnet 4.5, S100, and S40 on Feature & Improvement – API Change Implementation and Validation

This workspace demonstrates an end-to-end API change scenario evaluated across an outdated (pre-change) implementation and a refactored (post-change) implementation.

## Scenario Overview
- **Legacy endpoint:** `/v1/user`
- **Updated endpoint:** `/v2/profile`
- **Key differences:**
  - Deprecated endpoint returned loosely structured payloads (`status` string with nested data, inconsistent error fields).
  - Updated endpoint returns a stable envelope with `status_code`, `metadata`, and a strictly validated `profile` structure.
  - Improved handling for malformed tokens, pagination, and nested preference data.
- **Intended improvements:** Unified schema, stricter validation, faster in-memory routing, and consistent latency reporting.

## Repository Layout
- `Project_A_Outdated/`: Pre-change implementation highlighting schema drift and brittle error handling.
- `Project_B_Updated/`: Post-change implementation with schema parity, validation, and performance optimisations.
- `test_data.json`: Shared structured tests spanning normal, boundary, malformed, and compatibility scenarios.
- `run_all.sh`: Orchestrates setup, execution, and reporting across both projects.
- `compare_report.md`: Summarises behavioural and performance deltas between the two versions.

## How to Run
1. **Execute the full experiment**
   ```bash
   ./run_all.sh
   ```
   This script sequentially runs both projects, aggregates logs and timings, and regenerates `compare_report.md`.

2. **Run projects individually**
   ```bash
   # Project A (legacy)
   ./Project_A_Outdated/run_original.sh

   # Project B (updated)
   ./Project_B_Updated/run_optimized.sh
   ```

## Environment & Reproducibility
- Each project includes its own `requirements_*.txt` and `setup_*.sh` scripts that provision a local virtual environment.
- No live network calls are performed; the APIs are simulated in pure Python for deterministic results.
- Logs (`log_*.txt`) and latency samples (`time_*.txt`) are persisted for auditability.

## Limitations
- Shell scripts target a POSIX-compatible environment; on Windows, run them through WSL or adapt commands to PowerShell manually.
- Performance metrics are sample measurements from synthetic runs and should be recalculated after any changes.
