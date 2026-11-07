"""Home-run trail door, step 1: the fixed difference after the two affine rounds of the W40 field, and its chi3-input image.
For each field direction w_i: D_i(x) = R1(R0(x)) xor R1(R0(x xor w_i)) (state after round index 1, organizer round function via
cube_degree.py). On every coset the map is affine, so D_i(x) must not depend on x - checked on many random x. Linearity of the
difference map (D(w_i xor w_j) = D_i xor D_j) checked on random combinations. Then B3_i = theta/rho/pi of round index 2 applied to
D_i (linear; constants cancel in differences) = the chi3 input difference. Writes l2_b3.bin (40 x 25 u64, little endian) and
prints the per-direction chi3 active-row counts. Usage: python step1_l2.py"""

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

import sys, pathlib, random, struct
import numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3] / 'research' / 'sha3r6' / 'lowdegree'))
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/sha3r6/lowdegree'))
import cube_degree as cd

U = np.uint64
MASK = (1 << 64) - 1
rng = random.Random(20261010)

def two_rounds(srcs):                     # list of 320-bit ints -> 25 lanes (numpy arrays) after rounds 0 and 1
    u = [np.array([(s >> (64 * k)) & MASK for s in srcs], dtype=U) for k in range(5)]
    A = cd.lanes(u)
    for r in range(2):
        A = cd.rnd(A, r)
    return A

def trp(A):                               # theta, rho, pi of a round (linear on differences)
    C = [A[x] ^ A[x + 5] ^ A[x + 10] ^ A[x + 15] ^ A[x + 20] for x in range(5)]
    D = [C[(x - 1) % 5] ^ cd.rot(C[(x + 1) % 5], 1) for x in range(5)]
    B = [None] * 25
    for y in range(5):
        for x in range(5):
            B[y + 5 * ((2 * x + 3 * y) % 5)] = cd.rot(A[x + 5 * y] ^ D[x], cd.RHO[x + 5 * y])
    return B

W = cd.W
assert len(W) == 40
NX = 64
xs = [rng.getrandbits(320) for _ in range(NX)]
base = two_rounds(xs)
Dvec = []
bad_affine = 0
for i, w in enumerate(W):
    other = two_rounds([x ^ w for x in xs])
    diff = [base[k] ^ other[k] for k in range(25)]
    for k in range(25):                    # must be the same for all NX random x
        if not np.all(diff[k] == diff[k][0]):
            bad_affine += 1
            break
    Dvec.append([int(diff[k][0]) for k in range(25)])
print('directions whose 2-round difference depends on x (must be 0):', bad_affine)

# linearity of the difference map on random combinations
bad_lin = 0
for _ in range(200):
    S = [j for j in range(40) if rng.getrandbits(1)]
    d = 0
    for j in S: d ^= W[j]
    other = two_rounds([x ^ d for x in xs[:8]])
    diff = [int((base[k][:8] ^ other[k])[0]) for k in range(25)]
    want = [0] * 25
    for j in S:
        for k in range(25): want[k] ^= Dvec[j][k]
    bad_lin += diff != want
print('random combinations violating linearity (must be 0):', bad_lin, 'of 200')

# chi3 input differences B3_i and their active-row counts (row = (y, z): the 5 lanes x = 0..4 of plane y at bit z)
B3 = []
for i in range(40):
    A = [np.array([Dvec[i][k]], dtype=U) for k in range(25)]
    B = trp(A)
    B3.append([int(B[k][0]) for k in range(25)])

def active_rows(v):
    n = 0
    for y in range(5):
        o = 0
        for x in range(5): o |= v[x + 5 * y]
        n += bin(o).count('1')
    return n

rows = [active_rows(b) for b in B3]
print('chi3 active rows per basis direction: min', min(rows), 'max', max(rows), 'mean', round(sum(rows) / 40, 1))
print('sorted:', sorted(rows))
out = pathlib.Path(__file__).resolve().parent / 'l2_b3.bin'
out.write_bytes(b''.join(struct.pack('<25Q', *b) for b in B3))
print('wrote', out.name, out.stat().st_size, 'bytes')
