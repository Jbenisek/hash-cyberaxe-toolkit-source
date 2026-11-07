#!/usr/bin/env python3
# Full 2^32 scans (numpy, one process) for MOVERS.md.
# Part 1: outer tuples sharing one constant tuple. With the 18 constants fixed, S7 and S3 are fixed; for each w6,
#   S11 = ROL7(S7) ^ K3.b1(w6) and S3 = f(w6). Count all w6 with f(w6) = S3, rebuild each tuple, test Y4 in class.
# Part 2: forward m = |image of K| for one constant tuple: preimage counts n of K(g0) for sampled g0; |Im|/2^32 = E[1/n].
# Run: python -B scan.py [seed]

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

import random, sys
import numpy as np
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/pkg16/pkg/blake3-r2/experiments'))
import halfsearch as hs
from halfsearch import MASK, IV, rol, ror
from movers import consts, invert, K

U = np.uint32
def nrol(x, r): return (x << U(r)) | (x >> U(32 - r))
def nror(x, r): return (x >> U(r)) | (x << U(32 - r))
CH = 1 << 24

def part1(rnd, steps):
    members = {hs.class_member(i) for i in range(hs.CLASS_SIZE)}
    out = []
    for _ in range(steps):
        eight = [rnd.getrandbits(32) for _ in range(7)] + [rnd.getrandbits(hs.CLASS_SIZE.bit_length() - 1)]
        o = hs.ctr_outer(eight); c = consts(o)
        S7, S3 = U(o["S7"]), U(o["S3"])
        sols = []
        for base in range(0, 1 << 32, CH):
            w6 = np.arange(base, base + CH, dtype=np.uint64).astype(U)
            a = w6 + U((IV[3] + IV[7]) & MASK); d = nror(a ^ U(hs.CTR_FLAGS), 16); cc = U(IV[3]) + d
            b = nror(U(IV[7]) ^ cc, 12); s11 = nrol(S7, 7) ^ b; s3 = nrol(s11 - cc, 8) ^ d
            for w in w6[s3 == S3]:
                w = int(w); s = int(nrol(S7, 7)) ^ int(b[w - base])
                sols.append((w, s))
        valid = 0
        for w, s in sols:
            C0d1, Y4 = invert(c, w, s)
            if Y4 in members:
                e = [C0d1, eight[1], eight[2], s, eight[4], eight[5], w, 0]
                valid += 1
        out.append((len(sols), valid))
        print("part1 w6-solutions, of which Y4 in class:", len(sols), valid, flush=True)
    return out

def Kvec(g, c):
    c = {k: U(v) for k, v in c.items()}
    gq = g + c['q']
    S = g ^ nrol(gq, 16) ^ nrol(c['A'], 16)
    v = c['C'] - (c['A'] ^ gq)
    ms = c['M'] - S
    a = nrol(ms - c['I1'], 16); b = nror(c['I5'] ^ ms, 12)
    S1 = nrol(S, 8) ^ (ms - c['I1'])
    X0 = c['P'] - c['Q4'] - (a - c['I1'] - c['I5'])
    d0 = nrol(c['X15'], 8) ^ X0; S5 = nror(b ^ c['M'], 7); nd = c['N'] + d0
    x = nror(nror(S5 ^ nd, 12) ^ (nd + c['X15']), 7)
    A1 = c['X1'] + x + S1 - a - b
    B1 = nror(x ^ (c['X9'] + nror(c['X13'] ^ A1, 16)), 12)
    F = c['X1'] + x - a - b + B1 - c['S6']
    ph = nrol(c['D'], 16) ^ (v - (nrol(nrol(c['T'], 7) ^ v, 12) ^ c['E']))
    return g - c['c0'] + F + ph

def part2(rnd, tuples, ntar):
    res = []
    for _ in range(tuples):
        eight = [rnd.getrandbits(32) for _ in range(7)] + [0]
        c = consts(hs.ctr_outer(eight))
        g0 = [rnd.getrandbits(32) for _ in range(ntar)]
        tk = np.array(sorted({K(g, c) for g in g0}), dtype=U)
        assert all(int(Kvec(np.array([g], dtype=U), c)[0]) == K(g, c) for g in g0[:8])
        cnt = np.zeros(len(tk), dtype=np.int64)
        with np.errstate(over="ignore"):
            for base in range(0, 1 << 32, CH):
                kv = Kvec(np.arange(base, base + CH, dtype=np.uint64).astype(U), c)
                i = np.searchsorted(tk, kv); i[i == len(tk)] = 0
                hit = tk[i] == kv
                np.add.at(cnt, i[hit], 1)
        n = [int(cnt[np.searchsorted(tk, U(K(g, c)))]) for g in g0]
        ef = sum(1 / x for x in n) / len(n)
        res.append(ef)
        print("part2 preimage counts histogram:", {k: n.count(k) for k in sorted(set(n))},
              " E[1/n] = image fraction ~", round(ef, 4), flush=True)
    return res

if __name__ == "__main__":
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    rnd = random.Random(seed)
    mode = sys.argv[2] if len(sys.argv) > 2 else "both"
    with np.errstate(over="ignore"):
        if mode in ("both", "1"):
            part1(rnd, 8)
        if mode in ("both", "2"):
            part2(rnd, 2, 400)
