#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

./setup_original.sh >/dev/null

# shellcheck disable=SC1090
source .venv_original/bin/activate

START_TIME=$(python - <<'PY'
import time
print(time.perf_counter())
PY
)

pytest --maxfail=1 --disable-warnings -q | tee pytest_original_output.txt

END_TIME=$(python - <<'PY'
import time
print(time.perf_counter())
PY
)

python - <<PY
start = float("$START_TIME")
end = float("$END_TIME")
duration_ms = (end - start) * 1000
with open("time_original.txt", "w", encoding="utf-8") as handle:
    handle.write(f"total_duration_ms={duration_ms:.2f}\n")
    handle.write("notes=Includes environment activation and pytest discovery.\n")
PY

echo "[run_original] Legacy tests complete."
