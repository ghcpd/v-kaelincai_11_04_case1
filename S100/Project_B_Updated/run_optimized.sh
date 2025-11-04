#!/usr/bin/env bash
set -euo pipefail
PROJECT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
VENV_DIR="$PROJECT_DIR/.venv_optimized"
LOG_FILE="$PROJECT_DIR/log_optimized.txt"
TIME_FILE="$PROJECT_DIR/time_optimized.txt"

bash "$PROJECT_DIR/setup_optimized.sh"

if [ -f "$VENV_DIR/bin/activate" ]; then
  source "$VENV_DIR/bin/activate"
else
  source "$VENV_DIR/Scripts/activate"
fi

pytest "$PROJECT_DIR/test_optimized.py" --disable-warnings --maxfail=1 -q | tee "$LOG_FILE"

if [ -f "$TIME_FILE" ]; then
  echo "Collected latency metrics:" | tee -a "$LOG_FILE"
  cat "$TIME_FILE" | tee -a "$LOG_FILE"
fi
