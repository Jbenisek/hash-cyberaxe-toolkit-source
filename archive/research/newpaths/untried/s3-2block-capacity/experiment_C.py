"""s3-2block-capacity / experiment_C.py
Measure the 2-round and 3-round AFFINE FIELD DIMENSION as a function of block-2 capacity.

Directions live in the 320-bit source (u0..u4, copied to rows 0 and 2 -> round 1 affine for ANY source dir
and ANY capacity, verified by origin_test k=1). Capacity = constant on lanes 17-24 (set by block 1).

F2 is degree 2 globally (round1 affine), so a subspace V is 2-round-affine  <=>  every pair in V has zero
F2 cube-sum (totally isotropic for the polarization B2). Greedy builds a maximal such V.
Within V, F3 = chi3 o affine is degree 2, so a sub-subspace is 3-round-affine <=> totally isotropic for B3.
Greedy builds a maximal 3-round field inside V. Final fields are re-verified with full cube sums on several
random cosets (all-order check, not just pairwise).

cap modes: zero | cap<seed>  (random capacity on lanes 17-24) | full<seed> (also non-source rate lanes 5-9,15)
Usage: python experiment_C.py CAPMODE GREEDY_SEEDS NTRIALS VERIFY_COSETS
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

def cap_base(mode):
    C = [0] * 25
    if mode == 'zero':
        return C
    seed = int(mode[3:]) if mode.startswith('cap') else int(mode[4:])
    rng = random.Random(10000 + seed)
    lanes = range(17, 25) if mode.startswith('cap') else list(range(5, 10)) + [15] + list(range(17, 25))
    for i in lanes:
        C[i] = rng.getrandbits(64)
    return C

def Fk(srcs, C, k):
    """srcs: list of 320-bit source ints. Returns 25 lane arrays after k organizer rounds."""
    n = len(srcs)
    uk = [np.fromiter(((s >> (64 * j)) & MASK for s in srcs), dtype=U, count=n) for j in range(5)]
    A = [np.full(n, U(C[i] & MASK)) for i in range(25)]
    for j in range(5):
        A[j] = A[j] ^ uk[j]; A[10 + j] = A[10 + j] ^ uk[j]
    A[16] = A[16] ^ U(0x86 << 56)
    for i in range(k):
        A = cd.rnd(A, i)
    return A

def statevec(A, idx):
    v = 0
    for i in range(25):
        v |= (int(A[i][idx]) & MASK) << (64 * i)
    return v

def gf2_rank(vecs):
    piv = {}; rk = 0
    for v in vecs:
        v = int(v)
        while v:
            b = v.bit_length() - 1
            if b in piv: v ^= piv[b]
            else: piv[b] = v; rk += 1; break
    return rk

def in_span(v, basis_piv):
    v = int(v)
    for b in sorted(basis_piv, reverse=True):
        if (v >> b) & 1: v ^= basis_piv[b]
    return v == 0

def add_span(v, basis_piv):
    v = int(v)
    while v:
        b = v.bit_length() - 1
        if b in basis_piv: v ^= basis_piv[b]
        else:
            basis_piv[b] = v; return True
    return False

def greedy_field(C, k, base_t, rng, ntrials, cand_fn):
    """Greedy maximal totally-isotropic subspace for the F_k polarization at coset base_t.
    cand_fn(rng) -> a random 320-bit source direction. Returns list S of basis directions."""
    S = []; piv = {}
    Ft = statevec(Fk([base_t], C, k), 0)
    Fts = []  # F(t ^ s) for s in S
    for _ in range(ntrials):
        d = cand_fn(rng)
        if d == 0 or in_span(d, piv):
            continue
        Ftd = statevec(Fk([base_t ^ d], C, k), 0)
        if not S:
            S.append(d); add_span(d, piv); Fts.append(Ftd); continue
        cross = Fk([base_t ^ d ^ s for s in S], C, k)
        ok = True
        for m, s in enumerate(S):
            b = Ft ^ Ftd ^ Fts[m] ^ statevec(cross, m)   # B_k(d, s)
            if b != 0: ok = False; break
        if ok:
            S.append(d); add_span(d, piv); Fts.append(Ftd)
    return S

def verify_field(C, dirs, k, ncosets, npairs, rng):
    """Full all-order cube-sum check: is F_k affine on random cosets of span(dirs)?
    Samples subsets (cube over the subset's span) up to size min(len(dirs), 8)."""
    if len(dirs) < 2:
        return 0, 0
    bad = 0; tot = 0
    for _ in range(ncosets):
        t = rng.getrandbits(320)
        for _ in range(npairs):
            ssz = rng.randint(2, min(len(dirs), 8))
            sub = rng.sample(dirs, ssz)
            pts = []
            for m in range(1 << ssz):
                x = t
                for b in range(ssz):
                    if m >> b & 1: x ^= sub[b]
                pts.append(x)
            A = Fk(pts, C, k)
            cs = [int(np.bitwise_xor.reduce(A[i])) for i in range(25)]
            bad += int(any(cs)); tot += 1
    return bad, tot

if __name__ == '__main__':
    capmode = sys.argv[1]; gseeds = int(sys.argv[2]); ntrials = int(sys.argv[3]); vcos = int(sys.argv[4])
    C = cap_base(capmode)
    print(json.dumps({'capmode': capmode, 'cap_lanes_set': [i for i in range(25) if C[i]]}), flush=True)
    t_all = time.time()

    coord = lambda rng: 1 << rng.randrange(320)
    def combo(rng):
        v = 0
        for _ in range(rng.randint(1, 6)):
            v ^= 1 << rng.randrange(320)
        return v

    best2 = []
    for g in range(gseeds):
        rng = random.Random(900 + g)
        base_t = rng.getrandbits(320)
        S2 = greedy_field(C, 2, base_t, rng, ntrials, combo)
        if gf2_rank(S2) > gf2_rank(best2):
            best2 = S2
    d2 = gf2_rank(best2)
    vb2 = verify_field(C, best2, 2, vcos, 40, random.Random(7))
    print(json.dumps({'round2_field_dim': d2, 'verify_bad_over_tot': f'{vb2[0]}/{vb2[1]}', 'sec': round(time.time() - t_all, 1)}), flush=True)

    # 3-round field INSIDE the best 2-round field V (directions = combinations of best2 basis)
    best3 = []
    if d2 >= 2:
        V = best2
        def vcombo(rng):
            v = 0
            for b in range(len(V)):
                if rng.getrandbits(1): v ^= V[b]
            return v
        for g in range(gseeds):
            rng = random.Random(1300 + g)
            base_t = rng.getrandbits(320)
            S3 = greedy_field(C, 3, base_t, rng, ntrials, vcombo)
            if gf2_rank(S3) > gf2_rank(best3):
                best3 = S3
    d3 = gf2_rank(best3)
    vb3 = verify_field(C, best3, 3, vcos, 40, random.Random(11))
    print(json.dumps({'round3_field_dim': d3, 'verify_bad_over_tot': f'{vb3[0]}/{vb3[1]}',
                      'total_sec': round(time.time() - t_all, 1)}), flush=True)
