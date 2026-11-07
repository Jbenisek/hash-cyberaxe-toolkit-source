
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

import json,glob,os,sys,re
sys.path.insert(0,_hca_public_path_text('__HCA_WORKSPACE__/hash-smash'))
from verifier.io import canonical_json_bytes as cj
D=_hca_public_path_text('__HCA_WORKSPACE__/research/dossiers')
rows=[]
for f in sorted(glob.glob(D+'/*/runs/*/judge-evidence.json')):
    raw=open(f,'rb').read(); ev=json.loads(raw); c=len(cj(ev)); d=os.path.normpath(f).replace(chr(92),'/').split('/')[-4]

    prof=re.findall(rb'(sha256-r3\d|sha3-r\d|blake3-r\d)',raw)
    prof=max(set(prof),key=prof.count).decode() if prof else '?'
    rows.append((d,prof,len(raw),c,524288-c))
for r in rows:
    print(*r, 'equal' if r[2]==r[3] else 'DIFF')
print('canon recount equal',sum(r[2]==r[3] for r in rows),'of',len(rows))
