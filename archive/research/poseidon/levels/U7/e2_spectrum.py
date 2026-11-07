# E2/E3: differential spectrum of x^5. Real field by sampling (independent root count via gcd(x^p-x, f)), toys exhaustive, closed form via quadratic in z=y^2.
import random, sys
from common import *
from fractions import Fraction
from math import gcd
rnd = random.Random(20261012)

# --- polynomial helpers over F_q (lists low->high), degree <= 4 inputs
def pmod(a, f, q):
    a = a[:]; df = len(f)-1; inv_lead = inv(f[-1], q)
    while len(a)-1 >= df and a:
        c = a[-1]*inv_lead % q
        if c:
            sh = len(a)-1-df
            for i in range(df+1): a[sh+i] = (a[sh+i]-c*f[i]) % q
        a.pop()
    while a and a[-1] == 0: a.pop()
    return a
def pmul(a, b, q):
    if not a or not b: return []
    r = [0]*(len(a)+len(b)-1)
    for i, x in enumerate(a):
        for j, y in enumerate(b): r[i+j] = (r[i+j]+x*y) % q
    return r
def ppowmod_x(e, f, q):
    res = [1]; base = [0, 1]
    base = pmod(base, f, q)
    while e:
        if e & 1: res = pmod(pmul(res, base, q), f, q)
        base = pmod(pmul(base, base, q), f, q); e >>= 1
    return res
def psub(a, b, q):
    n = max(len(a), len(b)); r = [((a[i] if i < len(a) else 0)-(b[i] if i < len(b) else 0)) % q for i in range(n)]
    while r and r[-1] == 0: r.pop()
    return r
def pgcd(a, b, q):
    while b: a, b = b, pmod(a, b, q)
    return a
def nroots_quartic(a, b, q):
    """number of DISTINCT roots x in F_q of (x+a)^5 - x^5 - b"""
    f = [(pow(a, 5, q)-b) % q, 5*pow(a, 4, q) % q, 10*pow(a, 3, q) % q, 10*a*a % q, 5*a % q]
    f = [c % q for c in f]
    X = ppowmod_x(q, f, q)               # x^q mod f
    g = pgcd(f, psub(X, [0, 1], q), q)
    return len(g)-1 if g else len(f)-1

def predicted(a, b, q):
    """closed form: h=a/2, t=(b+8h^5)/(10 h^5) = u^2 ; N = (1+chi(u-1)) + (1+chi(-u-1)) (u != 0), N = 1+chi(-1) (u = 0)"""
    h = a*inv(2, q) % q
    t = (b+8*pow(h, 5, q))*inv(10*pow(h, 5, q), q) % q
    if t == 0: return 1+leg(-1, q) if leg(-1, q) == 1 else 0
    if leg(t, q) == -1: return 0
    u = sqrt_mod(t, q)
    return (1+leg(u-1, q))+(1+leg(-u-1, q))
def predicted_gen(a, b, q):
    # robust version also valid when q = 3 mod 4 (sqrt via brute pow since q small)
    h = a*inv(2, q) % q
    t = (b+8*pow(h, 5, q))*inv(10*pow(h, 5, q), q) % q
    if t == 0: return 2 if leg(-1, q) == 1 else 0
    if leg(t, q) == -1: return 0
    u = next(x for x in range(1, q) if x*x % q == t) if q < 5000 else sqrt_mod(t, q)
    return (1+leg(u-1, q))+(1+leg(-u-1, q))

print("== E2a real field Pallas, sampling (random a, random b): independent root count vs closed form ==")
cnt = {}; bad = 0; n = 1500
for _ in range(n):
    a = rnd.randrange(1, P); b = rnd.randrange(P)
    N = nroots_quartic(a, b, P); cnt[N] = cnt.get(N, 0)+1
    if N != predicted(a, b, P): bad += 1
