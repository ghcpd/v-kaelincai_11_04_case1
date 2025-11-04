#!/bin/bash

echo "========================================="
echo "API Change Evaluation - Full Test Suite"
echo "========================================="
echo ""

# Project A - Outdated
echo "Step 1: Setting up Project A (Outdated)"
cd Project_A_Outdated
bash setup_original.sh
echo ""

echo "Step 2: Running Project A Tests"
bash run_original.sh
cd ..
echo ""

# Project B - Updated
echo "Step 3: Setting up Project B (Updated)"
cd Project_B_Updated
bash setup_optimized.sh
echo ""

echo "Step 4: Running Project B Tests"
bash run_optimized.sh
cd ..
echo ""

# Generate comparison report
echo "Step 5: Generating Comparison Report"
python generate_report.py
echo ""

echo "========================================="
echo "Execution Complete!"
echo "See compare_report.md for full analysis"
echo "========================================="
