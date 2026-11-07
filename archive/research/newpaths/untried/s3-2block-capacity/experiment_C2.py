"""s3-2block-capacity / experiment_C2.py  (exact-form version)
2-round and 3-round affine field dimension vs block-2 capacity, via EXACT polarization forms.

Round 1 is affine for ANY source direction and ANY capacity (origin_test k=1). So F2 is degree 2 on the whole
320-bit source; its polarization B2(a,b) = cube-sum over {a,b} is a GF(2)-bilinear form valued in GF(2)^1600.
A 2-round-affine field = max totally-isotropic subspace of B2 (isotropic for all 1600 scalar forms at once).
  - radical(B2) = {a : B2(a,.)=0 for all output bits}   (rigorous lower bound on the 2-round field)
  - maximal isotropic subspace (greedy grow by null-space)  (the 2-round field dimension)
At cap 0 this reproduces W40 (dim 40). Within the 2-round field V, F3=chi3 o affine is degree 2; its polarization
B3 on a basis of V gives the 3-round field = max isotropic of B3|V (cap 0 -> matches linstruct3 = 2).

Usage: python experiment_C2.py CAPMODE ORDERINGS     (CAPMODE: zero | cap<seed> | full<seed>)
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
    n = len(srcs)
    uk = [np.fromiter(((s >> (64 * j)) & MASK for s in srcs), dtype=U, count=n) for j in range(5)]
    A = [np.full(n, U(C[i] & MASK)) for i in range(25)]
    for j in range(5):
        A[j] = A[j] ^ uk[j]; A[10 + j] = A[10 + j] ^ uk[j]
    A[16] = A[16] ^ U(0x86 << 56)
    for i in range(k):
        A = cd.rnd(A, i)
    return A

def tovecs(A):
    n = len(A[0]); lanes = [np.asarray(A[i]) for i in range(25)]
    out = []
    for p in range(n):
        v = 0
        for i in range(25):
            v |= (int(lanes[i][p]) & MASK) << (64 * i)
        out.append(v)
    return out

def build_form(dirs, C, k, base_t):
    m = len(dirs)
    pairidx = [(i, j) for i in range(m) for j in range(i + 1, m)]
    pts = [base_t] + [base_t ^ dirs[i] for i in range(m)] + [base_t ^ dirs[i] ^ dirs[j] for (i, j) in pairidx]
    V = tovecs(Fk(pts, C, k))
    Ft = V[0]; Fi = V[1:1 + m]; Fij = V[1 + m:]
    M = [[0] * m for _ in range(m)]
    for idx, (i, j) in enumerate(pairidx):
        b = Ft ^ Fi[i] ^ Fi[j] ^ Fij[idx]
        M[i][j] = b; M[j][i] = b
    return m, M

NBYTES = 200  # 1600 bits
def covectors(vecs, m):
    """vecs: list length m of up-to-1600-bit ints. Return covectors (m-bit ints), one per output bit that is set."""
    arr = np.zeros((m, NBYTES), np.uint8)
    for k in range(m):
        arr[k] = np.frombuffer(int(vecs[k]).to_bytes(NBYTES, 'little'), np.uint8)
    bits = np.unpackbits(arr, axis=1, bitorder='little')          # (m, 1600)
    cols = bits.T                                                 # (1600, m)
    nz = np.where(cols.any(axis=1))[0]
    mbytes = (m + 7) // 8
    out = []
    for t in nz:
        out.append(int.from_bytes(np.packbits(cols[t], bitorder='little').tobytes()[:mbytes], 'little'))
    return out

class Ech:
    def __init__(s): s.piv = {}
    def add(s, r):
        for b in sorted(s.piv, reverse=True):
            if (r >> b) & 1: r ^= s.piv[b]
        if r:
            p = r.bit_length() - 1
            for b in list(s.piv):           # keep REDUCED row echelon: clean pivot column p in all rows
                if (s.piv[b] >> p) & 1: s.piv[b] ^= r
            s.piv[p] = r
    def rank(s): return len(s.piv)
    def nullbasis(s, m):
        pivbits = set(s.piv); out = []
        for f in range(m):
            if f in pivbits: continue
            n = 1 << f
            for pb, r in s.piv.items():
                if (r >> f) & 1: n |= 1 << pb
            out.append(n)
        return out

def radical(M, m):
    ech = Ech()
    for j in range(m):
        for c in covectors([M[i][j] for i in range(m)], m):
            ech.add(c)
    return m - ech.rank()

def max_isotropic(M, m, orderings, seed):
    rng = random.Random(seed); best = []
    def red(x, piv):
        for b in sorted(piv, reverse=True):
            if (x >> b) & 1: x ^= piv[b]
        return x
    for _ in range(orderings):
        ech = Ech(); S = []; span = {}
        while True:
            nb = ech.nullbasis(m)
            # perp(S) = span(nb). Pick a RANDOM vector of this subspace not in span(S) (dense exploration).
            x = 0
            for _try in range(60):
                cand = 0
                for n in nb:
                    if rng.getrandbits(1): cand ^= n
                if red(cand, span) != 0:
                    x = cand; break
            if x == 0:
                # fall back to any basis element outside span
                rem = [n for n in nb if red(n, span) != 0]
                if not rem: break
                x = rem[0]
            S.append(x); y = red(x, span)
            if y: span[y.bit_length() - 1] = x
            xi = [i for i in range(m) if (x >> i) & 1]
            Bx = []
            for k in range(m):
                b = 0
                for i in xi: b ^= M[i][k]
                Bx.append(b)
            for c in covectors(Bx, m):
                ech.add(c)
        if len(S) > len(best): best = S[:]
    return best

def dim_of(masks):
    piv = {}; rk = 0
    for v in masks:
        v = int(v)
        while v:
            b = v.bit_length() - 1
            if b in piv: v ^= piv[b]
            else: piv[b] = v; rk += 1; break
    return rk

if __name__ == '__main__':
    capmode = sys.argv[1]; orderings = int(sys.argv[2])
    C = cap_base(capmode); rng = random.Random(42)
    base_t = rng.getrandbits(320)
    print(json.dumps({'capmode': capmode, 'cap_lanes': [i for i in range(25) if C[i]]}), flush=True)
    t0 = time.time()
    coords = [1 << i for i in range(320)]
    m, M = build_form(coords, C, 2, base_t)
    print(f'built B2 (320 coords) in {time.time()-t0:.1f}s', flush=True)
    rad2 = radical(M, m)
    print(json.dumps({'round2_radical_dim': rad2, 'sec': round(time.time()-t0, 1)}), flush=True)
    iso2 = max_isotropic(M, m, orderings, 1)
    V = []
    for msk in iso2:
        v = 0
        for i in range(m):
            if (msk >> i) & 1: v ^= coords[i]
        V.append(v)
    d2 = dim_of([mk for mk in iso2])
    print(json.dumps({'round2_field_dim': d2, 'sec': round(time.time()-t0, 1)}), flush=True)

    d3 = 0
    if d2 >= 2:
        Vbasis = []; piv = {}
        for v in V:
            x = v
            while x:
                b = x.bit_length() - 1
                if b in piv: x ^= piv[b]
                else: piv[b] = v; Vbasis.append(v); break
        m3, M3 = build_form(Vbasis, C, 3, base_t)
        rad3 = radical(M3, m3)
        iso3 = max_isotropic(M3, m3, orderings, 2)
        d3 = dim_of(iso3)
        print(json.dumps({'round3_radical_dim': rad3, 'round3_field_dim': d3, 'round2_dim_used': len(Vbasis)}), flush=True)
    print(json.dumps({'round3_field_dim': d3, 'total_sec': round(time.time()-t0, 1)}), flush=True)
