# U8: toy copies (exhaustive) + cycle lengths of x->x^5 on the real field.

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

import sys, random, time
from collections import Counter
from math import gcd
from sympy import isprime, factorint
from sympy.polys.galoistools import gf_factor, gf_irreducible_p, gf_pow_mod
from sympy.polys.domains import ZZ
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/orchard/impl'))
import poseidon_ref as R
def pr(*a): print(' '.join(str(x) for x in a), flush=True)
random.seed(88)

# ---- real field: Cauchy determinant fix and cycle lengths
P = R.P; M = R.MDS
N = [[pow(M[a][b], P-2, P) for b in range(3)] for a in range(3)]
x = [0, (N[1][0]-N[0][0]) % P, (N[2][0]-N[0][0]) % P]; y = [N[0][0], N[0][1], N[0][2]]
det = (M[0][0]*(M[1][1]*M[2][2]-M[1][2]*M[2][1])-M[0][1]*(M[1][0]*M[2][2]-M[1][2]*M[2][0])+M[0][2]*(M[1][0]*M[2][1]-M[1][1]*M[2][0])) % P
num = 1
for a in range(3):
    for b in range(a+1, 3): num = num*(x[b]-x[a]) % P*(y[b]-y[a]) % P
den = 1
for a in range(3):
    for b in range(3): den = den*(x[a]+y[b]) % P
