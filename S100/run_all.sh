#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
A_DIR="$ROOT_DIR/Project_A_Outdated"
B_DIR="$ROOT_DIR/Project_B_Updated"
REPORT_PATH="$ROOT_DIR/compare_report.md"

bash "$A_DIR/run_original.sh"
bash "$B_DIR/run_optimized.sh"

python "$ROOT_DIR/generate_compare_report.py"
