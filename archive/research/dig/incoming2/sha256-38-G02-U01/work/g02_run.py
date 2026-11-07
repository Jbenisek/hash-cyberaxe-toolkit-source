
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

import sys, math
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/dig/incoming2/sha256-38-G02-U01/work'))
from g02_ledger38 import ledger, Fr
def S(o): return o['log2_T'] + max(0.0, o['memory_log2_bytes'] - 20)
if __name__ == '__main__':
    o = ledger(show=False)
    print('k0', o['time_log2'], o['memory_log2_bytes'], o['T_num'], o['words'], S(o))
    o19 = ledger(show=False, B=1 << 19)
    print('k19', o19['time_log2'], o19['memory_log2_bytes'], o19['NG'], o19['T_num'], o19['T_den'], o19['words'], o19['words']*32, S(o19))
