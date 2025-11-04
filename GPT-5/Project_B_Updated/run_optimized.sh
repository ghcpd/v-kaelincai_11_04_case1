#!/usr/bin/env bash
set -euo pipefail
bash ./setup_optimized.sh
: > log_optimized.txt
: > time_optimized.txt
pytest -q --disable-warnings
python - <<'PY'
import time,json
from updated_api import handle_request, PROFILE_ENDPOINT
import pathlib
root = pathlib.Path(__file__).parent.parent
with open(root/'test_data.json','r',encoding='utf-8') as f:
    cases = json.load(f)
latencies=[]
for c in cases:
    t0=time.time()
    status,_=handle_request(c['path'],c['payload'],c['headers'])
    latencies.append((c['id'], (time.time()-t0)*1000,status))
with open('time_optimized.txt','w',encoding='utf-8') as tf:
    avg=sum(x[1] for x in latencies)/len(latencies)
    tf.write(json.dumps({'average_ms': avg,'per_case': latencies}, indent=2))
PY
