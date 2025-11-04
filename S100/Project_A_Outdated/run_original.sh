#!/usr/bin/env bash
set -euo pipefail
PROJECT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
VENV_DIR="$PROJECT_DIR/.venv_original"
LOG_FILE="$PROJECT_DIR/log_original.txt"
TIME_FILE="$PROJECT_DIR/time_original.txt"

bash "$PROJECT_DIR/setup_original.sh"

if [ -f "$VENV_DIR/bin/activate" ]; then
  source "$VENV_DIR/bin/activate"
else
  source "$VENV_DIR/Scripts/activate"
fi

pytest "$PROJECT_DIR/test_original.py" --disable-warnings --maxfail=1 -q | tee "$LOG_FILE"

# Ensure latency metrics captured during pytest run are visible in console too.
if [ -f "$TIME_FILE" ]; then
  echo "Collected latency metrics:" | tee -a "$LOG_FILE"
  cat "$TIME_FILE" | tee -a "$LOG_FILE"
fi
