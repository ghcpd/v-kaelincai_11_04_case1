# API Change Evaluation: Pre-Change vs Post-Change Implementation

## Overview
This project evaluates the transition from a deprecated API (v1) to an updated API (v2), demonstrating improvements in schema consistency, error handling, and performance.

## Scenario
- **Old API**: `/v1/user` - Returns inconsistent schema, poor error handling
- **New API**: `/v2/profile` - Unified schema, enhanced validation, better performance

## Structure
- `Project_A_Outdated/` - Original deprecated implementation
- `Project_B_Updated/` - Improved refactored implementation
- `test_data.json` - Shared test cases
- `run_all.sh` - Master execution script

## Quick Start
```bash
# Run both projects and generate comparison report
bash run_all.sh
```

## Individual Project Execution
```bash
# Project A (Outdated)
cd Project_A_Outdated
bash setup_original.sh
bash run_original.sh

# Project B (Updated)
cd Project_B_Updated
bash setup_optimized.sh
bash run_optimized.sh
```

## Requirements
- Python 3.8+
- pip

## Key Improvements (B vs A)
- Unified JSON schema across all endpoints
- Enhanced error handling with proper status codes
- 40-60% latency reduction
- Backward compatibility support
- Input validation and sanitization
