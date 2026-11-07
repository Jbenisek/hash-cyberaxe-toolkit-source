"""U9 Q5 (real field): factor the top forms Phi_k(z) (z=U/V, U=X^5, V=Y^5) of lane 0 after each round up to formal degree 625 over F_p.
Also tests the proportionality claim: after the first partial round all three lanes' top forms are scalar multiples of ONE polynomial, and stay so through the full rounds that follow, so the output top form = c * Phi_R3,0 ^ (5^(rounds after R3)) (a perfect power)."""
import sys
from u9lib import *
ring = Ring(P)
z = ring.x()
for r in (1, 2):
    f = [z*M[i][0] + M[i][1] for i in range(3)]; d = 1
    hist = {}
    log('--- r=%d' % r)
    for idx in schedule(r)[1:]:
        kd = kind(idx)
        if kd == 'full':
            g = [ring.pow5(x) for x in f]; f = [ring.lin(M[i], g) for i in range(3)]
        else:
            g0 = ring.pow5(f[0]); f = [g0*M[i][0] for i in range(3)]
        d *= 5
        if idx == 3: phi3 = f[0]; phi3all = list(f)
        if idx >= 4 and idx < 60 or idx >= 60:
            pass
        # proportionality test: f_i * f_j[0-coefficient ratio]: f_i == c_i * f_0 ?
        prop = None
        if idx >= 4:
            c1 = f[1].leading_coefficient() / f[0].leading_coefficient(); c2 = f[2].leading_coefficient() / f[0].leading_coefficient()
            prop = (f[1] == f[0]*c1 and f[2] == f[0]*c2)
        if d <= 625:
            c, facs = f[0].factor()
            log('after R%-2d (%s) deg %d: lane0 factors: %s' % (idx, kd, d, sorted([(g.degree(), m) for g, m in facs])) + ('  lanes proportional: %s' % prop if prop is not None else ''))
        else:
            log('after R%-2d (%s) deg %d: lanes proportional (f_1 = c1 f_0, f_2 = c2 f_0): %s' % (idx, kd, d, prop))
        # perfect power test of final: lane 0 equals c * phi3^(5^k)?
        if idx >= 4:
            n = 5
            k = 1
            e = 1
            # exponent: number of S-box layers applied to phi3 so far = idx-state rounds after R3
            rounds_after = len([j for j in schedule(r) if j > 3 and (j < 60 or True)]) 
    # final exact check: output top form = c * phi3^(e), e = 5^(#rounds after R3)
    nafter = len(schedule(r)) - 4
    e = 5**nafter
    # compute phi3^e by repeated fifth powers
    h = phi3
    for _ in range(nafter): h = ring.pow5(h)
    c = f[0].leading_coefficient() / h.leading_coefficient()
    log('r=%d: output top form == c * (Phi_R3,0)^(5^%d) with c=%s... ? %s   (degree %d)' % (r, nafter, hex(int(c))[:18], f[0] == h*c, f[0].degree()))
