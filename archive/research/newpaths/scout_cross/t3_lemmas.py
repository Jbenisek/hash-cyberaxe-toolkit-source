"""Checks of Lemma 1 (dY3 != 0 for the 55/63 sibling pair) and the premises/conclusion of Lemma 2
(B-half fold => dE3.b1 = dE3.c2 ^ rotr(dE3.c2, R2-R3)).  Usage: python -B t3_lemmas.py w log2N [alt]"""
import sys
import numpy as np
from xtoy import Toy, PERM

w = int(sys.argv[1]); lg = int(sys.argv[2]); alt = len(sys.argv) > 3 and sys.argv[3] == "alt"
T = Toy(w, alt=alt); mask = T.mask; R0, R1, R2, R3 = T.rots
rng = np.random.default_rng(5)
b1 = 55 & int(mask); b2 = b1 ^ 8
n = 1 << min(lg, 18); nb = 1 << max(0, lg - 18)
mp = [PERM[i] for i in range(16)]          # round-1 schedule: m'[i] = m[PERM[i]]
tot = dict(N=0, dY3zero=0, E1d1_nonzero=0, E1d2_rule_fail=0, Beq=0, lemma2_fail_on_Beq=0)


def g_half(a, b, c, d, x):
    a1 = (a + b + x) & mask
    d1 = T.rotr(d ^ a1, R0)
    c1 = (c + d1) & mask
    b1_ = T.rotr(b ^ c1, R1)
    return a1, b1_, c1, d1


for _ in range(nb):
    M = [rng.integers(0, int(mask) + 1, n, dtype=np.uint64) for _ in range(16)]
    v1 = T.init_state(n, blen=b1, flags=11); v2 = T.init_state(n, blen=b2, flags=11)
    a1 = (v1[2] + v1[6] + M[4]) & mask; a1p = a1 ^ np.uint64(b1 ^ b2)
    Mp = list(M); Mp[4] = (a1p - v1[2] - v1[6]) & mask; Mp[5] = (M[5] + a1 - a1p) & mask
    f1, X1, Y1 = T.rounds(M, v1, keep=True)
    f2, X2, Y2 = T.rounds(Mp, v2, keep=True)
    tot['N'] += n
    tot['dY3zero'] += int((Y1[3] == Y2[3]).sum())
    # E1 = G(Y1,Y6,Y11,Y12; m'[10], m'[11]) = (m12, m5); E3 = G(Y3,Y4,Y9,Y14; m'[14], m'[15]) = (m15, m8)
    e1a = g_half(Y1[1], Y1[6], Y1[11], Y1[12], M[mp[10]]); e1b = g_half(Y2[1], Y2[6], Y2[11], Y2[12], Mp[mp[10]])
    tot['E1d1_nonzero'] += int((e1a[3] != e1b[3]).sum())
    dE1a2 = f1[1] ^ f2[1]; dE1d2 = f1[12] ^ f2[12]
    tot['E1d2_rule_fail'] += int((dE1d2 != T.rotr(dE1a2, R2)).sum())
    eq = [(f1[i] ^ f1[i + 8]) == (f2[i] ^ f2[i + 8]) for i in range(8)]
    B = eq[1] & eq[3] & eq[4] & eq[6]
    tot['Beq'] += int(B.sum())
    if B.any():
        e3a = g_half(Y1[3], Y1[4], Y1[9], Y1[14], M[mp[14]]); e3b = g_half(Y2[3], Y2[4], Y2[9], Y2[14], Mp[mp[14]])
        db1 = e3a[1] ^ e3b[1]; dc2 = f1[9] ^ f2[9]
        r = (R2 - R3) % w
        rule = dc2 ^ T.rotr(dc2, r)
        tot['lemma2_fail_on_Beq'] += int(((db1 != rule) & B).sum())
print(f"w={w} rots={T.rots} N=2^{lg}: {tot}")
