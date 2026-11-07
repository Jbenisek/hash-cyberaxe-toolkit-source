export PATH=$HOME/.local/bin:$PATH
yukon submissions --all --json > /tmp/subs.json 2>/dev/null
grep -o '75d5e1f9-[0-9a-f-]*' /tmp/subs.json | head -2
python3 - <<'PY'
import json
d=json.load(open('/tmp/subs.json'))
L=d if isinstance(d,list) else d.get('submissions',d)
for s in L:
    if str(s.get('id','')).startswith('75d5e1f9') or str(s.get('submissionId','')).startswith('75d5e1f9'):
        print({k:s[k] for k in s if k in ('status','track','challenge','lane','timeLog2','time_log2')})
PY
