
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

import json,sys,os
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/dig')); import add_cell
out=_hca_public_path_text('__HCA_WORKSPACE__/research/dig/incoming2/sha256-37-G04-U04')
def put(cell,rec):
    rec.update(hash='sha256-37',source='our workflow: scan-once-wave2',own_test=True,date='2026-10-12')
    rec['notes']='universe cell '+cell+' | '+rec['notes']
    fn=os.path.join(out,cell.replace('|','_').replace(' ','_')+'.json')
    json.dump(rec,open(fn,'w',encoding='utf-8'),indent=1)
    print(cell, add_cell.validate(json.load(open(fn,encoding='utf-8')),add_cell.load()))
ev='research/dig/incoming2/sha256-37-G04-U04/work/'
exec(open('records.py').read())
