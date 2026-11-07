
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

import sys, os
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/tools/vm1mib'))
import build
H = os.path.dirname(os.path.abspath(__file__))
stack = int(sys.argv[1]) if len(sys.argv) > 1 else 4096
extra = sys.argv[2:]
ok = build.cc(os.path.join(H, "gen.c"), os.path.join(H, "gen.wasm"), ["run", "info_ptr", "code_ptr"], stack=stack, extra=["-Wall"] + extra)
sys.exit(0 if ok else 1)
