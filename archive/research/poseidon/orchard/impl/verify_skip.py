"""Check (COMPUTED, small scale) the coordinator's 'skip round 0 and 1' parametrisation for r = 1, 2.

For each kept coordinate j in {0,1,2}:
  U = (nk+c0_0)^5, V = (rho+c0_1)^5 (bijective, since gcd(5,p-1)=1);
  round-1 S-box input  x(U,V) = M[:,0] U + M[:,1] V + M[:,2] K' + c1,  K' = (2^65 + c0_2)^5  (affine in (U,V));
  direction d = M[j,1]*M[:,0] - M[j,0]*M[:,1]  (so d_j = 0), point Q with Q_i = 0 for i != j;
  line (U,V) = (U0,V0) + tau*(a,b), W = tau^5.
Claims verified: (1) round-1 S-box outputs are affine in W; (2) the state after round 1 is affine in W;
(3) the state after round 3 (+ k partial rounds) has degree exactly 5^(2+k) in W (finite differences);
(4) distinct W give distinct (nk, rho) that hash (full target) to F(W); (5) h(s)=F(c+s)-F(c-s) is odd.
"""
import random, sys
from poseidon_ref import *

random.seed(7)
INV5 = pow(5, -1, P - 1)
assert (5 * INV5) % (P - 1) == 1
root5 = lambda x: pow(x, INV5, P)
inv = lambda x: pow(x, P - 2, P)


def setup_line(j):
    Kp = pow((CAPACITY + RC[0][2]) % P, 5, P)
    base = [(MDS[i][2] * Kp + RC[1][i]) % P for i in range(3)]          # x = M[:,0]U + M[:,1]V + base
    a, b = MDS[j][1], (-MDS[j][0]) % P
    d = [(MDS[i][0] * a + MDS[i][1] * b) % P for i in range(3)]
    assert d[j] == 0
    ii = [i for i in range(3) if i != j]
    # solve MDS[i][0]U + MDS[i][1]V = -base[i] for the two i != j
    (p0, q0), (p1, q1) = (MDS[ii[0]][0], MDS[ii[0]][1]), (MDS[ii[1]][0], MDS[ii[1]][1])
    det = (p0 * q1 - p1 * q0) % P
    assert det != 0
    r0, r1 = (-base[ii[0]]) % P, (-base[ii[1]]) % P
    U0 = (r0 * q1 - r1 * q0) * inv(det) % P
    V0 = (p0 * r1 - p1 * r0) * inv(det) % P
    return a, b, U0, V0, d


def inputs_for_tau(tau, a, b, U0, V0):
    U = (U0 + a * tau) % P; V = (V0 + b * tau) % P
    return (root5(U) - RC[0][0]) % P, (root5(V) - RC[0][1]) % P


def state_after(nk, rho, upto_partial):
    s = [nk, rho, CAPACITY]
    for idx in range(4 + upto_partial):
        s = round_full(s, idx) if idx < 4 else round_partial(s, idx)
    return s


def fdiff_degree(vals, maxdeg):
    """vals at equally spaced points; return minimal d with (d+1)-th difference identically zero."""
    cur = list(vals)
    for k in range(1, maxdeg + 2):
        cur = [(cur[i + 1] - cur[i]) % P for i in range(len(cur) - 1)]
        if all(x == 0 for x in cur):
            return k - 1
    return None


for r in (1, 2):
    for j in range(3):
        a, b, U0, V0, d = setup_line(j)
        w0, h = random.randrange(1, P), random.randrange(1, P)
        npts = 5 ** (2 + r) + 4
        Ws = [(w0 + k * h) % P for k in range(npts)]
        taus = [root5(w) for w in Ws]
        pairs = [inputs_for_tau(t, a, b, U0, V0) for t in taus]
        assert len(set(pairs)) == npts                                          # distinct inputs
        # (1)/(2): after rounds 0 and 1 (both full): state affine in W
        s01 = []
        for nk, rho in pairs[:6]:
            s = [nk, rho, CAPACITY]; s = round_full(s, 0)
            x = [(s[i] + RC[1][i]) % P for i in range(3)]
            s01.append((x, [pow(v, 5, P) for v in x], round_full(s, 1)))
        for c in range(3):
            xs = [e[0][c] for e in s01]
            if c == j:
                assert all(v == xs[0] for v in xs)                                # kept coordinate is constant in tau
            else:
                assert len(set(xs)) > 1                                           # moves with tau
        # Q_i = 0 point is tau = 0: x_i(tau) = d_i * tau, so S-box output = d_i^5 * W
        for k, (x, sb, st) in enumerate(s01):
            for c in range(3):
                if c != j:
                    assert x[c] == d[c] * taus[k] % P and sb[c] == pow(d[c], 5, P) * Ws[k] % P
        def after_r01(nk, rho):
            return round_full(round_full([nk, rho, CAPACITY], 0), 1)
        st01 = [after_r01(nk, rho) for nk, rho in pairs[:5]]
        sdeg1 = [fdiff_degree([v[c] for v in st01], 3) for c in range(3)]
        assert sdeg1 == [1, 1, 1], sdeg1                                        # affine in W
        # (3): degree after rounds 0..3 and k partial rounds = 5^(2+k)
        degs = []
        for kk in range(0, r + 1):
            nn = 5 ** (2 + kk) + 3
            vals = [state_after(nk, rho, kk) for nk, rho in pairs[:nn]]
            degs.append([fdiff_degree([v[c] for v in vals], 5 ** (2 + kk) + 1) for c in range(3)])
            assert degs[-1] == [5 ** (2 + kk)] * 3, (kk, degs[-1])
        print(f'r={r} j={j}: S-box outputs d_i^5*W exact; state after round 1 affine in W; degree after round 3 (+k partial) = {[5**(2+k) for k in range(r+1)]} verified; distinct inputs {npts}')
    # (4)/(5) on one line, full target, plus oddness of h(s)
    a, b, U0, V0, d = setup_line(0)
    F = lambda W: hash_reduced(*inputs_for_tau(root5(W), a, b, U0, V0), r)
    c0 = random.randrange(P)
    for _ in range(3):
        s = random.randrange(1, P)
        assert (F((c0 + s) % P) - F((c0 - s) % P)) % P == (-(F((c0 - s) % P) - F((c0 + s) % P))) % P
    # explicit forced collision of F at W, W' to check the map back is injective & the hash is a function of W
    W1, W2 = random.randrange(P), random.randrange(P)
    assert inputs_for_tau(root5(W1), a, b, U0, V0) != inputs_for_tau(root5(W2), a, b, U0, V0)
    # round-trip: W -> (nk,rho) -> U,V,tau -> W
    nk, rho = inputs_for_tau(root5(W1), a, b, U0, V0)
    U = pow((nk + RC[0][0]) % P, 5, P); V = pow((rho + RC[0][1]) % P, 5, P)
    tau = (U - U0) * inv(a) % P
    assert (V - V0) * inv(b) % P == tau and pow(tau, 5, P) == W1
    print(f'r={r}: map-back round trip ok; F(W) = hash(nk(W), rho(W)) well-defined')
print('verify_skip: OK')
