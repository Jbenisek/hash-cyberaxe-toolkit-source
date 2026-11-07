#!/usr/bin/env bash
D=/root/hashsmash/yukon/pos_f1020214842/pareto/.yukon/work/tracks/blake3-pareto
ls -la $D
cat $D/pareto-outcome.json 2>/dev/null | head -c 1500; echo
python3 - $D/experiment-report.json <<'PY'
import json, sys
try:
    d = json.load(open(sys.argv[1]))
except Exception as e:
    print("no report", e); sys.exit()
ex = d.get('execution', {})
print('status', ex.get('status'))
for e in ex.get('experiments', []):
    t = e.get('checked_trials', [])
    print(e.get('id'), len(t), 'success', sum(1 for x in t if x.get('success')), {k: v for k, v in e.items() if k not in ('checked_trials',)} if False else '')
PY
