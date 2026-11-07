cd ~/hashsmash/yukon/pos_b3r3pv
python3 - <<'PY'
import json
d=json.load(open('cost-models/collision-frontier-v5.json'))
def walk(o,p=''):
    if isinstance(o,dict):
        for k,v in o.items():
            if isinstance(v,(dict,list)): walk(v,p+'/'+k)
            else: print(p+'/'+k,'=',str(v)[:300])
    elif isinstance(o,list):
        for i,v in enumerate(o):
            if isinstance(v,(dict,list)): walk(v,p+'[%d]'%i)
            else: print(p+'[%d]'%i,'=',str(v)[:300])
walk(d)
PY
