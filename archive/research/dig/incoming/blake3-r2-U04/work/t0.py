
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

import sys,time,random
sys.path.insert(0,_hca_public_path_text('__HCA_WORKSPACE__/research/tools/build_pkg/scratch/pkgB3U/pkg/blake3-r2/experiments'))
t=time.time()
import frontline as F
print('import',time.time()-t)
random.seed(1)
ow=[random.getrandbits(32) for _ in range(7)]
e1,y=F.member(12345)
v=F.rebuild(ow,y,e1)
c1=random.getrandbits(32)
u=F.step_ct(v,c1)
ch=F.chart(u)
print(ch['cons'],[hex(x) for x in ch['cva']],[hex(x) for x in ch['cvb']])
