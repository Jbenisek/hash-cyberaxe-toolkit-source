"""B' working-set memory of the shipped r5.py (pkgR5M), unmodified, one R7 label.
usage: bprime_mem.py k mode   mode = rss | trace
Reports tracemalloc peak (python-allocated bytes above the post-Base baseline) or ru_maxrss, plus time."""

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

import sys, time, json, resource, importlib.util, tracemalloc, gc
SRC=_hca_public_path_text('__HCA_WORKSPACE__/research/tools/build_pkg/scratch/pkgR5M/pkg/sha3-256-r5/experiments/r5.py')
spec=importlib.util.spec_from_file_location("r5",SRC); r5=importlib.util.module_from_spec(spec); sys.modules["r5"]=r5; spec.loader.exec_module(r5)
from r5 import *
k=int(sys.argv[1]); mode=sys.argv[2]
label=("hashsmash sha3-256-r5 R7 run %d"%k).encode()
rss0=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
base=Base(); OB=own_bits(); gc.collect()
rss1=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
if mode=="trace": tracemalloc.start(); tracemalloc.reset_peak() if hasattr(tracemalloc,"reset_peak") else None
cur0=tracemalloc.get_traced_memory()[0] if mode=="trace" else 0
t0=time.time(); w0=WK.cost()
r=bprime(base,OB,label,B_BUDGET,None,0,CCAP,B_TRUE)
dt=time.time()-t0
out={"k":k,"mode":mode,"seconds":round(dt,1),"result_c_j_DF":None if r is None else [r[2],r[3],r[4]],
     "WK_prim_B_prime":WK.cost()-w0,"maxrss_KB_start":rss0,"maxrss_KB_after_Base":rss1,
     "maxrss_KB_end":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
if mode=="trace":
    cur,peak=tracemalloc.get_traced_memory(); out.update(trace_cur_B=cur-cur0, trace_peak_B=peak-cur0, trace_base_B=cur0)
print(json.dumps(out))
