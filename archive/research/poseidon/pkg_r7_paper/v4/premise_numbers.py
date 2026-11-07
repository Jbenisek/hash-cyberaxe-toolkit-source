#!/usr/bin/env python3
"""Exact-rational recomputation of the success bound of proof.md section 9 for r = 7 (standard library only; prints every number used).
Premise H-GEOM-w gives E[k] >= 1/2 - e1 and E[k(k-1)] <= w/4 + e2 (Weil's bound with the plane genus bound; section 9.2).
Cauchy-Schwarz: P(k >= 1) >= E[k]^2 / (E[k] + E[k(k-1)]).  Markov on k(k-1): P(k >= DMAX+1) <= E[k(k-1)] / ((DMAX+1) DMAX).
q = P(1 <= k <= DMAX) >= the difference; K independent centres: 1 - (1-q)^K - K (eps_coin + eps_iso)."""
import math
from fractions import Fraction as Fr
from math import comb
P = (1 << 254) + 0x224698FC094CF91B992D30ED00000001
SP = 1 << 127                                   # floor(sqrt(P)) = 2^127, (2^127 + 1)^2 > P
R, DMAX, ZCAP = 7, 16, 64
D = 5 ** (6 + R); d = D - 1
# first moment: |N - P| <= (d-1)(d-2) sqrt(P) + d (d-1)(d-2)/2 + 2d + 1 for the plane curve G = 0 (degree d); E[k] = N*/(2P)
e1 = Fr((d - 1) * (d - 2) * (SP + 1) + d * (d - 1) * (d - 2) // 2 + 2 * d + 1, 2 * P)
# pair curve V: Bezout degree delta = d^2; N_V <= w (P+1) + (delta-1)(delta-2) sqrt(P) + (delta-1)(delta-2)/2 + delta^2; E[k(k-1)] = N_V / (4P)
delta = d * d
def e2_of(w): return Fr(w + (delta - 1) * (delta - 2) * (SP + 1) + (delta - 1) * (delta - 2) // 2 + delta * delta, 4 * P)
# coins: a draw is x = w mod P for one uniform 256-bit word w. 2^256 = 3 P + RES with 0 < RES < P: the residues below RES have 4 preimages, the other S3 = P - RES = 4 P - 2^256 have 3.
# statistical distance of x from uniform: eps_coin = S3 (1/P - 3/2^256).
# isolation lemma: a round is good (both parts nonconstant) when the shift a lies in a set of (P-1)/2 residues, at least (P-3)/2 of them nonzero; a is the draw x with 0 replaced by 1,
# every residue has at least 3 preimages and all but S3 residues have 4, so P[a in good] >= (4 (P-3)/2 - S3) / 2^256
RES = (1 << 256) - 3 * P
S3 = P - RES
assert 0 < RES < P and S3 == 4 * P - (1 << 256)
wq = Fr(4 * ((P - 3) // 2) - S3, 1 << 256)
eps_iso = sum(comb(ZCAP, j) * wq ** j * (1 - wq) ** (ZCAP - j) for j in range(0, 4))
eps_coin = S3 * (Fr(1, P) - Fr(3, 1 << 256))

def bound(w, K):
    e2 = e2_of(w)
    a = Fr(1, 2) - e1
    b = Fr(w, 4) + e2
    q_cs = a * a / (a + b)
    tail = b / ((DMAX + 1) * DMAX)
    q = q_cs - tail
    succ = 1 - (1 - q) ** K - K * (eps_coin + eps_iso)
    return dict(e2=e2, b=b, q_cs=q_cs, tail=tail, q=q, succ=succ, succ_notail=1 - (1 - q_cs) ** K)

def f(x, n=12): return '%.*f' % (n, float(x))

if __name__ == '__main__':
    W, K = 2, 2
    B = bound(W, K)
    print('D = 5^%d = %d, d = D - 1' % (6 + R, D))
    print('e1 < %.3e' % float(e1)); print('e2 < %s' % f(B['e2'], 10))
    print('E[k] >= 1/2 - e1; E[k(k-1)] <= w/4 + e2 = %s  (w = %d)' % (f(B['b'], 10), W))
    print('Cauchy-Schwarz: P(k >= 1) >= %s' % f(B['q_cs'], 10))
    print('Markov tail:    P(k > %d)  <= %s' % (DMAX, f(B['tail'], 10)))
    print('q = P(1 <= k <= %d) >= %s' % (DMAX, f(B['q'], 10)))
    print('K = %d without the tail (P(k >= 1) only): %s' % (K, f(B['succ_notail'], 10)))
    print('per-round good probability w >= %s = 1/2 - %.3e' % (f(wq, 20), float(Fr(1, 2) - wq)))
    print('eps_iso < %.3e (2^%.2f)   eps_coin < %.3e (2^%.2f)' % (float(eps_iso), math.log2(float(eps_iso)), float(eps_coin), math.log2(float(eps_coin))))
    print('success >= 1 - (1-q)^%d - %d (eps_coin + eps_iso) = %s' % (K, K, f(B['succ'], 12)))
    print('claimed success_probability: %s (floor at 5 decimals)' % ('%.5f' % (int(B['succ'] * 100000) / 100000)))
    for w in (1, 2, 3):
        Bw = bound(w, 2)
        print('w = %d: P(k>=1) >= %s, q >= %s, K=2 success %s, K=3 success %s' % (w, f(Bw['q_cs'], 8), f(Bw['q'], 8), f(Bw['succ'], 8), f(bound(w, 3)['succ'], 8)))
