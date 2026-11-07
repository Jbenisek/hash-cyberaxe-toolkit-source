
# Publication path adapter: resolve data paths from the extracted source tree.
def _hca_public_path_text(value):
    if "__HCA_WORKSPACE__/" not in value:
        return value
    import os as _hca_os
    from pathlib import Path as _hca_Path
    root = _hca_os.environ.get("HASHCYBERAXE_WORKSPACE")
    if root is None:
        here = _hca_Path(__file__).resolve().parent
        root = next((str(p) for p in (here, *here.parents) if (p / "research").is_dir()), None)
    if root is None:
        raise FileNotFoundError("Extract the research source tree, or set HASHCYBERAXE_WORKSPACE to its archive directory.")
    return value.replace("__HCA_WORKSPACE__/", str(_hca_Path(root).resolve()).replace("\\", "/") + "/")

import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mk3_common as C
import mk3_a, mk3_b, mk3_c
W=_hca_public_path_text('__HCA_WORKSPACE__/')
ALLOWED_LABELS=set("N D X C S I B P K E Z 0".split())
STATUS={"BEDROCK","COMPUTED","SAMPLED","LOCAL_ONLY","CLAIMED-UNTESTED","KILLED","OPEN"}
REQ=["hash","row_i","row_j","object","question","labels","status","number","source","own_test","evidence","date","lever","gain_bits","notes","held_fixed","reopen_if"]
units={}
for l in open(W+'research/dig/UNITS.jsonl',encoding='utf-8'):
    d=json.loads(l)
    if d['id'].startswith('blake3-r3-U') and 73<=int(d['id'].split('U')[1])<=81: units[d['id']]=d['cells']
want={(u,c) for u,cs in units.items() for c in cs}
have={(u,c) for u,c,_ in C.recs}
print('cells wanted',len(want),'written',len(have),'missing',sorted(want-have),'extra',sorted(have-want))
errs=0
for u,c,d in C.recs:
    for k in REQ:
        if k not in d: print('MISSING',c,k); errs+=1
    if d['hash']!='blake3-r3' or d['source']!='our workflow: dig-scan-b3r3' or d['date']!='2026-10-12' or d['own_test'] is not True: print('BASE',c); errs+=1
    if not set(d['labels'])<=ALLOWED_LABELS: print('LABEL',c); errs+=1
    if d['status'] not in STATUS: print('STATUS',c); errs+=1
    if d['status']=='KILLED': print('KILLED present',c); errs+=1
    if d['lever'] and (d['gain_bits'] is None or 'gain_basis' not in d): print('LEVER fields',c); errs+=1
    if not d['held_fixed'] or not d['reopen_if']: print('EMPTY opt',c); errs+=1
    for p in [x.strip() for x in d['evidence'].split(',')]:
        if not os.path.exists(W+p): print('EVIDENCE missing',c,p); errs+=1
    for k,v in d.items():
        if isinstance(v,str) and any(ord(ch)>127 for ch in v): print('NONASCII',c,k); errs+=1
    od=os.path.join(C.OUT,u); os.makedirs(od,exist_ok=True)
    fn=c.replace('|','_')+'.json'
    json.dump(d,open(os.path.join(od,fn),'w',encoding='utf-8'),indent=1)
print('records',len(C.recs),'errors',errs)
