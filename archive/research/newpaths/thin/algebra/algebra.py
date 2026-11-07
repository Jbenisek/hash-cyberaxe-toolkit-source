#!/usr/bin/env python
"""algebra.py: does the residual R (digest words 1,3,4,6 of the 55/63 2-round BLAKE3 path, counter arrangement)
have low-degree / biased / cube-sum structure in cheap coordinates?  Toy word sizes 6, 8, 10.  Research only.

Model (transcribed from counter/toy/ctr_toy.c: cmd_mass and the ctr_step chain, and STACK.md section 1):
  E1 = G(Y1, Y6, c, Y12; w12, w5) for A (c = y11) and B (c = y11b, w5 + delta); free inner word d1 = E1.d1,
       a1 = ROL(d1,R1) ^ P, Y6 = a1 - K  (P = Y12, K = Y1 + w12, J = w5), c1 = y11 + d1.
  pi : Y10 = ROL(Y6,R4) ^ C2b1, Y14 = Y10 - C2c1, h1 = ROR(Y14 ^ e1, R1)  (c1 -> h1 a permutation per outer step)
  E3 = G(y3, Y4, Y9, Y14; 0, w8) for A, a-input y3b for B.
  R words: r1 = dE1.a ^ dE3.c, r3 = dE3.a ^ dE1.c, r4 = dE3.b ^ dE1.d, r6 = dE1.b ^ dE3.d (d = A xor B).
Free coordinates: c1 bits inside the heaviest-beta cube (beta = c1 ^ c1b; the set is a cube: fixed + free bits),
all d1 bits, Y9 bits, w8 bits.  Everything else ("fixed words") drawn per seed; survival = re-draw (seeds).
Output functions (packed bits): 4W bits of R, then indicators [r1=0],[r3=0],[r4=0],[r6=0],[R=0].
"""
import sys, time, math
import numpy as np

ROTS = {6: (3, 2, 2, 1), 8: (4, 3, 2, 1), 10: (5, 4, 3, 2)}
U = np.uint64


