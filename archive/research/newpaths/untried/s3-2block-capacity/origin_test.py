"""s3-2block-capacity / origin_test.py
Question: in a 2-block message, block-1 sets block-2's 512 capacity bits (chosen at cost ~2^c for c linear
conditions). Does a nonzero/chosen capacity enlarge the rounds-affine field for block 2, or deepen it
(2-round -> 3-round), relative to the single-block capacity=0 case?

Math being tested: affinity of a round map on a direction-span is governed by the SECOND finite difference
(cube sum over a pair of directions) = the polarization. For a degree-<=2 map this is a CONSTANT, independent
of the base point. The capacity is part of the base point. So capacity cannot change affinity of any map that
is degree<=2 on the field. W40 makes rounds 0-1 affine, so F2 is degree 2 and F3 = chi3 o affine is degree 2
on W40 -> origin-independent. This script verifies it on the organizer round function (cd.rnd, verified vs
keccak.py by cd.selfcheck).

Outputs per round depth k=1..4:
  - affine_defect_rank: GF(2) rank of the set of 2nd differences {D_wi D_wj F_k} over W40 pairs
    (0 => F_k is affine on all of W40; >0 => not affine, max affine subspace is smaller).
  - cap_variant_mismatches: number of pairs whose 2nd difference DIFFERS between capacity=0 and a
    random capacity base (and a second random base). 0 => capacity provably irrelevant at this depth.
Control: random SOURCE directions outside W40 (chi1 already quadratic) -> F3 2nd diff SHOULD depend on capacity.
Usage: python origin_test.py SEED NPAIRS
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

import sys, json, time, random, importlib.util
import numpy as np

CD = _hca_public_path_text('__HCA_WORKSPACE__/research/sha3r6/lowdegree/cube_degree.py')
spec = importlib.util.spec_from_file_location('cd', CD); cd = importlib.util.module_from_spec(spec); spec.loader.exec_module(cd)
U = np.uint64; MASK = (1 << 64) - 1
W = cd.W  # 40 direction vectors (320-bit ints), rank 40

def build(u, C):
    """Full 25-lane state: source structure u (copies in rows 0 and 2, pad 0x86 in lane 16) + base constant C.
    C must be 0 on source/pad lanes 0-4,10-14,16; nonzero C on lanes 17-24 == a chosen capacity."""
    n = len(u[0])
    A = [np.full(n, U(C[i] & MASK)) for i in range(25)]
    for k in range(5):
        A[k] = A[k] ^ u[k]; A[10 + k] = A[10 + k] ^ u[k]
    A[16] = A[16] ^ U(0x86 << 56)
    return A

def Fk(u, C, k):
    A = build(u, C)
    for i in range(k):
        A = cd.rnd(A, i)
    return A

def second_diff(t, a, b, C, k):
    """D_a D_b F_k at base (source t, capacity/base C): cube sum over the 4 points of span{a,b}."""
    u = cd.points(t, [a, b])
    A = Fk(u, C, k)
    return [int(np.bitwise_xor.reduce(A[i])) for i in range(25)]

def to_bitvec(lanes25):
    v = 0
    for i, w in enumerate(lanes25):
        v |= (w & MASK) << (64 * i)
    return v

def gf2_rank(vecs):
    piv = {}; rk = 0
    for v in vecs:
        while v:
            b = v.bit_length() - 1
            if b in piv: v ^= piv[b]
            else: piv[b] = v; rk += 1; break
    return rk

def cap_base(rng, mode):
    C = [0] * 25
    if mode == 'zero':
        return C
    lanes = range(17, 25) if mode == 'cap' else list(range(5, 10)) + [15] + list(range(17, 25))
    for i in lanes:
        C[i] = rng.getrandbits(64)
    return C

if __name__ == '__main__':
    seed = int(sys.argv[1]); npairs = int(sys.argv[2])
    rng = random.Random(seed)
    print(json.dumps({'W_rank': cd.rank(W), 'sponge_selfcheck_cap0': cd.selfcheck(rng)}), flush=True)

    # fixed set of W40 direction pairs (basis pairs, capped at npairs), plus some random combinations
    pairs = []
    for i in range(len(W)):
        for j in range(i + 1, len(W)):
            pairs.append((W[i], W[j]))
    rng.shuffle(pairs); pairs = pairs[:npairs]

    t0 = rng.getrandbits(320); t1 = rng.getrandbits(320)
    C0 = cap_base(rng, 'zero')
    Ccap = cap_base(rng, 'cap')       # pure capacity (lanes 17-24)
    Ccap2 = cap_base(rng, 'cap')
    Cfull = cap_base(rng, 'full')     # capacity + non-source rate base (lanes 5-9,15,17-24)

    table = []
    for k in (1, 2, 3, 4):
        tk = time.time()
        defect = []           # 2nd diffs at base (t0, C0) -> rank measures non-affinity on W40
        mm_cap = mm_cap2 = mm_full = mm_t = 0
        for (a, b) in pairs:
            d00 = second_diff(t0, a, b, C0, k)
            d_cap = second_diff(t0, a, b, Ccap, k)
            d_cap2 = second_diff(t0, a, b, Ccap2, k)
            d_full = second_diff(t0, a, b, Cfull, k)
            d_t1 = second_diff(t1, a, b, Ccap, k)
            v = to_bitvec(d00); defect.append(v)
            mm_cap += int(to_bitvec(d_cap) != v)
            mm_cap2 += int(to_bitvec(d_cap2) != v)
            mm_full += int(to_bitvec(d_full) != v)
            mm_t += int(to_bitvec(d_t1) != to_bitvec(d_cap))   # vary source base too, capacity fixed
        table.append({'k': k, 'pairs': len(pairs),
                      'affine_defect_rank': gf2_rank(defect),
                      'nonzero_2nd_diffs': sum(1 for v in defect if v),
                      'mismatch_vs_cap': mm_cap, 'mismatch_vs_cap2': mm_cap2,
                      'mismatch_vs_full': mm_full, 'mismatch_vs_sourcebase': mm_t,
                      'sec': round(time.time() - tk, 1)})
        print(json.dumps(table[-1]), flush=True)

    # CONTROL: random source directions OUTSIDE W40 (chi1 quadratic) -> F3 2nd diff must depend on capacity
    print('--- control: random source directions (outside W40) ---', flush=True)
    for k in (1, 2, 3):
        dep = 0; nz = 0; cpairs = []
        for _ in range(min(npairs, 40)):
            a = rng.getrandbits(320); b = rng.getrandbits(320)
            v0 = to_bitvec(second_diff(t0, a, b, C0, k))
            vc = to_bitvec(second_diff(t0, a, b, Ccap, k))
            dep += int(v0 != vc); nz += int(v0 != 0)
        print(json.dumps({'control_k': k, 'nonzero_2nd_diffs': nz,
                          'cap_dependent_2nd_diffs': dep, 'of': min(npairs, 40)}), flush=True)
