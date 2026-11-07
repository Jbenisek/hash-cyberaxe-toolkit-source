
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

import sys,gc,tracemalloc,time
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/tools/build_pkg/scratch/pkgR5T/pkg/sha3-256-r5/experiments'))
from r5 import *
lab=rlab(7,37)
base,OB=Base(),own_bits()
gc.collect(); tracemalloc.start()
b0=tracemalloc.get_traced_memory()[0]
r=bprime(base,OB,lab)
gc.collect()
cur,pk=tracemalloc.get_traced_memory()
print("bprime: peak over base",pk-b0,"live after return",cur-b0)
st=Setup(base,r[0],r[1]); gc.collect()
cur2=tracemalloc.get_traced_memory()[0]
print("after Setup(Cand) live over base",cur2-b0)
tracemalloc.reset_peak()
spaces=[];i=0;c=r[2]
while len(spaces)<5:
    s,info=attempt(st,Coins(run_seed(lab+b"conn"+(c+1).to_bytes(4,"little"),i)));i+=1
    if s=="ok": spaces.append(info)
gc.collect();cur3,pk3=tracemalloc.get_traced_memory()
print("connector phase 5 EM: peak over base",pk3-b0,"live",cur3-b0, "per EM", (cur3-cur2)/5)
