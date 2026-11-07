
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
for d in ['cfeb996a','1393e83b']:
    f=glob.glob(D+'/'+d+'/runs/*/judge-evidence.json')[0]
    j=json.load(open(f,encoding='utf-8'))
    n=0
    def walk(o):
        global n
        if isinstance(o,dict):
            if 'untrusted_source_text' in o:
                os.makedirs(d,exist_ok=True)
                nm=o.get('path','x%d'%n); n+=1
                open(d+'/'+nm.replace('/','_'),'w',encoding='utf-8',newline='').write(o['untrusted_source_text']); print(d,nm,o.get('size_bytes'))
            for v in o.values(): walk(v)
        elif isinstance(o,list):
            for v in o: walk(v)
    walk(j)
