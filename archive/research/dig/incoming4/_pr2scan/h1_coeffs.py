"""H1: exact coefficient vector of F(c+s) (s = shifted W) for the line-j digest polynomial, r given, via 2^k evaluations + inverse NTT.
usage: h1_coeffs.py r j c(0|seed) outbin"""
import sys, time, json, random
from pos_scan_lib import *
r = int(sys.argv[1]); j = int(sys.argv[2]); cm = sys.argv[3]; outbin = sys.argv[4]
pw = {0: 14, 1: 17, 2: 19}[r]
n = 1 << pw
t0 = time.time()
alpha, beta, line = line_affine(j)
specs = specs_from_2(r)
rng = random.Random(12345 if cm == '0' else int(cm))
c = 0 if cm == '0' else rng.randrange(1, P)
w = root_of_unity(n)
pts = [mpz(1)]
for _ in range(n - 1):
    pts.append(pts[-1] * w % P)
vals = [F_eval(alpha, beta, specs, (c + s) % P) for s in pts]
t1 = time.time()
co = intt(vals, w)
t2 = time.time()
D = poly_degree(co)
nz = sum(1 for x in co if x != 0)
# independent reconstruction check at random points off the grid
ok = True
for _ in range(3):
    s = rng.randrange(1, P)
    acc = mpz(0)
    for x in reversed(co[:D + 1]):
        acc = (acc * s + x) % P
    ok &= (acc == F_eval(alpha, beta, specs, (c + s) % P))
# full-hash check: F(W) equals reference hash on mapped inputs
W = rng.randrange(1, P)
hh = hash_reduced(*inputs_for_tau(root5(W), line), r)
okhash = (hh == F_eval(alpha, beta, specs, W))
par2 = [sum(1 for i, x in enumerate(co) if x != 0 and i % 2 == m) for m in (0, 1)]
par5 = [sum(1 for i, x in enumerate(co) if x != 0 and i % 5 == m) for m in range(5)]
with open(outbin, 'wb') as f:
    for x in co[:D + 1]:
        f.write(int(x).to_bytes(32, 'little'))
res = dict(r=r, j=j, c_mode=cm, c=hex(c), degree=D, expected=5 ** (6 + r), nonzero=nz, lead=hex(co[D]),
           reconstruct_ok=ok, ref_hash_ok=okhash, nonzero_by_parity=par2, nonzero_by_mod5=par5,
           sec_eval=round(t1 - t0, 1), sec_ntt=round(t2 - t1, 1), n_points=n)
print(json.dumps(res))
