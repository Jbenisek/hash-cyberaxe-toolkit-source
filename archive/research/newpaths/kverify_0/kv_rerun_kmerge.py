"""kverify_0: rerun kmath/kmerge.py (read-only import) claim2 and c4k4 configs; log to this folder."""

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

import sys
import time
sys.dont_write_bytecode = True
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/newpaths/kmath'))
import kmerge

with open("kmerge_rerun.txt", "a") as log:
    log.write(f"=== rerun {time.ctime()}\n")
    kmerge.claim2(12, [6, 12, 18], log)
    kmerge.claim2(16, [8, 16, 20], log)
    for cfg in kmerge.configs(8, ["c4k4", "c4k8", "c3k4", "c2k2"]):
        kmerge.run(*cfg, log)
    kmerge.small_lists(log)
