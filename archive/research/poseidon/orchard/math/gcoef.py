# check: g(S) = sum_m f_{2m+1} S^m (Taylor coeffs of F at c) is recovered from 2*N/2 permutation-like evaluations + one inverse NTT of size N/2
import time
from fpoly import *
r = 0; j = 0
L = Line(j); F = build_F(L, r); D = F.degree(); m = (D - 1) // 2
c = random.randrange(p)
co = F.compose(R([c, 1])).coeffs()
g_ref = [int(co[k]) for k in range(1, len(co), 2)]
LG = (m + 1 - 1).bit_length()        # 2^LG >= m+1
H = 1 << LG                           # N/2
g = 2
while True:
    w32 = pow(g, (p - 1) >> 32, p)
    if pow(w32, 1 << 31, p) != 1: break
    g += 1
wN = pow(w32, 1 << (32 - (LG + 1)), p)      # order 2^(LG+1)
t = time.time()
vals = []
for i in range(H):
    s = pow(wN, i, p)
    hv = (L.F((c + s) % p, r) - L.F((c - s) % p, r)) % p
    vals.append(hv * pow(2 * s, -1, p) % p)       # g(s^2)
w = pow(wN, 2, p)    # order H
def ntt(a, root):
    n = len(a); j2 = 0
    for i in range(1, n):
        bit = n >> 1
        while j2 & bit: j2 ^= bit; bit >>= 1
        j2 ^= bit
        if i < j2: a[i], a[j2] = a[j2], a[i]
    ln = 2
    while ln <= n:
        wl = pow(root, n // ln, p); half = ln // 2
        tw = [1] * half
        for k in range(1, half): tw[k] = tw[k-1] * wl % p
        for s0 in range(0, n, ln):
            for k in range(half):
                u = a[s0+k]; v = a[s0+k+half] * tw[k] % p
                a[s0+k] = (u + v) % p; a[s0+k+half] = (u - v) % p
        ln <<= 1
    return a
co2 = ntt(vals, pow(w, -1, p)); hi = pow(H, -1, p)
co2 = [x * hi % p for x in co2]
print('m =', m, 'H =', H, 'evaluations of F:', 2 * H, 'match with Taylor g:', co2[:m + 1] == g_ref, 'high coefs zero:', all(x == 0 for x in co2[m + 1:]), f'{time.time()-t:.1f}s')