class Toy:
    def __init__(s, W, seed):
        s.W, s.M, s.R = W, (1 << W) - 1, ROTS[W]
        rng = np.random.default_rng(7919 * W + seed)
        r = lambda: int(rng.integers(0, 1 << W))
        s.y11 = r(); s.y11b = s.y11
        while s.y11b == s.y11: s.y11b = r()
        s.delta = 0
        while s.delta == 0: s.delta = r()
        s.P, s.K, s.J = r(), r(), r()
        s.y3 = r(); s.y3b = s.y3
        while s.y3b == s.y3: s.y3b = r()
        s.Y4, s.C2b1, s.C2c1, s.Y9, s.w8 = r(), r(), r(), r(), r()
        D = (s.y11b - s.y11) & s.M
        c = np.arange(1 << W, dtype=np.int64)
        x = c ^ ((c + D) & s.M)
        best = int(np.argmax(np.bincount(x, minlength=1 << W)))
        S = c[x == best]
        var = int(np.bitwise_or.reduce(S ^ S[0]))
        s.cube_free = [i for i in range(W) if var >> i & 1]
        assert len(S) == 1 << len(s.cube_free), "beta set is not a cube"
        s.c1base, s.beta = int(S[0]), best

    def ror(s, x, r): return ((x >> U(r)) | (x << U(s.W - r))) & U(s.M)
    def rol(s, x, r): return ((x << U(r)) | (x >> U(s.W - r))) & U(s.M)
    def add(s, *xs):
        t = xs[0]
        for v in xs[1:]: t = t + v
        return t & U(s.M)
    def sub(s, x, k): return (x + U((-k) & s.M)) & U(s.M)

    def G(s, a, b, c, d, x, y):
        R1, R2, R3, R4 = s.R
        a = s.add(a, b, x); d = s.ror(d ^ a, R1); c = s.add(c, d); b = s.ror(b ^ c, R2); d1 = d
        a = s.add(a, b, y); d = s.ror(d ^ a, R3); c = s.add(c, d); b = s.ror(b ^ c, R4)
        return a, b, c, d, d1

    def residual(s, d1, Y9, w8, parts=False):
        R1, R2, R3, R4 = s.R
        a1 = s.rol(d1, R1) ^ U(s.P)
        Y6 = s.sub(a1, s.K)
        # E1 (A and B): only c-input and w5 differ
        out = []
        for c_in, dl in ((s.y11, 0), (s.y11b, s.delta)):
            c1 = s.add(d1, U(c_in)); b1 = s.ror(Y6 ^ c1, R2)
            a2 = s.add(a1, b1, U((s.J + dl) & s.M)); d2 = s.ror(d1 ^ a2, R3); c2 = s.add(c1, d2); b2 = s.ror(b1 ^ c2, R4)
            out.append((a2, b2, c2, d2))
        (a2, b2, c2, d2), (a2b, b2b, c2b, d2b) = out
        # pi and E3 (A and B): only the a-input differs
        Y14 = s.sub(s.rol(Y6, R4) ^ U(s.C2b1), s.C2c1)
        o3 = []
        for y3 in (s.y3, s.y3b):
            e1 = U((y3 + s.Y4) & s.M); h1 = s.ror(Y14 ^ e1, R1); g1 = s.add(Y9, h1); f1 = s.ror(U(s.Y4) ^ g1, R2)
            e2 = s.add(e1, f1, w8); h2 = s.ror(h1 ^ e2, R3); g2 = s.add(g1, h2); f2 = s.ror(f1 ^ g2, R4)
            o3.append((e2, f2, g2, h2))
        (e2, f2, g2, h2), (e2b, f2b, g2b, h2b) = o3
        r1 = (a2 ^ a2b) ^ (g2 ^ g2b); r3 = (e2 ^ e2b) ^ (c2 ^ c2b)
        r4 = (f2 ^ f2b) ^ (d2 ^ d2b); r6 = (b2 ^ b2b) ^ (h2 ^ h2b)
        if parts: return r1, r3, r4, r6, Y6, Y14
        return r1, r3, r4, r6

    def selfcheck(s, n=2000):
        rng = np.random.default_rng(5)
        d1 = rng.integers(0, 1 << s.W, n).astype(U); Y9 = rng.integers(0, 1 << s.W, n).astype(U)
        w8 = rng.integers(0, 1 << s.W, n).astype(U); Y1 = rng.integers(0, 1 << s.W, n).astype(U)
        r1, r3, r4, r6, Y6, Y14 = s.residual(d1, Y9, w8, parts=True)
        w12 = (U(s.K) + U(1 << s.W) - Y1) & U(s.M)
        A = s.G(Y1, Y6, U(s.y11), U(s.P), w12, U(s.J)); B = s.G(Y1, Y6, U(s.y11b), U(s.P), w12, U((s.J + s.delta) & s.M))
        C = s.G(U(s.y3), U(s.Y4), Y9, Y14, U(0), w8); Dd = s.G(U(s.y3b), U(s.Y4), Y9, Y14, U(0), w8)
        ok = np.all(A[4] == d1) and np.all(B[4] == d1)
        ok &= np.all(r1 == (A[0] ^ B[0] ^ C[2] ^ Dd[2])) and np.all(r3 == (C[0] ^ Dd[0] ^ A[2] ^ B[2]))
        ok &= np.all(r4 == (C[1] ^ Dd[1] ^ A[3] ^ B[3])) and np.all(r6 == (A[1] ^ B[1] ^ C[3] ^ Dd[3]))
        return bool(ok)

    def table(s, V):
        """truth table over the 2^n grid of the variable list V = [(word, bit)]; packed uint64"""
        n = len(V); W = s.W
        idx = np.arange(1 << n, dtype=U)
        base = {'c1': s.c1base, 'd1': (s.c1base - s.y11) & s.M, 'Y9': s.Y9, 'w8': s.w8}
        arr = {k: np.full(1 << n, v, dtype=U) for k, v in base.items()}
        for j, (w, i) in enumerate(V):
            arr[w] = (arr[w] & U(s.M ^ (1 << i))) | (((idx >> U(j)) & U(1)) << U(i))
        if any(w == 'c1' for w, _ in V): d1 = s.sub(arr['c1'], s.y11)
        else: d1 = arr['d1']
        r1, r3, r4, r6 = s.residual(d1, arr['Y9'], arr['w8'])
        T = r1 | (r3 << U(W)) | (r4 << U(2 * W)) | (r6 << U(3 * W))
        z = [(r == 0) for r in (r1, r3, r4, r6)]
        for k, zz in enumerate(z): T |= zz.astype(U) << U(4 * W + k)
        T |= (z[0] & z[2]).astype(U) << U(4 * W + 4)      # [r1=0 and r4=0]
        T |= (z[1] & z[3]).astype(U) << U(4 * W + 5)      # [r3=0 and r6=0]
        T |= (z[0] & z[1] & z[2] & z[3]).astype(U) << U(4 * W + 6)
        return T


