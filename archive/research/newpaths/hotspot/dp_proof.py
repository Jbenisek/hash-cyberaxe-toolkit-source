#!/usr/bin/env python3
"""dp_proof.py (hotspot; research only) - EXACT carry counts (bit-serial dynamic programme) for the two strongest hot
spots, independent of any sampling.

E1 side. In the cube, c1b = c1 ^ CM (beta = beta*), and d2b = d2 ^ ror(tau, 8). So
    eps = (c1 + d2) ^ ((c1 ^ CM) + (d2 ^ ror(tau, 8)))
depends on (c1, d2) only. For each listed tau of beta*, count (c1 in the cube, d2 any 32-bit value) with eps = eps*,
split by the parities c1[11]^c1[12] and c1[20]^c1[22]. Every d2 value is reachable by some a2, so a zero count
means NO trial (any a1, Y6, w5, outer words) can give the listed E1 outcome in that cell.

E3 side. h1b = h1 ^ ETA (class), so Delta g1 = (y9 + h1) ^ (y9 + (h1 ^ ETA)) depends on (y9, h1) only, and the
listed partial E3 events of eps* need Delta f1 = ror(Delta g1, 12) in the eps* list. Count (y9, h1) per value of
(y9[0], y9[1], y9[2]); a zero count means no outer step with those Y9 bits can give such an event.
"""
from itertools import product
from ref import ror, rol, M, CM, CV, Y3A, Y3B, E3L

BETA_STAR = 0x18b0e098
TAUS = [0x175020a0, 0x175060a0, 0x185020a0, 0x185060a0, 0x275020a0, 0x275060a0, 0x285020a0, 0x285060a0, 0x385020a0,
        0x385060a0, 0x675020a0, 0x675060a0, 0x685020a0, 0x685060a0]
EPS = 0x6e21be55
ETA = 0x830303CF
TRACK_C1 = (11, 12, 20, 22)
assert rol(BETA_STAR, 12) == CM


def dp_e1(tau):
    D = ror(tau, 8)
    st = {(0, 0, ()): 1}            # (carry, carry', tracked c1 bits) -> count
    for i in range(32):
        nst = {}
        xs = [(CV >> i) & 1] if (CM >> i) & 1 else [0, 1]
        for (c, cb, tr), n in st.items():
            for x in xs:
                for y in (0, 1):
                    xb, yb = x ^ ((CM >> i) & 1), y ^ ((D >> i) & 1)
                    s, sb = x ^ y ^ c, xb ^ yb ^ cb
                    if s ^ sb != (EPS >> i) & 1:
                        continue
                    nc = (x & y) | (x & c) | (y & c)
                    ncb = (xb & yb) | (xb & cb) | (yb & cb)
                    t2 = tr + (x,) if i in TRACK_C1 else tr
                    k = (nc, ncb, t2)
                    nst[k] = nst.get(k, 0) + n
        st = nst
    cells = {}
    for (c, cb, tr), n in st.items():
        b = dict(zip(TRACK_C1, tr))
        key = (b[11] ^ b[12], b[20] ^ b[22])
        cells[key] = cells.get(key, 0) + n
    return cells


def dp_e3(target_dg1):
    st = {(0, 0, ()): 1}
    for i in range(32):
        nst = {}
        for (c, cb, tr), n in st.items():
            for x in (0, 1):            # y9 bit
                for y in (0, 1):        # h1 bit
                    yb = y ^ ((ETA >> i) & 1)
                    s, sb = x ^ y ^ c, x ^ yb ^ cb
                    if s ^ sb != (target_dg1 >> i) & 1:
                        continue
                    nc = (x & y) | (x & c) | (y & c)
                    ncb = (x & yb) | (x & cb) | (yb & cb)
                    t2 = tr + (x,) if i < 3 else tr
                    k = (nc, ncb, t2)
                    nst[k] = nst.get(k, 0) + n
        st = nst
    cells = {}
    for (c, cb, tr), n in st.items():
        cells[tr] = cells.get(tr, 0) + n
    return cells


if __name__ == '__main__':
    # sanity: the class gives e1 ^ e1b = ror(ETA, 16) ... checked on random class members
    import random
    random.seed(5)
    x = rol(ETA, 16); v = ((Y3B - Y3A) + x) & M; cm = x & 0x7FFFFFFF; cvv = ~(v >> 1) & cm & M
    bad = 0
    for _ in range(100000):
        e1 = cvv | (random.getrandbits(32) & ~cm & M)
        y4 = (e1 - Y3A) & M
        if ror(e1 ^ ((Y3B + y4) & M), 16) != ETA:
            bad += 1
    print(f'class check: h1 ^ h1b == ETA for 100000 random class members; exceptions {bad}')
    print('E1 side: (c1 in cube, d2) with eps = eps* per listed tau, by cell (c1[11]^c1[12], c1[20]^c1[22])')
    tot = {}
    for t in TAUS:
        cells = dp_e1(t)
        for k, n in cells.items():
            tot[k] = tot.get(k, 0) + n
        print(f'  tau {t:08x}: ' + '  '.join(f'{k}:{cells.get(k, 0)}' for k in product((0, 1), repeat=2)))
    print('  total       : ' + '  '.join(f'{k}:{tot.get(k, 0)}' for k in product((0, 1), repeat=2)))
    psis, code = E3L[EPS]
    print(f'E3 side: (y9, h1) with Delta f1 in the eps* list ({len(psis)} psi values), by (y9[0], y9[1], y9[2])')
    tot = {}
    for p in sorted(psis):
        cells = dp_e3(rol(p, 12))
        for k, n in cells.items():
            tot[k] = tot.get(k, 0) + n
    allk = list(product((0, 1), repeat=3))
    S = sum(tot.values())
    print('  ' + '  '.join(f'{k}:{tot.get(k, 0)} ({tot.get(k, 0) / S:.3f})' for k in allk))
    print(f'  total {S} of 2^64 = 2^{__import__("math").log2(S) - 64:.3f}')
