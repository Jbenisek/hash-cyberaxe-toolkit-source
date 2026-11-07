
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

import sys, numpy as np, random
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/levels/U9'))
from u9_toylib import toy_params
def sched(r): return list(range(0,4))+list(range(4,4+r))+list(range(60,64))
def kind(i): return 'full' if (i<4 or i>=60) else 'partial'
