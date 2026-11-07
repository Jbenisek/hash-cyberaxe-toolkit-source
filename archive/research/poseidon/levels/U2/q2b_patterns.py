"""Q2 follow-up: are the factor patterns of the top forms F_{1,j} (degree 5) and F_{2,j} (degree 25) typical for random polynomials, or structural?
   Uses primes q = 2 mod 5 near 2^31 (same residue class as Pallas), random Cauchy MDS; compares with random polynomials of the same degree."""
import sys, random, time
import u2lib as U
def is_prime(n):
    if n < 2: return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % p == 0: return n == p
    d = n - 1; s = 0
    while d % 2 == 0: d //= 2; s += 1
    for a in (2, 3, 5, 7, 11, 13, 17):
        x = pow(a, d, n)
        if x in (1, n - 1): continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1: break
        else: return False
    return True
rng = random.Random(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
nmat = int(sys.argv[2]) if len(sys.argv) > 2 else 300
def find_prime():
    while True:
        n = rng.randrange(2**30, 2**31)
        n = n - n % 5 + 2
        if is_prime(n): return n
def cauchy(q):
    while True:
        xs = [rng.randrange(q) for _ in range(3)]; ys = [rng.randrange(q) for _ in range(3)]
        if len(set(xs)) == 3 and len(set(ys)) == 3 and all((x + y) % q for x in xs for y in ys):
            return [[pow(x + y, q - 2, q) for y in ys] for x in xs]
def forms(M, q, kmax):
    P = q
    F = [[[M[j][1], M[j][0]] for j in range(3)]]
    for k in range(1, kmax + 1):
        prev = [U.p5(f) for f in F[-1]]
        new = []
        for j in range(3):
            acc = []
            for i in range(3): acc = U.padd(acc, [M[j][i] * c % P for c in prev[i]])
            new.append(acc)
        F.append(new)
    return F
def pattern(f, kmax=None):
    d = U.pgcd(f, U.pderiv(f))
    sf = len(d) == 1
    return sf, U.ddf(f, kmax)
from collections import Counter
t0 = time.time()
stat = {1: Counter(), 2: Counter()}
cnt = {1: Counter(), 2: Counter()}
rnd = {1: Counter(), 2: Counter()}
tot_lane = 0
for n in range(nmat):
    q = find_prime(); U.P = q
    M = cauchy(q)
    F = forms(M, q, 2)
    for j in range(3):
        sf, dd = pattern(F[1][j])
        cnt[1][tuple(sorted(dd.items()))] += 1
        # random quintic
        g = [rng.randrange(q) for _ in range(6)]
        if g[-1]:
            sfr, ddr = pattern(g); rnd[1][tuple(sorted(ddr.items()))] += 1
        sf2, dd2 = pattern(F[2][j], kmax=5)
        cnt[2][('deg5' if 5 in dd2 else 'no5', 'root' if 1 in dd2 else 'noroot')] += 1
        g = [rng.randrange(q) for _ in range(26)]
        sfr2, ddr2 = pattern(g, kmax=5)
        rnd[2][('deg5' if 5 in ddr2 else 'no5', 'root' if 1 in ddr2 else 'noroot')] += 1
    tot_lane += 3
print(f"{nmat} random (prime q = 2 mod 5, random Cauchy M) instances, {tot_lane} lanes, t={time.time()-t0:.1f}s")
print("R1 form (quintic) factor patterns (factor degree, total degree): Cauchy-MDS lanes vs random quintics")
for k in sorted(set(cnt[1]) | set(rnd[1]), key=lambda x: -cnt[1][x]):
    print(f"  {str(k):40s} MDS {cnt[1][k]/tot_lane:.3f}   random {rnd[1][k]/sum(rnd[1].values()):.3f}")
print("R2 form (degree 25): has an irreducible factor of degree 5 / has a root, Cauchy-MDS vs random degree-25 polynomials")
for k in sorted(set(cnt[2]) | set(rnd[2])):
    print(f"  {str(k):30s} MDS {cnt[2][k]/tot_lane:.3f}   random {rnd[2][k]/sum(rnd[2].values()):.3f}")