pr("Cauchy det formula prod_{i<j}(x_j-x_i)(y_j-y_i)/prod(x_i+y_j) == det M:", num*pow(den, P-2, P) % P == det)
q69 = 539204044132271846773; q143 = 8999194758858563409123804352480028797519453
assert (1 << 32)*3*463*q69*q143 == P-1
def ordmod(a, m, fac):  # fac: dict prime->exp of phi(m)
    o = 1
    for pp, e in fac.items():
        o_ = o
    t = 1
    # multiplicative order of a mod m given factorisation of phi(m)
    phi = 1
    for pp, e in fac.items(): phi *= pp**e
    o = phi
    for pp, e in fac.items():
        for _ in range(e):
            if pow(a, o//pp, m) == 1: o //= pp
            else: break
    return o
pr("ord of 5 mod 3 =", ordmod(5, 3, {2: 1}), "(atlas G1 says 3 - a slip, ord must divide phi(3)=2)")
pr("ord of 5 mod 463 =", ordmod(5, 463, factorint(462)), " (462 =", factorint(462), ")")
pr("ord of 5 mod 2^32 =", 1 << 30, "(5 has order 2^(k-2) mod 2^k, k>=3)")
t0 = time.time()
f69 = factorint(q69-1); pr("q69 - 1 =", f69, "(%.1fs)" % (time.time()-t0))
o69 = ordmod(5, q69, f69); pr("ord of 5 mod q69 =", o69, " ; (q69-1)/ord =", (q69-1)//o69)
# q143-1: try ECM w/ time limit via sympy
import threading
res = {}
def work():
    try: res['f'] = factorint(q143-1, limit=10**6, use_ecm=True)
    except Exception as e: res['f'] = repr(e)
th = threading.Thread(target=work, daemon=True); th.start(); th.join(300)
pr("q143 - 1 factorisation attempt (300 s cap):", res.get('f', 'not finished'))
# ---- toy copies
def toy_search():
    out = []
    for q in range(3, 5_000_000, 2):
        pass
cands = [65537, 1000003]
# add primes q = 1 mod 3*2^12, q = 2 or 3 mod 5, q < 2^22 (mimic p: 1 mod 3, 1 mod 8, ord_5(q)=4, high 2-adicity)
for m in range(1, 1000):
    q = 3*(1 << 12)*m+1
    if q < 2**22 and isprime(q) and q % 5 in (2, 3): cands.append(q)
pr("\ntoy primes:", cands[:12])
def toy(q):
    pr("\n=== toy q =", q, " q-1 =", factorint(q-1), " q mod 5 =", q % 5, " q mod 8 =", q % 8, " gcd(5,q-1) =", gcd(5, q-1))
    assert gcd(5, q-1) == 1
    # 5th root unique: map is a bijection
    img = set(pow(v, 5, q) for v in range(q)); pr("x->x^5 is a bijection of F_q:", len(img) == q)
    # fixed points
    fp = [v for v in range(q) if pow(v, 5, q) == v]; pr("fixed points of x^5:", len(fp), "=", fp if len(fp) < 8 else "...", " (1+gcd(4,q-1) =", 1+gcd(4, q-1), ")")
    # cycle structure
    seen = bytearray(q); cyc = Counter()
    for v in range(q):
        if seen[v]: continue
        L = 0; w = v
        while not seen[w]:
            seen[w] = 1; w = pow(w, 5, q); L += 1
        cyc[L] += 1
    pr("cycle-length histogram of x->x^5 (length: #cycles) first 12:", sorted(cyc.items())[:12], " max length", max(cyc), " total cycles", sum(cyc.values()))
    # predicted max cycle = ord of 5 in (Z/(q-1))^*
    n = q-1; ph = 1
    for pp, e in factorint(n).items(): ph *= (pp-1)*pp**(e-1)
    o = 1
    while pow(5, o, n) != 1: o += 1
    pr("ord of 5 mod (q-1) =", o, "(= max cycle length predicted)")
    # characters invariance & octic permutation
    s2 = (q-1).bit_length()
    v2 = 0; t = q-1
    while t % 2 == 0: t //= 2; v2 += 1
    pr("2-adicity of q:", v2)
    g = next(z for z in range(2, q) if pow(z, (q-1)//2, q) == q-1)
    inv_ok = all(pow(pow(v, 5, q), (q-1)//2, q) == pow(v, (q-1)//2, q) for v in range(1, q, 7))
    pr("quadratic character preserved by x^5:", inv_ok)
    if q % 4 == 1:
        i = pow(g, (q-1)//4, q)
        inv4 = all(pow(pow(v, 5, q), (q-1)//4, q) == pow(v, (q-1)//4, q) for v in range(1, q, 7))
        pr("sqrt(-1) =", i, "; quartic character preserved by x^5:", inv4)
    # 2-depth histogram
    odd = (q-1) >> v2
    H = Counter()
    for v in range(1, q):
        tt = pow(v, odd, q); o = 0
        while tt != 1: tt = tt*tt % q; o += 1
        H[v2-o] += 1
    pr("2-depth histogram of F_q^* (depth: count):", sorted(H.items()), "(expected (q-1)/2^(d+1), top level d=%d has %d)" % (v2, odd))
    # elements of order 2^k
    pr("number of elements of order 2^k, k=1..6:", [sum(1 for v in range(1, q) if pow(v, 1 << k, q) == 1 and pow(v, 1 << (k-1), q) != 1) for k in range(1, 7)] if q < 100000 else "(skipped, q large)")
    # x^5-c pattern
    pat = Counter()
    for c in random.sample(range(1, q), 100):
        F = gf_factor([1, 0, 0, 0, 0, (-c) % q], q, ZZ)[1]
        pat[tuple(sorted((len(f)-1, e) for f, e in F))] += 1
    pr("x^5-c factor patterns (100 random c):", dict(pat), "; Phi5 irreducible:", gf_irreducible_p([1, 1, 1, 1, 1], q, ZZ), "ord_5(q) =", next(k for k in range(1, 5) if pow(q, k, 5) == 1))
    # cubic
    if q % 3 == 1:
        cubes = set(pow(v, 3, q) for v in range(1, q))
        a = next(a for a in range(2, q) if a not in cubes)
        fr = pow(a, (q-1)//3, q); w = [pow(g, (q-1)//3, q), pow(g, 2*(q-1)//3, q)]
        pr("cubes among F_q^*:", len(cubes), "= (q-1)/3:", len(cubes) == (q-1)//3, "; smallest non-cube a =", a, "; theta^q = theta*", fr, "= omega" if fr == w[0] else "= omega^2", "where omega=", w[0])
    else:
        pr("q mod 3 =", q % 3, ": x->x^3 is a bijection; every x^3-a has exactly one root; F_{q^3} needs a different cubic")
        # find irreducible cubic x^3 - x - a
        for a in range(1, 50):
            if gf_irreducible_p([1, 0, -1 % q, (-a) % q], q, ZZ):
                pr("smallest a with x^3-x-a irreducible:", a); break
for q in [c for c in cands if c<1100000][:5]:
    toy(q)
pr("done")
