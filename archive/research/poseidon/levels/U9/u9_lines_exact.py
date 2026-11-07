"""U9 Q6: exact line polynomials nk=a+u t, rho=b+v t through all rounds with python-flint (dense, exact).
usage: python u9_lines_exact.py <r> <seed> <timecap_seconds>
Per round: degree of each lane after S and after M, zero coefficients strictly inside [0,deg] per lane, state check at a random t against poseidon_ref."""
import sys
from u9lib import *
r, seed, cap = int(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3])
random.seed(seed)
ring = Ring(P)
a, b, u, v = [random.randrange(1, P) for _ in range(4)]
t0 = random.randrange(P)
lanes = [ring.mk([a, u]), ring.mk([b, v]), ring.const(CAP)]
log('r=%d seed=%d line: nk=a+u t, rho=b+v t; a=%s.. u=%s..' % (r, seed, hex(a)[:12], hex(u)[:12]))
ref = [(a+u*t0) % P, (b+v*t0) % P, CAP]
sch = schedule(r)
def zeros_inside(f):
    cs = f.coeffs(); z = [k for k, c in enumerate(cs) if c == 0]
    return len(cs)-1, z
for n, idx in enumerate(sch):
    t = time.time(); kd = kind(idx)
    lanes = [lanes[i] + RC[idx][i] for i in range(3)]
    lanes = [ring.pow5(l) if (kd == 'full' or i == 0) else l for i, l in enumerate(lanes)]
    degS = [l.degree() for l in lanes]
    last = (idx == 63)
    if last:
        lanes = [ring.lin(M[0], lanes)]
    else:
        lanes = [ring.lin(M[i], lanes) for i in range(3)]
    out = []
    for l in lanes:
        d, z = zeros_inside(l); out.append((d, len(z), z[:5]))
    ref = R.round_full(ref, idx) if kd == 'full' else R.round_partial(ref, idx)
    ok = all(int(lanes[i](t0)) == ref[i] for i in range(len(lanes)))
    exp = 5**(n+1)
    log('R%-2d %-7s degS=%s degM=%s expected 5^%d=%d  zero-coeffs-inside=%s first zero idx=%s  state-check=%s (%.0fs, %.0fs total)' % (
        idx, kd, degS, [o[0] for o in out], n+1, exp, [o[1] for o in out], [o[2] for o in out], 'MATCH' if ok else 'MISMATCH', time.time()-t, time.time()-T0))
    if time.time()-T0 > cap and not last:
        log('STOPPED: time cap reached before next round'); break