print("samples", n, "counts", dict(sorted(cnt.items())), "mismatch vs closed form:", bad)
print("fractions:", {k: round(v/n, 4) for k, v in sorted(cnt.items())}, "  predicted 0:5/8=.625 2:1/4=.25 4:1/8=.125 (3: 1/p)")
print("== E2b real field, the special b ==")
a = rnd.randrange(1, P); h = a*inv(2) % P
for name, b in (("b=2h^5 = a^5/16", 2*pow(h, 5, P) % P), ("b=-8h^5 (D=0)", -8*pow(h, 5, P) % P), ("b=0", 0), ("b=a^5 (x=0 is a root)", pow(a, 5, P))):
    print(name, "-> solutions", nroots_quartic(a, b, P), " closed form", predicted(a, b, P))
print("== E2c homogeneity: spectrum for a depends on a only via scaling b -> a^5 b (check 200 pairs) ==")
ok = 0
for _ in range(200):
    a = rnd.randrange(1, P); b = rnd.randrange(P); l = rnd.randrange(1, P)
    ok += nroots_quartic(a, b, P) == nroots_quartic(l*a % P, pow(l, 5, P)*b % P, P)
print("agree", ok, "/200")

print("== E2d toys exhaustive: spectrum {#b with k solutions}, a=1, primes with gcd(5,q-1)=1; formula fits by q mod 8 ==")
from sympy import primerange
rows = []
for q in primerange(11, 3500):
    if (q-1) % 5 == 0: continue
    spec = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}
    # brute force count solutions over x for each b
    tbl = {}
    for x in range(q):
        d = (pow(x+1, 5, q)-pow(x, 5, q)) % q; tbl[d] = tbl.get(d, 0)+1
    for b in range(q): spec[tbl.get(b, 0)] += 1
    rows.append((q, q % 8, spec))
for q, m8, s in rows[:12]+rows[-4:]:
    print("q=%5d q%%8=%d  %s"%(q, m8, {k: v for k, v in s.items() if v or k in (0, 2, 3, 4)}))
print("-- fits n_k = (alpha*q + beta)/8, per class q mod 8, fitted on the two smallest, checked on all")
for m8 in (1, 3, 5, 7):
    cl = [(q, s) for q, mm, s in rows if mm == m8]
    if len(cl) < 3: print("class", m8, "too few primes"); continue
    out = []
    for k in (0, 1, 2, 3, 4):
        (q1, s1), (q2, s2) = cl[0], cl[1]
        alpha = Fraction(s1[k]-s2[k], q1-q2)*8
        beta = (s1[k]-alpha*q1/8)*8
        fits = all(Fraction(s[k]) == (alpha*q+beta)/8 for q, s in cl)
        out.append((k, str(alpha), str(beta), fits))
    print("class q=%d mod 8 (%d primes): "%(m8, len(cl)), "; ".join("n%d=(%s q + %s)/8 fits=%s"%o for o in out))
print("-- closed form (u-parametrisation) vs brute force on toys, all b, a random")
bad = 0; tot = 0
for q in (17, 29, 37, 97, 193, 257, 769, 1009, 4099, 12289):
    if (q-1) % 5 == 0: continue
    a = rnd.randrange(1, q)
    tbl = {}
    for x in range(q):
        d = (pow(x+a, 5, q)-pow(x, 5, q)) % q; tbl[d] = tbl.get(d, 0)+1
    for b in range(q):
        tot += 1; bad += tbl.get(b, 0) != predicted_gen(a, b, q)
print("checked", tot, "(a,b) pairs, mismatches", bad)
print("== E2e prediction for Pallas (p = 1 mod 8): counts per a, as exact numbers ==")
n4 = (P-9)//8; n3 = 1; n2 = (P+3)//4; n0 = P-n4-n3-n2
print("n4 = (p-9)/8 =", n4); print("n2 = (p+3)/4 =", n2); print("n3 = 1"); print("n0 = 5(p-1)/8 =", n0, "  check 5(p-1)/8:", n0 == 5*(P-1)//8)
