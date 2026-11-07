import sys, time
from attack import *
j = int(sys.argv[1]); r = int(sys.argv[2])
D = 5 ** (6 + r)
LG = (D + 1 - 1).bit_length()          # N = 2^LG > D
N = 1 << LG
# primitive 2^32-th root of unity
g = 2
while True:
    w32 = pow(g, (p - 1) >> 32, p)
    if pow(w32, 1 << 31, p) != 1: break
    g += 1
w = pow(w32, 1 << (32 - LG), p)
assert pow(w, N // 2, p) == p - 1
L = Line(j)
t0 = time.time()
pts = [pow(w, i, p) for i in range(N)]
vals = [L.F(x, r) for x in pts]
t1 = time.time()
def ntt(a, root):
    n = len(a)
    # iterative bit-reversal
    j2 = 0
    for i in range(1, n):
        bit = n >> 1
        while j2 & bit:
            j2 ^= bit; bit >>= 1
        j2 ^= bit
        if i < j2: a[i], a[j2] = a[j2], a[i]
    ln = 2
    while ln <= n:
        wl = pow(root, n // ln, p)
        half = ln // 2
        tw = [1] * half
        for k in range(1, half): tw[k] = tw[k-1] * wl % p
        for s in range(0, n, ln):
            for k in range(half):
                u = a[s+k]; v = a[s+k+half] * tw[k] % p
                a[s+k] = (u + v) % p; a[s+k+half] = (u - v) % p
        ln <<= 1
    return a
coef = ntt(vals[:], pow(w, -1, p))
ninv = pow(N, -1, p)
coef = [c * ninv % p for c in coef]
t2 = time.time()
deg = max(i for i, c in enumerate(coef) if c)
# independent check: Horner at 3 fresh random points against direct evaluation
rnd_ok = True
for _ in range(3):
    x = random.randrange(p)
    h = 0
    for c in reversed(coef[:deg+1]): h = (h * x + c) % p
    rnd_ok &= (h == L.F(x, r))
# also check the true hash for two (nk,rho) from the line
tau = random.randrange(1, p); nk, rho = L.inputs(tau)
true_ok = digest(nk, rho, r) == sum(c * pow(pow(tau, 5, p), i, p) for i, c in enumerate(coef[:deg+1]) if c) % p if deg < 2000 else None
nz_above = sum(1 for c in coef[D+1:] if c)
print(f'j={j} r={r} expected deg 5^{6+r}={D}  N=2^{LG}  found deg={deg}  coeffs above expected: {nz_above}  fresh-point Horner check: {rnd_ok}  lc={hex(coef[deg])[:14]}..  zero coefs below deg: {sum(1 for c in coef[:deg+1] if c==0)}  evalT={t1-t0:.0f}s nttT={t2-t1:.0f}s', flush=True)
