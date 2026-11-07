"""U9 Q1/Q3: leading-coefficient tracker on many random lines and on the axes. Exact big-int.
Each lane = (degree, leading coeff). lc nonzero at every lane after every M  => line degree of every lane is exactly the generic one (PROVED for that line).
Also records lane degree after every round for lines in the nk direction (u=1,v=0), rho direction (u=0,v=1), (1,1)."""
import sys
from u9lib import *
random.seed(20261012+9)
def track(r, u, v, b_const=None, a_const=None):
    # lane = [deg, lc]; degree-0 lanes carry their constant in lc
    lane = [[1, u] if u else [0, random.randrange(1, P)], [1, v] if v else [0, random.randrange(1, P)], [0, CAP]]
    hist = []
    for n, idx in enumerate(schedule(r)):
        kd = kind(idx)
        for i in range(3):
            if lane[i][0] == 0: lane[i][1] = (lane[i][1] + RC[idx][i]) % P
        out = []
        for i in range(3):
            if kd == 'full' or i == 0: out.append([5*lane[i][0], pow(lane[i][1], 5, P)])
            else: out.append(list(lane[i]))
        if idx == 63:
            rows = [0]
        else: rows = [0, 1, 2]
        new = []
        for i in rows:
            dm = max(o[0] for o in out if True)
            # lanes with deg 0 contribute at degree 0 only
            terms = [(out[j][0], M[i][j]*out[j][1] % P) for j in range(3)]
            dm = max(t[0] for t in terms)
            c = sum(t[1] for t in terms if t[0] == dm) % P
            new.append([dm, c])
        if any(c == 0 for _, c in new):
            hist.append((idx, 'LC-ZERO', new)); return hist
        lane = new + [[0, 0]]*(3-len(new))
        hist.append((idx, [d for d, c in new]))
    return hist
for r in (1, 2):
    nz = 0; N = 300; exp = 5**(8+r)
    for trial in range(N):
        u, v = random.randrange(1, P), random.randrange(1, P)
        h = track(r, u, v)
        if h[-1][1] == 'LC-ZERO': nz += 1; log('  ZERO lc at', h[-1])
        else:
            assert h[-1][1][0] == exp, h[-1]
    log('r=%d: %d random lines (u,v nonzero random): zero leading coefficient in %d; final output degree %d = 5^%d on all others' % (r, N, nz, exp, 8+r))
    for lab, (u, v) in (('nk-direction (u=1,v=0), rho fixed', (1, 0)), ('rho-direction (u=0,v=1), nk fixed', (0, 1)), ('diagonal (1,1)', (1, 1)), ('(1,-1)', (1, P-1))):
        h = track(r, u, v)
        log('  r=%d %s: ' % (r, lab) + ' '.join('R%d:%s' % (i, d) for i, d in h))
