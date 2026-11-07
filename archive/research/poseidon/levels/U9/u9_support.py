"""U9 part C: exact bivariate supports on the real field via Kronecker encoding f(z, z^W).
usage: python u9_support.py <coords nk|AB> <r> <last_round_idx> <W> [verify]
Prints per round per lane: #monomials, total degree, deg in x, deg in y, full-triangle?, law check (nk coords)."""
import sys, numpy as np
from u9lib import *
coords, r, last, W = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
ring = Ring(P)
sch = schedule(r)
def law_set(N):
    return {(i, j) for i in range(5*N+1) for j in range(5*N+1) if -(-i//5) + -(-j//5) <= N}
def law_count(N):
    w = lambda m: 1 if m == 0 else 5
    return sum(w(m)*w(n) for m in range(N+1) for n in range(N+1-m))
def eval_biv(f, x, y):
    cs = f.coeffs(); s = 0
    xp = [1]*W
    for k in range(1, W): xp[k] = xp[k-1]*x % P
    ypow = 1; 
    for jj in range((len(cs)+W-1)//W):
        row = cs[jj*W:(jj+1)*W]
        s = (s + ypow*sum(int(c)*xp[k] for k, c in enumerate(row))) % P
        ypow = ypow*y % P
    return s
z = ring.x(); zW = ring.xpow(W)
if coords == 'nk':
    lanes = [z, zW, ring.const(CAP)]; todo = sch
else:
    K = pow((CAP + RC[0][2]) % P, 5, P)
    lanes = [z*M[i][0] + zW*M[i][1] + ring.const(M[i][2]*K) for i in range(3)]; todo = sch[1:]
    log('AB coords: lanes after R0.M are M_i0*A + M_i1*B + M_i2*K')
N = 1
for idx in todo:
    t = time.time()
    if idx > last: break
    kd = kind(idx)
    lanes = apply_round(ring, lanes, idx, M, RC)
    if coords == 'nk' and idx == 0: pass
    # (A,B) degree after this round
    row = []
    for i, l in enumerate(lanes):
        nzi, ln = ring.nz_index(l); s = stats2(nzi, W)
        row.append(s)
    log('R%d %s: ' % (idx, kd) + '; '.join('lane%d n=%d deg=%d degx=%d degy=%d fullTriangle=%s (tri=%d)' % (i, s['n'], s['deg'], s['degx'], s['degy'], s['full'], s['tri']) for i, s in enumerate(row)) + '  (%.1fs)' % (time.time()-t))
    if coords == 'nk' and row[0]['n'] > 0:
        Nn = {0: 1, 1: 5, 2: 25, 3: 125}.get(idx)
        if Nn:
            ex = law_set(Nn)
            for i, s in enumerate(row):
                got = set(zip(s['i'].tolist(), s['j'].tolist()))
                log('   law ceil(i/5)+ceil(j/5)<=%d : predicted count %d, lane %d actual %d, symmetric difference %d' % (Nn, law_count(Nn), i, len(got), len(got ^ ex)))
    if len(sys.argv) > 5 and sys.argv[5] == 'verify':
        xx, yy = random.randrange(P), random.randrange(P)
        if coords == 'nk':
            ref = R.perm([xx, yy, CAP], 0)  # placeholder replaced below
        # compare lane values with reference state after the same rounds
        if coords == 'nk':
            s = [xx, yy, CAP]
            for q in todo:
                s = R.round_full(s, q) if kind(q) == 'full' else R.round_partial(s, q)
                if q == idx: break
            xa, ya = xx, yy
        else:
            xa = pow(xx, 5, P); ya = pow(yy, 5, P)   # A = a^5 where a=xx? treat xx as nk with c0,0 = 0 trick not valid -> use a,b directly
            s = [xx, yy, CAP]
            s[0] = (xx - RC[0][0]) % P; s[1] = (yy - RC[0][1]) % P
            for q in sch:
                s = R.round_full(s, q) if kind(q) == 'full' else R.round_partial(s, q)
                if q == idx: break
            xa = pow(xx, 5, P); ya = pow(yy, 5, P)
        vals = [eval_biv(l, xa if coords == 'AB' else xx, ya if coords == 'AB' else yy) for l in lanes]
        log('   verify against poseidon_ref at random point: ', 'MATCH' if vals == s else 'MISMATCH')
log('total %.1fs' % (time.time()-T0))
