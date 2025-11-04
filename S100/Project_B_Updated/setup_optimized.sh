#!/usr/bin/env bash
set -euo pipefail
PROJECT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
VENV_DIR="$PROJECT_DIR/.venv_optimized"

if [ ! -d "$VENV_DIR" ]; then
  python -m venv "$VENV_DIR"
fi

if [ -f "$VENV_DIR/bin/activate" ]; then
  source "$VENV_DIR/bin/activate"
elif [ -f "$VENV_DIR/Scripts/activate" ]; then
  source "$VENV_DIR/Scripts/activate"
else
  echo "Could not locate virtual environment activation script." >&2
  exit 1
fi

pip install --upgrade pip
pip install -r "$PROJECT_DIR/requirements_optimized.txt"
