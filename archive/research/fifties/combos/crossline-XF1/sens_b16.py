# Copy of grok_xfer\claude_check\sens.py with b restricted to (14, 16): the full sens.py also runs b = 24
# (2^24 bit-serial alive() calls), which exceeded the 2-minute step-1 limit and is not needed by the XF1 claim.
# Everything else is unchanged.

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
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/tools/build_pkg/scratch/pkgCJ/work'))
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/fifties/combos/grok_xfer/claude_check'))
import frontline_full as F
from window14 import alive
for b in (14, 16):
    n = 1 << b
    al = bytearray(alive(x, b) for x in range(n))
    a9 = [alive(x, 9) for x in range(512)]
    dom = [x for x in range(n) if a9[x & 511]]
    print("b=%d alive share in alive9 domain %.5f" % (b, sum(al[x] for x in dom) / len(dom)))
    print("  bit: sensitivity count (flip changes alive_b, both in domain)")
    out = []
    for i in range(b):
        c = sum(1 for x in dom if a9[(x ^ (1 << i)) & 511] and al[x] != al[x ^ (1 << i)])
        out.append("%d:%d" % (i, c))
    print("  " + " ".join(out))
    if b <= 16:
        pats = {}
        for p in range(512):
            if not a9[p]: continue
            pats.setdefault(bytes(al[p | (h << 9)] for h in range(1 << (b - 9))), []).append(p)
        print("  distinct alive patterns over the high window, across alive 9-bit prefixes:", len(pats),
              [ (len(v), min(v)) for v in pats.values()][:12])
