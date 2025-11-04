#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
VENV="${SCRIPT_DIR}/.venv_updated"
if [ ! -d "$VENV" ]; then
  python -m venv "$VENV"
fi
# shellcheck disable=SC1090
source "$VENV/bin/activate"
pip install --upgrade pip >/dev/null
pip install -r requirements_optimized.txt
