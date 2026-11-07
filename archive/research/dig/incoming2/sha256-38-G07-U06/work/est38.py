
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

import os,glob,sys
S=_hca_public_path_text('__HCA_WORKSPACE__/research/tools/build_pkg/scratch')
for p in ['pkgR38N','pkgR38N2','pkgR38L','pkgR38M3']:
    pkg=os.path.join(S,p,'pkg'); T=os.path.join(pkg,'sha256-r38')
    proof=open(os.path.join(T,'proof.md'),encoding='utf-8').read().replace('\r\n','\n')
    note=glob.glob(os.path.join(pkg,'submission-note*.md'))[0]; dep=os.path.join(pkg,'dependencies.json')
    shipped=[f for f in glob.glob(T+'/**/*',recursive=True) if os.path.isfile(f) and '__pycache__' not in f]
    est=len(proof.encode())+9*proof.count('\n')+sum(os.path.getsize(f) for f in shipped if not f.endswith('proof.md'))
    est+=os.path.getsize(note)+(os.path.getsize(dep) if os.path.exists(dep) else 0)
    prog=[f for f in shipped if f.endswith('.py')]
    print(p,'est',est,'prog',[(os.path.basename(f),os.path.getsize(f)) for f in prog],'proofB',len(proof.encode()),'lines',proof.count('\n'))
