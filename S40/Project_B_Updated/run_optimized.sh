#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
LOG_FILE="$SCRIPT_DIR/log_optimized.txt"
TIME_FILE="$SCRIPT_DIR/time_optimized.txt"
VENV="$SCRIPT_DIR/.venv_updated"

if [ ! -d "$VENV" ]; then
  bash "$SCRIPT_DIR/setup_optimized.sh"
else
  # shellcheck disable=SC1090
  source "$VENV/bin/activate"
  pip install --upgrade pip >/dev/null
  pip install -r requirements_optimized.txt >/dev/null
fi

python - <<'PY'
import json
import pathlib
import subprocess
import sys
import time

root = pathlib.Path(__file__).resolve().parent
log_path = root / "log_optimized.txt"
time_path = root / "time_optimized.txt"

start = time.perf_counter()
result = subprocess.run([sys.executable, "-m", "pytest", "-q"], capture_output=True, text=True)
elapsed = time.perf_counter() - start

combined_output = result.stdout
if result.stderr:
    combined_output += "\n" + result.stderr
log_path.write_text(combined_output)

time_payload = {
    "duration_seconds": round(elapsed, 4),
    "tests_passed": result.returncode == 0,
    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
}
time_path.write_text(json.dumps(time_payload, indent=2))

sys.stdout.write(result.stdout)
if result.returncode != 0:
    sys.stderr.write(result.stderr)
    sys.exit(result.returncode)
PY
