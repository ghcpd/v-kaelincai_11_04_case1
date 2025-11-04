#!/usr/bin/env bash
set -euo pipefail
bash ./setup_original.sh
# Clear old logs
: > log_original.txt
: > time_original.txt
start_total=$(python - <<'PY'
import time; print(time.time())
PY
)
pytest -q --disable-warnings || true
python - <<'PY'
import time,json
from original_api import handle_request, LEGACY_ENDPOINT
import pathlib
root = pathlib.Path(__file__).parent.parent
with open(root/'test_data.json','r',encoding='utf-8') as f:
    cases = json.load(f)
latencies=[]
for c in cases:
    t0=time.time()
    status,_=handle_request(LEGACY_ENDPOINT,c['payload'],c['headers'])
    latencies.append((c['id'], (time.time()-t0)*1000,status))
with open('time_original.txt','w',encoding='utf-8') as tf:
    avg=sum(x[1] for x in latencies)/len(latencies)
    tf.write(json.dumps({'average_ms': avg,'per_case': latencies}, indent=2))
PY
