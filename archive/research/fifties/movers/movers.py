#!/usr/bin/env python3
# Which drawn words of one counter outer step move which of the 18 constants of K and the target k.
# Exact map (traced from halfsearch.ctr_outer / check_ak.kfun) + bit-flip perturbation.
# Run: python -B movers.py [steps] [seed]       (pure computation, writes nothing)

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
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/pkg16/pkg/blake3-r2/experiments'))
import halfsearch as hs
from halfsearch import MASK, IV, X15, W13, Y11, rol, ror

NAMES = "q A C M I1 I5 P Q4 X15 N X1 X9 X13 S6 D T E c0".split()

def consts(o):
    'The 18 constants of K (CLOUD_BRIEF_BATCH_S form) read off one outer step o = hs.ctr_outer(eight).'
    return dict(q=(o["D2.b1"] + W13) & MASK, A=rol(o["X13"], 8), C=o["D2.c1"], M=o["S9"], I1=IV[1], I5=IV[5],
                P=o["C0.a1"], Q4=o["X4"], X15=X15, N=o["S10"], X1=o["X1"], X9=o["X9"], X13=o["X13"],
                S6=o["S6"], D=o["D1.d1"], T=o["S4"], E=IV[4], c0=(o["S2"] + o["S7"]) & MASK)

def K(g, c):
    'K(g) exactly as in CLOUD_BRIEF_BATCH_S.md.'
    S = g ^ rol((g + c['q']) & MASK, 16) ^ rol(c['A'], 16)
    v = (c['C'] - (c['A'] ^ ((g + c['q']) & MASK))) & MASK
    a = rol((c['M'] - S - c['I1']) & MASK, 16)
    b = ror(c['I5'] ^ ((c['M'] - S) & MASK), 12)
    S1 = rol(S, 8) ^ ((c['M'] - S - c['I1']) & MASK)
    X0 = (c['P'] - c['Q4'] - ((a - c['I1'] - c['I5']) & MASK)) & MASK
    d0 = rol(c['X15'], 8) ^ X0
    S5 = ror(b ^ c['M'], 7)
    nd = (c['N'] + d0) & MASK
    x = ror(ror(S5 ^ nd, 12) ^ ((nd + c['X15']) & MASK), 7)
    A1 = (c['X1'] + x + S1 - a - b) & MASK
    B1 = ror(x ^ ((c['X9'] + ror(c['X13'] ^ A1, 16)) & MASK), 12)
    F = (c['X1'] + x - a - b + B1 - c['S6']) & MASK
    ph = rol(c['D'], 16) ^ ((v - (rol(rol(c['T'], 7) ^ v, 12) ^ c['E'])) & MASK)
    return (g - c['c0'] + F + ph) & MASK

def H(o, c1, a):
    'Target k demanded by trial (c1, E1.a2 = a): check_ak.hfun, k = u - (ROL12(a-u-w5) ^ c1).'
    u = rol((c1 - Y11) & MASK, 16) ^ o["Y12"]
    return (u - (rol((a - u - o["w5"]) & MASK, 12) ^ c1)) & MASK

def invert(c, w6, S11):
    'From the 18 constants plus (w6, S11) rebuild the eight words; None if Y4 is not a class member.'
    D2b1 = (c['q'] - W13) & MASK; X9 = c['X9']; S4 = c['T']
    o = hs.ctr_outer([0, 0, D2b1, S11, S4, X9, w6, 0])        # gives K3.*, S3, S7, X8, D3.* for these words
    X12 = (hs.X11 - ((c['D'] + S11) & MASK)) & MASK
    C0d1 = ror(X12 ^ c['P'], 16)
    C0c1 = (o["X8"] + C0d1) & MASK
    C0b1 = ror(c['Q4'] ^ C0c1, 12)
    Y0 = (c['P'] + C0b1 + w6) & MASK
    Y12 = ror(Y0 ^ C0d1, 8)
    Y4 = ror(((Y12 + C0c1) & MASK) ^ C0b1, 7)
    return C0d1, Y4

def main(n, seed):
    rnd = random.Random(seed)
    cs = hs.CLASS_SIZE; cb = cs.bit_length() - 1
    labels = ["C0.d1", "D2.a1(g)", "D2.b1", "S11", "S4", "X9", "w6", "member"]
    width = [32] * 7 + [cb]
    move = {l: set() for l in labels + ["c1 (a fixed)", "a", "c1 (g fixed)"]}
    kmove = {l: 0 for l in move}; kmove_fwd = {l: 0 for l in move}
    bad = 0; inv_bad = 0; free_c1 = len(hs.CTR_FREE)
    for step in range(n):
        eight = [rnd.getrandbits(32) for _ in range(7)] + [rnd.getrandbits(cb)]
        o = hs.ctr_outer(eight); c = consts(o); g = eight[1]
        kf = K(g, c); bad += kf != (o["Y1"] + o["w12"]) & MASK
        j = rnd.getrandbits(free_c1); c1 = hs.ctr_c1(j); a = rnd.getrandbits(32)
        kt = H(o, c1, a)
        # rebuild from the constants: must give back C0.d1 and Y4
        C0d1, Y4 = invert(c, eight[6], eight[3]); inv_bad += (C0d1, Y4) != (eight[0], o["Y4"])
        for wi, l in enumerate(labels):
            b = rnd.randrange(width[wi])
            e2 = list(eight); e2[wi] ^= 1 << b
            o2 = hs.ctr_outer(e2); c2 = consts(o2)
            move[l] |= {x for x in NAMES if c2[x] != c[x]}
            kmove[l] += H(o2, c1, a) != kt
            kmove_fwd[l] += K(e2[1], c2) != kf
        j2 = j ^ (1 << rnd.randrange(free_c1)); c1b = hs.ctr_c1(j2)
        kmove["c1 (a fixed)"] += H(o, c1b, a) != kt
        kmove["a"] += H(o, c1, a ^ (1 << rnd.randrange(32))) != kt
        # forward: g fixed, c1 changes -> trial E1.a2 changes but K(g) does not
        r1, r2 = hs.ctr_trial(o, c1), hs.ctr_trial(o, c1b)
        if r1 and r2:
            kmove_fwd["c1 (g fixed)"] += H(o, c1b, r2[3]["E1.a2"]) != H(o, c1, r1[3]["E1.a2"])
            bad += H(o, c1, r1[3]["E1.a2"]) != kf
    print(f"steps {n} seed {seed}; K/AK* mismatches {bad}; rebuild-from-constants mismatches {inv_bad}")
    for l in move:
        print(f"  {l:14s} constants moved {sorted(move[l], key=NAMES.index)}  target-k moved {kmove[l]}/{n}"
              f"  K(g) moved {kmove_fwd[l]}/{n}")
    return 0 if bad == 0 and inv_bad == 0 else 1

if __name__ == "__main__":
    sys.exit(main(int(sys.argv[1]) if len(sys.argv) > 1 else 10000, int(sys.argv[2]) if len(sys.argv) > 2 else 1))
