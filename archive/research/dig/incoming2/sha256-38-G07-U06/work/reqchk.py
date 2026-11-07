
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

import json,hashlib,glob
def canon(v): return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode()
rep=json.load(open(glob.glob(_hca_public_path_text('__HCA_WORKSPACE__/research/dossiers/cfeb996a/runs/*/experiment-report.json'))[0]))
for e in rep['execution']['experiments']:
    print(e['id'],e['request_sha256'][:16],e.get('reproducibility'),e['organizer_digest_evaluations'])
    r=json.load(open('req_N_%s_pub.json'%e['id']))
    print(' mine canon',hashlib.sha256(canon(r)).hexdigest()[:16],'raw',hashlib.sha256(open('req_N_%s_pub.json'%e['id'],'rb').read()).hexdigest()[:16])
