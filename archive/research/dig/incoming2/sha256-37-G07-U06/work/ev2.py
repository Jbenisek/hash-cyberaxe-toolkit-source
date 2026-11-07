
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

import json,glob,os,sys
sys.path.insert(0,_hca_public_path_text('__HCA_WORKSPACE__/hash-smash'))
from verifier.io import canonical_json_bytes as cj
D=_hca_public_path_text('__HCA_WORKSPACE__/research/dossiers')
for d in ['b43280d0','b74a016c','04441cbc','7319bba9','1c368173','cfeb996a']:
    f=glob.glob(D+'/'+d+'/runs/*/judge-evidence.json')[0]
    raw=open(f,'rb').read(); ev=json.loads(raw)
    c=len(cj(ev)); print(d,len(raw),c,'equal' if c==len(raw) else 'DIFF',524288-c)
