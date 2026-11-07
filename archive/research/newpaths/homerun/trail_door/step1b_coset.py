"""Step 1b: within ONE coset t + span(W40) the 2-round difference of the pair (x, x xor w_i) must be constant (= L_t(w_i)).
For 4 random cosets: check constancy over 32 points of the coset, then the chi3 active rows of L_t(w_i) and of 2^20 random
combinations d (the minimum seen estimates how light the best field difference can be). Usage: python step1b_coset.py"""

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

import sys, random
import numpy as np
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/sha3r6/lowdegree'))
import cube_degree as cd
from step1_l2 import two_rounds, trp, active_rows, MASK, U

rng = random.Random(4242)
W = cd.W
for c in range(4):
    t = rng.getrandbits(320)
    pts = []
    for _ in range(32):
        v = 0
        for j in range(40):
            if rng.getrandbits(1): v ^= W[j]
        pts.append(t ^ v)
    base = two_rounds(pts)
    L, nonconst = [], 0
    for w in W:
        o = two_rounds([p ^ w for p in pts])
        diff = [base[k] ^ o[k] for k in range(25)]
        nonconst += any(not np.all(diff[k] == diff[k][0]) for k in range(25))
        L.append([int(diff[k][0]) for k in range(25)])
    B = [[int(b[0]) for b in trp([np.array([L[i][k]], dtype=U) for k in range(25)])] for i in range(40)]
    rows = [active_rows(b) for b in B]
    best = 10**9
    for _ in range(1 << 14):
        S = rng.getrandbits(40) or 1
        acc = [0] * 25
        for j in range(40):
            if S >> j & 1:
                for k in range(25): acc[k] ^= B[j][k]
        best = min(best, active_rows(acc))
    print(f'coset {c}: directions with x-dependent difference inside the coset = {nonconst} (must be 0); '
          f'chi3 active rows per direction min {min(rows)} max {max(rows)}; min over 2^14 random combinations {best} of 320')
