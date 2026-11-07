"""Validate cd.rnd (6 rounds) against the organizer permutation() on FULL random states (nonzero capacity).
cd.selfcheck only covers capacity=0 (single-block sha3_256). This covers arbitrary capacity, so the
origin_test finding (capacity changes affinity at depth>=2) is trusted as the real round function, not a bug.
Usage: python validate.py NTRIALS SEED"""

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

import sys, random, importlib.util
import numpy as np
CD = _hca_public_path_text('__HCA_WORKSPACE__/research/sha3r6/lowdegree/cube_degree.py')
spec = importlib.util.spec_from_file_location('cd', CD); cd = importlib.util.module_from_spec(spec); spec.loader.exec_module(cd)
kec = cd.kec
U = np.uint64; MASK = (1 << 64) - 1

def organizer_perm6(lanes25):
    state = b''.join((l & MASK).to_bytes(8, 'little') for l in lanes25)
    out = kec.permutation(state, width_bits=1600, rounds=6)
    return [int.from_bytes(out[8 * i:8 * i + 8], 'little') for i in range(25)]

def cdrnd6(lanes25):
    A = [np.array([U(l & MASK)], dtype=U) for l in lanes25]
    for i in range(6):
        A = cd.rnd(A, i)
    return [int(a[0]) for a in A]

if __name__ == '__main__':
    n = int(sys.argv[1]); seed = int(sys.argv[2]); rng = random.Random(seed)
    ok = 0
    for _ in range(n):
        lanes = [rng.getrandbits(64) for _ in range(25)]          # full random: capacity lanes 17-24 nonzero
        ok += int(organizer_perm6(lanes) == cdrnd6(lanes))
    print(f'cd.rnd(6) == organizer permutation(rounds=6) on {ok}/{n} FULL random states (nonzero capacity)')
