"""Test the low-degree (FES) route at EVERY round depth r=3..7 (reusing the certified W40 embedding
from research/sha3r6/lowdegree/cube_degree.py). For each r:
  f_t(u) = chi_r-input = rounds 0..r-2 full + theta/rho/pi of round r-1, row y=0 (5 lanes = 320 bits).
  Claim (D19): deg f_t <= D = 2^(r-3), and chi_r+iota(f_t) = sha3_256(msg, rounds=r).
Checks, on a small inner dimension n and WORD cosets:
  (1) FES Gray chain at degree D reproduces direct evaluation at every point (0 mismatches => route works);
  (2) control at degree D-1 FAILS where n>D-1 (confirms degree is exactly 2^(r-3), tight);
  (3) explicit chi_r+iota of the FES planes == organizer sha3_256(rounds=r) on sample (coset,point) pairs.
Usage: python test_fes_by_round.py
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

import sys, time, random
import numpy as np
from itertools import combinations
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/sha3r6/lowdegree'))
import cube_degree as cd

U = np.uint64
MASK = (1 << 64) - 1

def pre_chi_r(A, r):                 # rounds 0..r-2 full, then theta/rho/pi of round r-1; return row0 lanes 0..4
    for i in range(r - 1):
        A = cd.rnd(A, i)
    C = [A[x] ^ A[x + 5] ^ A[x + 10] ^ A[x + 15] ^ A[x + 20] for x in range(5)]
    Dd = [C[(x - 1) % 5] ^ cd.rot(C[(x + 1) % 5], 1) for x in range(5)]
    Bl = [None] * 25
    for y in range(5):
        for x in range(5):
            Bl[y + 5 * ((2 * x + 3 * y) % 5)] = cd.rot(A[x + 5 * y] ^ Dd[x], cd.RHO[x + 5 * y])
    return Bl[0:5]

def fes_once(r, n, WORD, SAMPLE, D, seed):
    rng = random.Random(seed)
    dirs = rng.sample(cd.W, n)
    starts = [rng.getrandbits(320) for _ in range(WORD)]
    P = 1 << n
    u = [np.concatenate([cd.points(s, dirs)[k] for s in starts]) for k in range(5)]
    B = pre_chi_r(cd.lanes(u), r)                              # 5 lanes, each WORD*P points
    bits = np.stack([np.unpackbits(b.view(np.uint8).reshape(-1, 8), axis=1, bitorder='little') for b in B], axis=1)
    bits = bits.reshape(WORD, P, 320)
    F = np.packbits(bits.transpose(1, 2, 0), axis=2, bitorder='little').view(U)[:, :, 0]   # [point, plane] vertical words
    g = lambda i: i ^ (i >> 1)
    def deriv(T, y):
        v = np.zeros(320, U)
        for m in range(1 << len(T)):
            e = 0
            for b, tt in enumerate(T):
                if m >> b & 1: e |= 1 << tt
            v ^= F[y ^ e]
        return v
    tab = {}
    for j in range(1, min(D, n) + 1):
        for T in combinations(range(n), j):
            tab[T] = deriv(T, g(sum(1 << q for q in T) - 1))
    x = F[0].copy(); bad = 0
    for i in range(1, P):
        ks = [q for q in range(n) if i >> q & 1][:D]
        L = len(ks)
        for j in range(L - 1, 0, -1):
            tab[tuple(ks[:j])] ^= tab[tuple(ks[:j + 1])]
        x ^= tab[(ks[0],)]
        bad += int(np.count_nonzero(x != F[g(i)]))
    # end-to-end: chi_r+iota of planes vs organizer sha3_256(rounds=r)
    want = sorted(rng.sample(range(P), min(SAMPLE, P)))
    ok = tot = 0
    for p in want:
        planes = F[p]
        for c in range(WORD):
            Bl = [0] * 5
            for k in range(5):
                w = 0
                for b in range(64):
                    w |= ((int(planes[64 * k + b]) >> c) & 1) << b
                Bl[k] = w
            dig = [(Bl[x] ^ (~Bl[(x + 1) % 5] & Bl[(x + 2) % 5])) & MASK for x in range(4)]
            dig[0] ^= int(cd.RC[r - 1])
            m = starts[c]
            for jj in range(n):
                if p >> jj & 1: m ^= dirs[jj]
            L25 = [0] * 25
            for k in range(5): L25[k] = (m >> (64 * k)) & MASK; L25[10 + k] = L25[k]
            L25[16] = 0x86 << 56
            msg = b''.join(l.to_bytes(8, 'little') for l in L25[:17])[:135]
            ok += cd.kec.sha3_256(msg, rounds=r) == b''.join(d.to_bytes(8, 'little') for d in dig); tot += 1
    return bad, (P - 1) * 320, ok, tot

def chi_r_input_cube(r, dims, ncubes, seed):
    """Vectorized cube/degree test on the chi_r-input f_t (rounds 0..r-2 + theta/rho/pi of round r-1),
    row0 320 bits. Returns, per dim d: fraction of ncubes whose XOR-sum over a random d-subspace of W40
    is nonzero. Degree is the largest d that is still nonzero (zero one above)."""
    rng = random.Random(seed)
    out = {}
    for d in dims:
        nz = 0
        for _ in range(ncubes):
            t = rng.getrandbits(320)
            dirs = rng.sample(cd.W, d)
            u = cd.points(t, dirs)
            B = pre_chi_r(cd.lanes(u), r)
            s = int(np.bitwise_xor.reduce(np.concatenate([b for b in B])))
            nz += (s != 0)
        out[d] = f"{nz}/{ncubes}"
    return out

if __name__ == '__main__':
    print(f"W rank = {cd.rank(cd.W)} (expect 40)")
    cfg = {3: (12, 64), 4: (12, 64), 5: (13, 64), 6: (13, 64)}   # r -> (n, WORD=64 for uint64 packing); r=7 via cube test (3^n init too slow)
    print("FES end-to-end (route works iff mismatches=0 at D and digests all match):")
    print("r | D=2^(r-3) | n | FES@D mismatches | FES@D-1 mismatches (control) | end-to-end digests | sec")
    for r in (3, 4, 5, 6):
        n, WORD = cfg[r]
        D = 1 << (r - 3)
        t0 = time.time()
        bad, tot_pw, ok, tot = fes_once(r, n, WORD, 6, D, 1000 + r)
        badc = ctot = -1
        if D - 1 >= 1:                       # control at degree D-1 (should fail when n > D-1)
            badc, ctot, _, _ = fes_once(r, n, WORD, 0, D - 1, 1000 + r)
        print(f"{r} | {D:>2} | {n} | {bad} of {tot_pw} | {badc} of {ctot} | {ok}/{tot} | {time.time()-t0:.1f}")
    print()
    print("Degree of the chi_r-input f_t via vectorized cubes (degree exactly D => nonzero at D, zero at D+1):")
    print("r | D=2^(r-3) | nonzero-cube fraction by dim")
    for r in (6, 7):
        D = 1 << (r - 3)
        dims = [D - 1, D, D + 1]
        t0 = time.time()
        res = chi_r_input_cube(r, dims, 40, 2000 + r)
        print(f"{r} | {D:>2} | " + "  ".join(f"dim{d}:{res[d]}" for d in dims) + f"  ({time.time()-t0:.1f}s)")
