"""U9 Q7 (toy, exhaustive): rank of the 3x2 Jacobian of the state w.r.t. (A,B) after every round, all q^2 points, numpy.
(A,B)=(a^5,b^5) is a bijection of the input domain; nk-coordinate Jacobian = AB-Jacobian * diag(5a^4,5b^4), so the two axes a=0,b=0 (2q-1 points) are rank<=1 for every round.
Reports per round: #points with rank<=1 (AB coords), #rank 0, cause split, nesting check, output-gradient zeros.
usage: python u9_toy_jac.py q seed r"""
import sys, numpy as np
from u9toy import *
q, seed, r = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
Mx, RCx, cap = toy_params(q, seed)
K = pow((cap + RCx[0][2]) % q, 5, q)
A, B = np.meshgrid(np.arange(q, dtype=np.int64), np.arange(q, dtype=np.int64), indexing='ij'); A = A.ravel(); B = B.ravel()
n = A.size
s = [(Mx[i][0]*A + Mx[i][1]*B + Mx[i][2]*K) % q for i in range(3)]
J = [[np.full(n, Mx[i][0], dtype=np.int64), np.full(n, Mx[i][1], dtype=np.int64)] for i in range(3)]
def rank_info(J):
    m = [(J[a][0]*J[b][1] - J[a][1]*J[b][0]) % q for a, b in ((0,1),(0,2),(1,2))]
    r2 = (m[0] != 0) | (m[1] != 0) | (m[2] != 0)
    r0 = np.ones(n, bool)
    for i in range(3):
        for j in range(2): r0 &= (J[i][j] == 0)
    return r2, r0
prev = None
print('q=%d seed=%d r=%d (toy, %d points)' % (q, seed, r, n))
for idx in sched(r)[1:]:
    kd = kind(idx)
    s = [(s[i] + RCx[idx][i]) % q for i in range(3)]
    zeros = sum((s[i] == 0).astype(np.int64) for i in range(3))
    S = []; d = []
    for i in range(3):
        if kd == 'full' or i == 0:
            s2 = s[i]*s[i] % q; s4 = s2*s2 % q; S.append(s4*s[i] % q); d.append(5*s4 % q)
        else:
            S.append(s[i]); d.append(np.ones(n, dtype=np.int64))
    Jd = [[d[i]*J[i][j] % q for j in range(2)] for i in range(3)]
    s = [sum(Mx[i][j]*S[j] for j in range(3)) % q for i in range(3)]
    J = [[sum(Mx[i][l]*Jd[l][j] for l in range(3)) % q for j in range(2)] for i in range(3)]
    r2, r0 = rank_info(J)
    low = ~r2
    # cause
    dbl = low & (zeros >= 2)
    sgl = low & (zeros == 1)
    non = low & (zeros == 0)
    nested = True if prev is None else bool(np.all(low[prev]))
    print('R%-2d %-7s rank<=1: %5d (rank0: %d)  cause: >=2 S-inputs zero %d | exactly 1 zero (rows dependent) %d | none %d ; previous set contained in this: %s' % (idx, kd, low.sum(), r0.sum(), dbl.sum(), sgl.sum(), non.sum(), nested))
    prev = low.copy()
# output gradient
g0, g1 = J[0]
crit = (g0 == 0) & (g1 == 0)
print('final lane-0 gradient (dy/dA, dy/dB) = (0,0) at %d points of %d ; of those, state-Jacobian rank<=1: %d' % (crit.sum(), n, (crit & prev).sum()))
print('rank<=1 points of the final state Jacobian: %d ; in nk coords add the axes (2q-1 = %d points)' % (prev.sum(), 2*q-1))
