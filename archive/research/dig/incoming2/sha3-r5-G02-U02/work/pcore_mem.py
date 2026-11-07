
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

import sys,resource,importlib.util,tracemalloc,json
SRC=_hca_public_path_text('__HCA_WORKSPACE__/research/tools/build_pkg/scratch/pkgR5M/pkg/sha3-256-r5/experiments/r5.py')
spec=importlib.util.spec_from_file_location("r5",SRC); R=importlib.util.module_from_spec(spec); sys.modules["r5"]=R; spec.loader.exec_module(R)
c=R.ALPHA3_BITS  # the certified core (10 rows)
r0=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
tracemalloc.start()
H=R.halves(c)
cur,peak=tracemalloc.get_traced_memory()
print(json.dumps({"entries":[len(h[0]) for h in H],"trace_cur_B":cur,"trace_peak_B":peak,"rss0_KB":r0,"rss_KB":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}))
