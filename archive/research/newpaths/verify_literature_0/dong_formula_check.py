# Check of Dong et al. CRYPTO 2021 eq. (9)/(10) (2021_427.txt lines 1321-1443).
# All quantities in BITS here (cells of w bits -> multiply by w). n = h*w output bits,
# T = t*w target bits, Dp/Dm = DoF+/DoF- bits, M = m*w filter bits (M <= T).
# Paper (eq 9, table-building terms dropped):  cost = n/2 - min(Dp-T/2, Dm-T/2, M-T/2, T/2)
# Derivation (lines 1335-1347): episodes E = 2^((n-T)/2 - (Dp+Dm-T)), per-episode
# cost 2^Dp + 2^Dm + 2^(Dp+Dm-M) + 2^(Dp+Dm-T).  Requires E >= 1, i.e. Dp+Dm <= (n+T)/2.
# Constrained optimum: pick a<=Dp, b<=Dm with a+b <= (n+T)/2, e = (n+T)/2 - a - b >= 0:
#   cost = e + max(a, b, a+b-M, a+b-T).
import itertools

def paper(n, T, Dp, Dm, M):
    return n/2 - min(Dp - T/2, Dm - T/2, M - T/2, T/2)

def constrained(n, T, Dp, Dm, M, step=1.0):
    best = None
    a = 0.0
    while a <= Dp + 1e-9:
        b = 0.0
        while b <= Dm + 1e-9:
            if a + b <= (n + T)/2 + 1e-9:
                e = (n + T)/2 - a - b
                c = e + max(a, b, a + b - M, a + b - T)
                if best is None or c < best[0]:
                    best = (c, a, b, e)
            b += step
        a += step
    return best

n = 256
print("n=256 bits (h=8 words), T=128 bits (t=4 words); all in bits")
for Dp, Dm, M in [(128,128,128),(96,96,128),(96,96,96),(160,160,128),(256,256,128),(64,64,64)]:
    p = paper(n, 128, Dp, Dm, M)
    c = constrained(n, 128, Dp, Dm, M)
    E = (n-128)/2 - (Dp+Dm-128)
    print(f"Dp={Dp} Dm={Dm} M={M}: paper eq9 -> {p:.1f}; log2(episodes) per paper = {E:.0f};"
          f" constrained best -> {c[0]:.1f} (a={c[1]:.0f}, b={c[2]:.0f}, e={c[3]:.0f})")

print()
print("Best over T (Dp=Dm=256 unlimited, M=T): constrained optimum per T, step 1 bit")
rows = []
for T in range(0, 257, 1):
    c = constrained(n, T, 256, 256, T, step=1.0) if T % 16 == 0 or 80 <= T <= 90 else None
    if c:
        rows.append((T, c[0], paper(n, T, 256, 256, T)))
for T, c, p in rows:
    print(f"T={T:3d}: constrained {c:6.2f}   paper-formula {p:6.2f}")
print("closed form: max((n+T)/4, (n-T)/2) minimised at T=n/3 =", n/3, "-> cost", n/3)
