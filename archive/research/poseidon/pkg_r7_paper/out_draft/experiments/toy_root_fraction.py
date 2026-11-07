"""Small-field analogue of the line construction: how often does a centre give a usable root?

The claim's premise H_root is about the deployed Orchard Poseidon over the 255-bit Pallas field at degree
5^(6+r) (millions to billions). Nothing here reaches that size. This program builds the SAME CONSTRUCTION on a
toy Poseidon-like permutation over a small prime p (p = 2 mod 5, so x -> x^5 is a bijection): state [nk, rho, cap],
two full rounds, a line in the (U, V) plane that makes round 1 free, L further layers (full and partial rounds),
digest = coordinate 0 after the last MDS. Constants and the 3x3 MDS are drawn from a fixed seed (they are NOT the
deployed constants, whose field is far larger).

For each toy it (1) checks the line against the genuine permutation, (2) checks that the digest polynomial F(W)
has degree exactly D = 5^L by finite differences, (3) for EVERY centre c in F_p decides exactly whether some
s != 0 has F(c+s) = F(c-s) (equivalently, the odd part g_c has a root S = s^2 that is a nonzero square), and
(4) does the same for a uniformly random table as a control. The reported number is the exact fraction of centres,
for that one fixed toy function. It is a measurement on toys. It is not a bound for the deployed target, it is not
a sampled probability, and the seeds are fixed in this file (declared in advance), not taken from the request.
"""
import json
import random
import sys
from math import comb
from operator import eq

SEED = "toy-root-fraction-v1"
PATTERNS = ((3, "FPF"), (4, "FFPF"))     # (L, kinds of the layers after the free round): F full, P partial


def next_prime(n):
    while True:
        n += 1
        if n % 5 == 2 and all(n % q for q in range(2, int(n ** 0.5) + 1)):
            return n


def build(p, L, kinds, rng):
    while True:
        M = [[rng.randrange(1, p) for _ in range(3)] for _ in range(3)]
        m2 = [M[a][b] * M[c][d] - M[a][d] * M[c][b] for a in range(3) for c in range(a + 1, 3)
              for b in range(3) for d in range(b + 1, 3)]
        det = (M[0][0] * (M[1][1] * M[2][2] - M[1][2] * M[2][1]) - M[0][1] * (M[1][0] * M[2][2] - M[1][2] * M[2][0])
               + M[0][2] * (M[1][0] * M[2][1] - M[1][1] * M[2][0]))
        if all(x % p for x in m2) and det % p:
            break
    rc = [[rng.randrange(p) for _ in range(3)] for _ in range(2 + L)]
    cap = rng.randrange(p)

    def mds(s):
        return [sum(M[i][j] * s[j] for j in range(3)) % p for i in range(3)]

    def layer(s, i, partial):
        s = [(x + c) % p for x, c in zip(s, rc[i])]
        for k in (range(1) if partial else range(3)):
            s[k] = pow(s[k], 5, p)
        return mds(s)

    def H(nk, rho):
        s = layer([nk, rho, cap], 0, False)
        s = layer(s, 1, False)
        for j, kd in enumerate(kinds):
            s = layer(s, 2 + j, kd == "P")
        return s[0]

    # line: x_k = M_k0 U + M_k1 V + b_k, with x_1 = x_2 = 0 at Q, direction (a, b) keeps x_0 constant
    K5 = pow((cap + rc[0][2]) % p, 5, p)
    bb = [(M[k][2] * K5 + rc[1][k]) % p for k in range(3)]
    det2 = (M[1][0] * M[2][1] - M[1][1] * M[2][0]) % p
    inv = pow(det2, p - 2, p)
    UQ = ((-bb[1]) * M[2][1] - (-bb[2]) * M[1][1]) * inv % p
    VQ = (M[1][0] * (-bb[2]) - M[2][0] * (-bb[1])) * inv % p
    a, b = M[0][1], (-M[0][0]) % p
    kappa = (M[0][0] * UQ + M[0][1] * VQ + bb[0]) % p
    d = [0] + [(M[i][0] * a + M[i][1] * b) % p for i in (1, 2)]
    v0 = pow(kappa, 5, p)
    v1 = [0, pow(d[1], 5, p), pow(d[2], 5, p)]

    def F(W):
        s = mds([v0, v1[1] * W % p, v1[2] * W % p])
        for j, kd in enumerate(kinds):
            s = layer(s, 2 + j, kd == "P")
        return s[0]

    e = (4 * (p - 1) + 1) // 5
    return H, F, (UQ, VQ, a, b, e, rc)


def exact_fraction(T, p):
    h = (p - 1) // 2
    T2 = T + T
    hit = 0
    for c in range(p):
        A = T2[c + 1:c + 1 + h]
        B = T2[c + p - h:c + p][::-1]
        hit += any(map(eq, A, B))
    return hit


def main():
    request = json.loads(sys.stdin.read())
    p = next_prime(8000)
    obs = {"toy_p": p}
    rng = random.Random(SEED)
    for L, kinds in PATTERNS:
        H, F, (UQ, VQ, a, b, e, rc) = build(p, L, kinds, rng)
        D = 5 ** L
        line_ok = True
        for _ in range(20):
            tau = rng.randrange(1, p)
            nk = (pow((UQ + tau * a) % p, e, p) - rc[0][0]) % p
            rho = (pow((VQ + tau * b) % p, e, p) - rc[0][1]) % p
            line_ok &= H(nk, rho) == F(pow(tau, 5, p))
        vals = [F(w) for w in range(D + 2)]
        diff = lambda n: sum((-1) ** (n - k) * comb(n, k) * vals[k] for k in range(n + 1)) % p
        degree_ok = diff(D + 1) == 0 and diff(D) != 0
        T = [F(w) for w in range(p)]
        hits = exact_fraction(T, p)
        ctl = [rng.randrange(p) for _ in range(p)]
        chits = exact_fraction(ctl, p)
        obs["L%d_D" % L] = D
        obs["L%d_line_ok" % L] = int(line_ok)
        obs["L%d_degree_ok" % L] = int(degree_ok)
        obs["L%d_centres_with_root" % L] = hits
        obs["L%d_centres_total" % L] = p
        obs["L%d_control_with_root" % L] = chits
    trials = [{"trial": t["trial"], "message_a_hex": None, "message_b_hex": None, "observations": obs}
              for t in request["trials"]]
    sys.stdout.write(json.dumps({"schema_version": 1, "trials": trials}))


main()
