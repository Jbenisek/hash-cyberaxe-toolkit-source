#!/usr/bin/env python3
"""e3depth.py (hotspot; research only) - how far the logged partial E3 events of eps(beta*) get toward the E3 side of
R = 0. For a listed E1 outcome (tau, eps*) of beta*, R = 0 needs on the E3 side (DERIVED from the trial code):
  eps3 = eps*,  Delta f1 = tau ^ ror(tau, 1),  Delta g2 = tau,  Delta h2 = ror(beta* ^ eps*, 7).
The E3 side is a function of h1 and the outer words only. Prints, per record, the best listed tau and the Hamming
distance of Delta g2 and Delta h2 from their targets.
  python -B e3depth.py out/h_sub.bin [out/h_all.bin]
"""
import sys
import numpy as np
from ref import F, load, ror, rol, M, Y3A, Y3B, BETA_STAR

TAUS = [0x175020a0, 0x175060a0, 0x185020a0, 0x185060a0, 0x275020a0, 0x275060a0, 0x285020a0, 0x285060a0, 0x385020a0,
        0x385060a0, 0x675020a0, 0x675060a0, 0x685020a0, 0x685060a0]
EPS = 0x6e21be55
H2T = ror(BETA_STAR ^ EPS, 7)
hw = lambda x: bin(x).count('1')


def e3side(h1, y9, y4, w8, e1):
    e1b = (Y3B + y4) & M
    out = []
    for e, h in ((e1, h1), (e1b, ror(rol(h1, 16) ^ e1 ^ e1b, 16))):
        g1 = (y9 + h) & M; f1 = ror(y4 ^ g1, 12); e2 = (e + f1 + w8) & M; h2 = ror(h ^ e2, 8); g2 = (g1 + h2) & M
        out.append((f1, e2, h2, g2))
    (f1, e2, h2, g2), (f1b, e2b, h2b, g2b) = out
    return f1 ^ f1b, e2 ^ e2b, h2 ^ h2b, g2 ^ g2b


for path in sys.argv[1:]:
    R = load(path)
    m = ((R[:, 0] & 32) != 0) & (((R[:, 1] >> 8) & 0xFF) == 2)
    rows = R[m]
    dist = {}
    best = []
    for r in rows:
        r = [int(x) for x in r]
        y4 = (r[F['e1']] - Y3A) & M
        df1, de2, dh2, dg2 = e3side(r[F['h1']], r[F['Y9']], y4, r[F['w8']], r[F['e1']])
        assert de2 == EPS and de2 == r[F['eps3']]
        taus = [t for t in TAUS if df1 == t ^ ror(t, 1)]
        dg = min((hw(dg2 ^ t) for t in taus), default=99)
        dh = hw(dh2 ^ H2T)
        dist[(dg, dh)] = dist.get((dg, dh), 0) + 1
        best.append((dg + dh, dg, dh, len(taus)))
    print(f'== {path}: partial E3 events with eps3 = eps(beta*): {len(rows)}')
    nt = sum(1 for b in best if b[3] > 0)
    print(f'   Delta f1 = tau ^ ror(tau,1) for some listed tau of beta*: {nt} of {len(rows)}')
    print(f'   Delta h2 on target: {sum(1 for b in best if b[2] == 0)}; Delta g2 on a target tau: {sum(1 for b in best if b[1] == 0)}')
    hist = {}
    for b in best:
        hist[b[0]] = hist.get(b[0], 0) + 1
    print('   HW(Delta g2 ^ tau) + HW(Delta h2 ^ target), distribution: ' + ' '.join(f'{k}:{hist[k]}' for k in sorted(hist)))
