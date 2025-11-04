#!/usr/bin/env bash
set -euo pipefail

VENV_DIR=".venv_original"

if [ ! -d "$VENV_DIR" ]; then
  python -m venv "$VENV_DIR"
fi

# shellcheck disable=SC1090
source "$VENV_DIR/bin/activate"

python -m pip install --upgrade pip
python -m pip install -r requirements_original.txt

echo "[setup_original] Virtual environment ready."
