
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

import json,glob,os
D=_hca_public_path_text('__HCA_WORKSPACE__/research/dossiers')
rows=[]
for f in glob.glob(D+'/*/runs/*/judge-evidence.json'):
    run=os.path.dirname(f); raw=open(f,'rb').read(); ev=json.loads(raw)
    canon=json.dumps(ev,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
    tr=ev['benchmark'].get('track_id','')
    ir=ev['submission']['intake_report']
    rows.append((os.path.basename(os.path.dirname(os.path.dirname(run))),len(raw),len(canon),tr,ir.get('package_sha256','')[:8]))
rows.sort(key=lambda r:r[1])
for r in rows: print(*r, 524288-r[2])
