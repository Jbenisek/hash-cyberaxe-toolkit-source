S=/root/hashsmash/yukon/pos_f1020143442/pareto
ls $S/.yukon/work/tracks/blake3-pareto/ 2>/dev/null
cat $S/.yukon/work/tracks/blake3-pareto/pareto-outcome.json 2>/dev/null | head -c 1500; echo
python3 - <<'PY'
import json,os
p="/root/hashsmash/yukon/pos_f1020143442/pareto/.yukon/work/tracks/blake3-pareto/experiment-report.json"
if os.path.exists(p):
    d=json.load(open(p)); e=d.get('execution',{})
    print(e.get('status'), [(x['id'], len(x.get('checked_trials',[])), sum(t.get('success',0) for t in x.get('checked_trials',[]))) for x in e.get('experiments',[])])
PY
cat $S/dependencies.json | python3 -c "import json,sys;print([d['submissionId'][:8] for d in json.load(sys.stdin)])"
