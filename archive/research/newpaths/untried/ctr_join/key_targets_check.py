"""Check the target sets used by struct_split.py against coupling.py's diffs().

key1 must be a function of (E1.a2, E1.b1, E1.d1) only: move the E1 inputs along the 2-word
null direction (new E1.a1, new Y1; Y12, w5, w12 compensate) and key1 must not change.
key3 is a function of (E3.h1, E3.g1, E3.f1, E3.e2): that map from (Y4, Y9, Y14, w8) is a
bijection; checked by inverting it.
"""

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

import random
import sys

sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/grok/work/job30_split'))
from coupling import World  # noqa: E402

w = World(32)
M = w.MASK
rng = random.Random(9)
N = 20000
bad1 = bad3 = moved = 0
for _ in range(N):
    Y1, Y6, Y12, w12, w5, Y4, Y9, Y14, w8 = [rng.getrandbits(32) for _ in range(9)]
    k1, k3, _, _ = w.diffs((Y1, Y6, Y12, w12, w5), (Y4, Y9, Y14, w8))
    a1 = (Y1 + Y6 + w12) & M
    d1 = w.ror(Y12 ^ a1, 16)
    c1 = (w.Y11 + d1) & M
    b1 = w.ror(Y6 ^ c1, 12)
    a2 = (a1 + b1 + w5) & M
    a1n = rng.getrandbits(32)
    Y1n = rng.getrandbits(32)
    Y12n = w.rol(d1, 16) ^ a1n
    w5n = (a2 - a1n - b1) & M
    w12n = (a1n - Y1n - Y6) & M
    k1n, _, _, _ = w.diffs((Y1n, Y6, Y12n, w12n, w5n), (Y4, Y9, Y14, w8))
    bad1 += (k1n != k1)
    moved += (Y12n, w5n, w12n) != (Y12, w5, w12)
    # E3: (Y4,Y9,Y14,w8) -> (h1,g1,f1,e2) and back
    ea1 = (w.Y3 + Y4) & M
    h1 = w.ror(Y14 ^ ea1, 16)
    g1 = (Y9 + h1) & M
    f1 = w.ror(Y4 ^ g1, 12)
    e2 = (ea1 + f1 + w8) & M
    Y4r = w.rol(f1, 12) ^ g1
    Y9r = (g1 - h1) & M
    Y14r = w.rol(h1, 16) ^ ((w.Y3 + Y4r) & M)
    w8r = (e2 - w.Y3 - Y4r - f1) & M
    bad3 += (Y4r, Y9r, Y14r, w8r) != (Y4, Y9, Y14, w8)
line = ("key1 from (E1.a2,E1.b1,E1.d1): %d mismatches in %d moves along the null direction (inputs moved %d); "
        "E3 inputs <-> (h1,g1,f1,e2) inverse: %d mismatches in %d" % (bad1, N, moved, bad3, N))
print(line)
open('key_targets_check.txt', 'w', encoding='utf-8').write(line + '\n')
