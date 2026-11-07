#!/usr/bin/env python3
"""diag.py (untried/ctr_alg; research only) - two checks behind e3sat.py.
(1) Plant feasibility for the beta* outcomes: Lipmaa-Moriai xdp+ weights of condition (1) [(q + h1) vs (q + h1^eta)]
    and of condition (3) given (1),(2) [(g1 + h2) vs (g1^G + h2^dh2), dh2 = ror(eta ^ eps, 8)], plus a sampled rate.
(2) Every kissat counter on one real system (sys00.cnf written by e3sat.py), to see where its work is counted.
"""
import os, random, subprocess, sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '..', '..', 'counter_next', 'stack')))
import e3solve as S  # noqa: E402
M, ETA, EPS = S.M, S.ETA, S.EPS
DH2 = S.ror(ETA ^ EPS, 8)


def lm(a, b, g):
    """xdp+(a, b -> g): None if impossible, else weight w (probability 2^-w)."""
    def eq(x, y, z): return (~x ^ y) & (~x ^ z) & M
    s = lambda x: (x << 1) & M
    if eq(s(a), s(b), s(g)) & (a ^ b ^ g ^ s(b)):
        return None
    return bin(~eq(a, b, g) & 0x7FFFFFFF).count('1')


rng = random.Random(5)
print(f'eta {ETA:08x}  eps {EPS:08x}  dh2 = ror(eta^eps, 8) = {DH2:08x}')
for k, t in enumerate(S.TAUS):
    G = S.G(t)
    w1 = lm(0, ETA, G); w3 = lm(G, DH2, t)
    hits = sum(((g1 + h2) & M) ^ (((g1 ^ G) + (h2 ^ DH2)) & M) == t
               for g1, h2 in ((rng.getrandbits(32), rng.getrandbits(32)) for _ in range(1 << 18)))
    print(f'tau#{k} {t:08x} G {G:08x}: (1) xdp+ weight {w1}; (3) xdp+(G, dh2 -> tau) weight {w3}; '
          f'(3) sampled {hits} of 2^18')
if len(sys.argv) > 1:
    out = subprocess.run(['kissat', '--time=60', '-s', '-n', sys.argv[1]], capture_output=True, text=True).stdout
    print('\n'.join(l for l in out.splitlines() if l.startswith('c ') and ':' in l and not l.startswith('c   ')))
