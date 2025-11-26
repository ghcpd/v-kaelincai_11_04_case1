#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

./setup_optimized.sh >/dev/null

# shellcheck disable=SC1090
source .venv_optimized/bin/activate

START_TIME=$(python - <<'PY'
import time
print(time.perf_counter())
PY
)

pytest --maxfail=1 --disable-warnings -q | tee pytest_optimized_output.txt

END_TIME=$(python - <<'PY'
import time
print(time.perf_counter())
PY
)

python - <<PY
start = float("$START_TIME")
end = float("$END_TIME")
duration_ms = (end - start) * 1000
with open("time_optimized.txt", "w", encoding="utf-8") as handle:
    handle.write(f"total_duration_ms={duration_ms:.2f}\n")
    handle.write("notes=Updated handler run including pytest execution.\n")
PY

echo "[run_optimized] Updated tests complete."
