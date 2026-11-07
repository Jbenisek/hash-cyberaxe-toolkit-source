S=/root/hashsmash/yukon/pos_f1020143442/pareto/.yukon/work/tracks/blake3-pareto
stat -c '%n %s' $S/judge-evidence.json $S/experiment-report.json
python3 -c "import json;d=json.load(open('$S/experiment-report.json'));print([ (x['id'], x.get('status'), sum(1 for t in x['checked_trials'] if t.get('verified', t.get('success')) is False and t.get('message_a_hex'))) for x in d['execution']['experiments']])" 2>&1 | head -3
