#!/usr/bin/env bash
set -euo pipefail
pushd Project_A_Outdated >/dev/null
bash run_original.sh || true
popd >/dev/null
pushd Project_B_Updated >/dev/null
bash run_optimized.sh
popd >/dev/null
python compare_results.py
