"""TEST 2b: per output word, zero channel vs XOR-fold channel, length-sibling pair, one instance.
out_i = v_i ^ v_{i+8}.  For each i: P[out_i equal], P[dv_i = 0 and dv_{i+8} = 0] (zero channel),
P[dv_i = dv_{i+8} != 0] (fold channel).  Random baseline for 'equal' is 2^-w.
Usage: python t2b_words.py w log2N [seed]
"""
import sys
import numpy as np
from xtoy import Toy

w = int(sys.argv[1]); log2n = int(sys.argv[2]); seed = int(sys.argv[3]) if len(sys.argv) > 3 else 3
T = Toy(w); mask = T.mask
rng = np.random.default_rng(seed)
b1 = 55 & int(mask); b2 = b1 ^ 8
n = 1 << min(log2n, 18); nb = 1 << max(0, log2n - 18)
eq = np.zeros(8); zero = np.zeros(8); fold = np.zeros(8); N = 0
for _ in range(nb):
    M = [rng.integers(0, int(mask) + 1, n, dtype=np.uint64) for _ in range(16)]
    v1 = T.init_state(n, blen=b1, flags=11); v2 = T.init_state(n, blen=b2, flags=11)
    a1 = (v1[2] + v1[6] + M[4]) & mask; a1p = a1 ^ np.uint64(b1 ^ b2)
    Mp = list(M); Mp[4] = (a1p - v1[2] - v1[6]) & mask; Mp[5] = (M[5] + a1 - a1p) & mask
    f1 = T.rounds(M, v1); f2 = T.rounds(Mp, v2)
    for i in range(8):
        dlo = f1[i] ^ f2[i]; dhi = f1[i + 8] ^ f2[i + 8]
        e = dlo == dhi
        eq[i] += e.sum(); z = (dlo == 0) & (dhi == 0); zero[i] += z.sum(); fold[i] += (e & ~z).sum()
    N += n
lg = lambda c: f"{np.log2(c / N):7.2f}" if c else "   -inf"
print(f"# w={w} N=2^{log2n} filed instance; baseline equal = 2^-{w}")
src = {0: "E0.a^E2.c", 2: "E2.a^E0.c", 5: "E0.b^E2.d", 7: "E2.b^E0.d",
       1: "E1.a^E3.c", 3: "E3.a^E1.c", 4: "E3.b^E1.d", 6: "E1.b^E3.d"}
for i in range(8):
    print(f"out{i} = {src[i]}: log2 P[equal] {lg(eq[i])} | zero channel {lg(zero[i])} | fold channel {lg(fold[i])}")