def hull_codim(T, n, b):
    """codimension of the affine hull of the support of output bit b (GF(2)); returns (support size, codim, equations)"""
    pts = np.nonzero((T >> U(b)) & U(1))[0]
    if len(pts) == 0: return 0, None, []
    x0 = int(pts[0]); basis = {}
    for p in pts[1:]:
        v = int(p) ^ x0
        while v:
            h = v.bit_length() - 1
            if h in basis: v ^= basis[h]
            else: basis[h] = v; break
        if len(basis) == n: break
    rank = len(basis)
    # equations: orthogonal complement of the span (as variable masks)
    vecs = list(basis.values()); eqs = []
    if rank < n:
        # reduce basis to RREF, complement by free columns
        piv = {}
        for v in sorted(vecs, reverse=True):
            for h, w in piv.items():
                if v >> h & 1: v ^= w
            if v:
                h = v.bit_length() - 1
                for k in list(piv):
                    if piv[k] >> h & 1: piv[k] ^= v
                piv[h] = v
        free = [j for j in range(n) if j not in piv]
        for f in free:
            e = 1 << f
            for h, w in piv.items():
                if w >> f & 1: e |= 1 << h
            const = bin(e & x0).count('1') & 1
            eqs.append((e, const))
    return len(pts), n - rank, eqs


def mobius(T, n):
    a = T.copy()
    for i in range(n):
        v = a.reshape(-1, 2, 1 << i)
        v[:, 1, :] ^= v[:, 0, :]
    return a


def degrees(anf, n, nb):
    pc = np.bitwise_count(np.arange(1 << n, dtype=U))
    deg = [-1] * nb
    for d in range(n + 1):
        sel = anf[pc == d]
        if len(sel) == 0: continue
        acc = int(np.bitwise_or.reduce(sel))
        for b in range(nb):
            if acc >> b & 1: deg[b] = d
    return deg


def walsh_stats(T, n, nb, W):
    """per bit: imbalance |corr(0)|, max |corr(u)| over u != 0 and its mask; indicators: count and best one-hyperplane gain"""
    res = []
    for b in range(nb):
        f = 1.0 - 2.0 * ((T >> U(b)) & U(1)).astype(np.float64)
        for i in range(n):
            v = f.reshape(-1, 2, 1 << i)
            x = v[:, 0, :].copy(); y = v[:, 1, :].copy()
            v[:, 0, :] = x + y; v[:, 1, :] = x - y
        corr = f / (1 << n)
        u = int(np.argmax(np.abs(corr[1:]))) + 1
        cnt = int(round((1 << n) * (1 - corr[0]) / 2))
        gain = None
        if b >= 4 * W and cnt >= 16:
            gain = 1.0 + float(np.max(-f[1:] / 2.0)) / cnt
        res.append((abs(corr[0]), abs(corr[u]), u, cnt, gain))
    return res


def cube_stats(anf, n, nb, kmax, ncube, rng):
    """per cube dimension k: counts over (cube, bit) of superpoly zero / const 1 / affine non-const / degree >= 2,
    counting only pairs where the bit depends on every cube variable (else the cube sum is trivially 0)"""
    idx = np.arange(1 << n, dtype=U)
    pc = np.bitwise_count(idx)
    dep = [int(np.bitwise_or.reduce(anf[(idx >> U(j)) & U(1) == U(1)])) for j in range(n)]
    out = {}
    for k in range(2, kmax + 1):
        if k >= n: break
        tot = math.comb(n, k)
        if tot <= ncube:
            from itertools import combinations
            cubes = list(combinations(range(n), k))
        else:
            seen = set(); cubes = []
            while len(cubes) < ncube:
                c = tuple(sorted(rng.choice(n, k, replace=False).tolist()))
                if c not in seen: seen.add(c); cubes.append(c)
        cnt = np.zeros((nb, 4), dtype=np.int64)
        for c in cubes:
            cm = sum(1 << j for j in c)
            m = (idx & U(cm)) == U(cm)
            sel = anf[m]; ps = pc[m]
            one = int(anf[cm])
            nonc = int(np.bitwise_or.reduce(sel[ps > k])) if np.any(ps > k) else 0
            hi = int(np.bitwise_or.reduce(sel[ps > k + 1])) if np.any(ps > k + 1) else 0
            for b in range(nb):
                if not all(dep[j] >> b & 1 for j in c): continue
                if hi >> b & 1: cnt[b, 3] += 1
                elif nonc >> b & 1: cnt[b, 2] += 1
                elif one >> b & 1: cnt[b, 1] += 1
                else: cnt[b, 0] += 1
        out[k] = (len(cubes), cnt)
    return out


WORDS = ['r1', 'r3', 'r4', 'r6']
IND = ['[r1=0]', '[r3=0]', '[r4=0]', '[r6=0]', '[r1=r4=0]', '[r3=r6=0]', '[R=0]']


