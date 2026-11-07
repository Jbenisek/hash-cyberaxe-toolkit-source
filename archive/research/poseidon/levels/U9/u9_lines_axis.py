"""U9 boring detail: line polynomials parallel to an axis. nk = a0 + t, rho = const: in the variable a = nk + c0,0 the output is G(a^5, B0), a polynomial in a^5 only.
In the variable t with a0 = -c0,0 (so t = a): exponents divisible by 5 only -> 4/5 of the coefficients are structurally zero. With a0 != -c0,0 (t = nk - a0): dense (binomial shift).
usage: python u9_lines_axis.py r mode   mode = center | shifted | rho_center"""
import sys
from u9lib import *
r, mode = int(sys.argv[1]), sys.argv[2]
random.seed(5)
ring = Ring(P)
b0 = random.randrange(P); a0 = random.randrange(P)
if mode == 'center': lanes = [ring.mk([(-RC[0][0]) % P, 1]), ring.const(b0), ring.const(CAP)]
elif mode == 'shifted': lanes = [ring.mk([a0, 1]), ring.const(b0), ring.const(CAP)]
else: lanes = [ring.const(a0), ring.mk([(-RC[0][1]) % P, 1]), ring.const(CAP)]
t0 = random.randrange(P)
refs = [ (lanes[0](t0)), lanes[1](t0) if lanes[1].degree()>=0 else 0, CAP ]
refs = [int(x) for x in refs]
refs = [(refs[0]) % P, refs[1] % P, CAP]
for idx in schedule(r):
    lanes = apply_round(ring, lanes, idx, M, RC) if idx != 63 else [ring.lin(M[0], [ring.pow5(lanes[i]+RC[63][i]) for i in range(3)])]
    refs = R.round_full(refs, idx) if kind(idx)=='full' else R.round_partial(refs, idx)
    okc = int(lanes[0](t0)) == refs[0]
    cs = lanes[0].coeffs(); n = len(cs)
    z = sum(1 for c in cs if c == 0)
    nz_exps_mod5 = sorted({k % 5 for k, c in enumerate(cs) if c != 0})
    log('r=%d mode=%s R%-2d lane0 degree %d, zero coefficients %d of %d (%.4f), residues of exponents mod 5 with nonzero coefficient: %s ; value check vs reference at random t: %s' % (r, mode, idx, n-1, z, n, z/n, nz_exps_mod5, 'MATCH' if okc else 'MISMATCH'))
