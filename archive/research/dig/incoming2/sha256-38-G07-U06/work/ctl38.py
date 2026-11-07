
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

import sys,json,time
sys.path.insert(0,_hca_public_path_text('__HCA_WORKSPACE__/hash-smash'))
from experiments import runner as R
W=_hca_public_path_text('__HCA_WORKSPACE__/research/dig/incoming2/sha256-38-G07-U06/work/')
S=_hca_public_path_text('__HCA_WORKSPACE__/research/tools/build_pkg/scratch/pkgR38L/pkg/sha256-r38/experiments/vt38.py')
src=open(S,'rb').read(); req=json.load(open(W+'req_L_vt-q3-smc-r38_pub.json'))
for to in (1.0,20.0):
    lim=R.ExperimentLimits(timeout_seconds=to); t=time.time()
    try:
        out=R._run_docker(src,req,lim,R.DEFAULT_DOCKER_IMAGE); print('timeout',to,'PASS',round(time.time()-t,2),'s bytes',len(out))
    except Exception as e: print('timeout',to,'RAISED',type(e).__name__,str(e)[:80],round(time.time()-t,2),'s')
print('size rule: shipped L',len(src),'N',len(open(S.replace('pkgR38L','pkgR38N'),'rb').read()))
