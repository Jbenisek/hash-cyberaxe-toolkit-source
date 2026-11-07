"""Parameterised copy of the op tracer of candidate_blake3/experiments/rho.py (our code). Counts ops of the 7-lane SWAR chain step
for any constant block layout. Base case must give 595."""

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
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/blake3_r3/candidate_blake3/experiments'))
import rho
from rho import Tracer, GCALLS, PERM, IV, M32
def trace(cv=IV, ctr=0, blen=64, flags=11, mconst=(0,)*8, varpos=tuple(range(8,16)), rounds=3):
    tr = Tracer()
    v = [("c", w) for w in cv] + [("c", w) for w in IV[:4]] + [("c", ctr & M32), ("c", ctr >> 32), ("c", blen), ("c", flags)]
    m = [("c", 0)] * 16
    ci = iter(mconst)
    for p in range(16):
        if p in varpos: m[p] = ("v", "i%d" % p, M32)
        else: m[p] = ("c", next(ci) if p < 8 else 0)
    for _ in range(rounds):
        for j, (a, b, c, d) in enumerate(GCALLS):
            x, y = m[2*j], m[2*j+1]
            v[a] = tr.add(v[a], v[b], x); v[d] = tr.ror(tr.xor(v[d], v[a]), 16)
            v[c] = tr.add(v[c], v[d]);     v[b] = tr.ror(tr.xor(v[b], v[c]), 12)
            v[a] = tr.add(v[a], v[b], y);  v[d] = tr.ror(tr.xor(v[d], v[a]), 8)
            v[c] = tr.add(v[c], v[d]);     v[b] = tr.ror(tr.xor(v[b], v[c]), 7)
        m = [m[i] for i in PERM]
    for i in range(8):
        z = tr.xor(v[i], v[i+8])
        if z[2] > M32: z = tr.mask(z)
    return tr.ops, dict(tr.by)
if __name__ == "__main__":
    print(trace())
