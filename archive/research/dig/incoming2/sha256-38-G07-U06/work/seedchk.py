
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
r=json.load(open('req_N_vt-q3-smc-r38_pub.json'));s=r['trials'][0]['seed'];print(s)
for x in glob.glob(_hca_public_path_text('__HCA_WORKSPACE__/research/dossiers/cfeb996a/runs/*/*.json')):
    t=open(x,encoding='utf-8').read(); print(os.path.basename(x),len(t),s in t)
