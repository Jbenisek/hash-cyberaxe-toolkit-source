"""U9 Q5/Q7 follow-up: for each round, number of F_p-roots of each lane's top form (directions where THAT lane loses degree) and the degree of gcd of the three lane forms (directions where ALL lanes lose degree = the whole state drops).
Only rounds with formal degree <= 625 (afterwards all lanes are proportional, see u9_topform_factor.py)."""
from u9lib import *
ring = Ring(P); z = ring.x()
f = [z*M[i][0] + M[i][1] for i in range(3)]; d = 1
r = 1
log('after R0: lane forms M_i0*U+M_i1*V : roots per lane (F_p) = 1 each (linear), gcd degree = %d' % f[0].gcd(f[1]).gcd(f[2]).degree())
for idx in schedule(r)[1:]:
    if kind(idx) == 'full':
        g = [ring.pow5(x) for x in f]; f = [ring.lin(M[i], g) for i in range(3)]
    else:
        g0 = ring.pow5(f[0]); f = [g0*M[i][0] for i in range(3)]
    d *= 5
    if d > 625: break
    nr = [len(x.roots()) for x in f]
    gd = f[0].gcd(f[1]).gcd(f[2]).degree()
    log('after R%-2d: formal degree %d ; distinct F_p roots per lane %s ; deg gcd(lane0,lane1,lane2) = %d (common roots over closure; 0 means no direction drops all three lanes)' % (idx, d, nr, gd))