def varsets(t):
    W = t.W
    cube = [('c1', i) for i in t.cube_free]
    d1 = [('d1', i) for i in range(W)]; Y9 = [('Y9', i) for i in range(W)]; w8 = [('w8', i) for i in range(W)]
    sets = {'c1cube': cube, 'd1': d1, 'Y9': Y9, 'w8': w8}
    if W <= 8:
        sets['c1cube+Y9+w8'] = cube + Y9 + w8
        sets['d1+Y9'] = d1 + Y9; sets['d1+w8'] = d1 + w8; sets['Y9+w8'] = Y9 + w8
    if W == 6: sets['d1+Y9+w8'] = d1 + Y9 + w8
    if W == 10: sets['Y9+w8'] = Y9 + w8
    return sets


def main():
    Ws = [int(a) for a in sys.argv[1].split(',')] if len(sys.argv) > 1 else [6, 8]
    seeds = range(1, int(sys.argv[2]) + 1) if len(sys.argv) > 2 else range(1, 7)
    ncube = int(sys.argv[3]) if len(sys.argv) > 3 else 120
    rng = np.random.default_rng(99)
    t0 = time.time()
    for W in Ws:
        nb = 4 * W + len(IND)
        for seed in seeds:
            t = Toy(W, seed)
            print(f"SEED W {W} seed {seed} selfcheck {t.selfcheck()} y11 {t.y11:x} y11b {t.y11b:x} delta {t.delta:x} P {t.P:x} K {t.K:x} "
                  f"J {t.J:x} y3 {t.y3:x} y3b {t.y3b:x} Y4 {t.Y4:x} C2b1 {t.C2b1:x} C2c1 {t.C2c1:x} Y9 {t.Y9:x} w8 {t.w8:x} "
                  f"beta {t.beta:x} cube_free {t.cube_free} c1base {t.c1base:x}", flush=True)
            for name, V in varsets(t).items():
                n = len(V)
                if n < 2: continue
                T = t.table(V)
                anf = mobius(T, n)
                deg = degrees(anf, n, nb)
                pz = [int(np.count_nonzero((T >> U(4 * W + k)) & U(1))) for k in range(len(IND))]
                line = f"DEG W {W} seed {seed} set {name} n {n}"
                for j, w in enumerate(WORDS): line += f" {w} " + ",".join(str(d) for d in deg[j * W:(j + 1) * W])
                line += " ind " + ",".join(str(d) for d in deg[4 * W:])
                line += " zeros " + ",".join(str(z) for z in pz)
                print(line, flush=True)
                for q, nm in enumerate(IND):
                    sz, cd, eqs = hull_codim(T, n, 4 * W + q)
                    if sz == 0: continue
                    es = []
                    for e, c in eqs[:8]:
                        es.append("+".join(f"{V[x][0]}.{V[x][1]}" for x in range(n) if e >> x & 1) + f"={c}")
                    print(f"HULL W {W} seed {seed} set {name} n {n} ind {nm} support {sz} codim {cd} eqs " + (" ".join(es) if es else "-"), flush=True)
                if n <= 18:
                    ws = walsh_stats(T, n, nb, W)
                    line = f"WAL W {W} seed {seed} set {name} n {n}"
                    for j, w in enumerate(WORDS):
                        line += f" {w} imb " + ",".join(f"{x[0]:.3f}" for x in ws[j * W:(j + 1) * W])
                        line += " lin " + ",".join(f"{x[1]:.3f}" for x in ws[j * W:(j + 1) * W])
                    line += " indgain " + ",".join("-" if x[4] is None else f"{x[4]:.2f}" for x in ws[4 * W:])
                    print(line, flush=True)
                    fr = np.random.default_rng(seed).integers(0, 2, (3, 1 << n)).astype(U)
                    base = max(walsh_stats(fr[i], n, 1, 99)[0][1] for i in range(3))
                    print(f"WALBASE W {W} n {n} random_max_lin {base:.3f}", flush=True)
                if n >= 4:
                    cs = cube_stats(anf, n, nb, min(6, n - 1), ncube, rng)
                    for k, (nc, cnt) in cs.items():
                        line = f"CUBE W {W} seed {seed} set {name} n {n} k {k} ncubes {nc}"
                        for j, w in enumerate(WORDS + ['ind']):
                            sl = cnt[j * W:(j + 1) * W] if j < 4 else cnt[4 * W:]
                            s = sl.sum(axis=0); tot = max(1, int(s.sum()))
                            line += f" {w} pairs {int(s.sum())} zero {s[0]/tot:.3f} one {s[1]/tot:.3f} aff {s[2]/tot:.3f} hi {s[3]/tot:.3f}"
                        print(line, flush=True)
            print(f"TIME {time.time() - t0:.1f}", flush=True)
    print("END")


if __name__ == '__main__':
    main()
