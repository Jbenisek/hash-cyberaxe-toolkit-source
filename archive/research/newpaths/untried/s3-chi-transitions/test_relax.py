"""Soundness test of the relaxation on real differences (ls.f2 = organizer _permute_lanes on the 1080-bit message).
For a seed word v and random base points m0: B1 = actual chi1 output difference, A2 = P(B1),
D3 = actual chi3-input difference = P(round-2 output difference). Check K(A2) <= D3 and N(A2) & D3 = 0.
Also checks P_or against the explicit union of single-bit P images, and Uspace on all 31 nonzero row differences."""
import random
import numpy as np
from common import *

rng = random.Random(1)
# Uspace sanity: identity reachable for single bits; dims
dims = {d: len(Uspace(d)[1]) for d in range(1, 32)}
print('U dims single-bit', [dims[1 << x] for x in range(5)], 'all', sorted(set(dims.values())))
# P_or check
for _ in range(20):
    bits = rng.sample(range(1600), 7)
    A = bits_to_lanes(bits)
    U = np.zeros((1, 25), U64)
    for b in bits: U |= P_or(bits_to_lanes([b])) if False else 0
    u2 = np.zeros((1, 25), U64)
    for b in bits: u2 |= P(bits_to_lanes([b]))
    assert (P_or(A) == u2).all()
print('P_or ok')
W = load_cycles()
FIDX = ls.FIDX
def vint(bits):
    m = 0
    for b in bits: m |= 1 << FIDX[b]
    return m
def lanes_arr(L): return np.array([L], dtype=U64)
bad = 0; tot = 0; Ksz = []; D3sz = []
for wi in rng.sample(range(len(W)), 40):
    vi = vint(W[wi])
    for _ in range(25):
        m0 = rng.getrandbits(ls.NF)
        s1a = lanes_arr(ls.f2(m0, 1)); s1b = lanes_arr(ls.f2(m0 ^ vi, 1))
        s2a = lanes_arr(ls.f2(m0, 2)); s2b = lanes_arr(ls.f2(m0 ^ vi, 2))
        B1 = s1a ^ s1b; A2 = P(B1); D3 = P(s2a ^ s2b)
        assert (P(B1) == P(s1a) ^ P(s1b)).all()
        K, N = chi_relax_KN(A2)
        tot += 1
        if (K & ~D3).any() or (N & D3).any(): bad += 1
        Ksz.append(int(popc(K)[0])); D3sz.append(int(popc(D3)[0]))
print('relaxation soundness: violations', bad, 'of', tot, '| |K| median', int(np.median(Ksz)), '| |D3| median', int(np.median(D3sz)))
