"""H2: per-centre odd part g(S) of the line-j digest polynomial and its root structure with FLINT (own driver).
usage: h2_flint.py r j ncentres seed [centre_mode]   (centre_mode 'zero' tests c=0 as well)"""
import sys, time, json, random
from pos_scan_lib import *
import flint
from flint import fmpz_mod_poly_ctx, fmpz_mod_ctx, fmpz
r = int(sys.argv[1]); j = int(sys.argv[2]); nc = int(sys.argv[3]); seed = int(sys.argv[4])
pw = {0: 14, 1: 17, 2: 19}[r]
n = 1 << pw
w = root_of_unity(n)
pts = [mpz(1)]
for _ in range(n - 1):
    pts.append(pts[-1] * w % P)
alpha, beta, line = line_affine(j)
specs = specs_from_2(r)
D = 5 ** (6 + r)
m = (D - 1) // 2
fctx = fmpz_mod_ctx(P)
R = fmpz_mod_poly_ctx(fctx)
X = R([0, 1])
half = (P - 1) // 2
rng = random.Random(seed)
out = []
centres = [0] + [rng.randrange(1, P) for _ in range(nc - 1)] if (len(sys.argv) > 5 and sys.argv[5] == 'zero') else [rng.randrange(1, P) for _ in range(nc)]
for c in centres:
    t0 = time.time()
    vals = [F_eval(alpha, beta, specs, (c + s) % P) for s in pts]
    co = intt(vals, w)
    assert poly_degree(co) == D
    lead2 = 2 * co[D] % P
    g_co = [int(2 * co[2 * i + 1] % P) for i in range(m + 1)]
    assert g_co[m] == lead2
    li = pow(lead2, P - 2, P)
    g = R([int(x * li % P) for x in g_co])           # monic
    assert g.degree() == m
    t1 = time.time()
    gd = g.derivative()
    sq = g.gcd(gd)
    t2 = time.time()
    # roots S that are nonzero squares: gcd(g, S^h - 1)
    if len(sys.argv) > 6 and sys.argv[6] == 'sqfree':
        gcd_sq = gcd_nonsq = R([1])
    else:
        Sh = X.pow_mod(half, g)
        gcd_sq = g.gcd(Sh - R([1]))
        gcd_nonsq = g.gcd(Sh + R([1]))
    t3 = time.time()
    rec = dict(r=r, j=j, c=hex(c), deg_g=g.degree(), gcd_g_gprime_degree=sq.degree(), deg_gcd_square_roots=gcd_sq.degree(),
               deg_gcd_nonsquare_roots=gcd_nonsq.degree(), sec_build=round(t1 - t0, 1), sec_sqfree=round(t2 - t1, 1), sec_roots=round(t3 - t2, 1))
    out.append(rec)
    print(json.dumps(rec), flush=True)
