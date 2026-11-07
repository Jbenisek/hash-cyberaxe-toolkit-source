#!/usr/bin/env python3
"""subcube.py (hotspot; research only) - density of the listed E1 outcome over sub-cubes of the beta* cube (cells of
the free c1 bits), ranked on the discovery half, gain measured on the held-out half; plus the exact eps-only
probability per cube member (DP over d2) for comparison.
  python -B subcube.py out/h_sub.bin
"""
import sys
import numpy as np
from ref import F, load, ror, CM, CV
from analyze_hot import events, K_NULL

EPS = 0x6e21be55
TAUS = [0x175020a0, 0x175060a0, 0x185020a0, 0x185060a0, 0x275020a0, 0x275060a0, 0x285020a0, 0x285060a0, 0x385020a0,
        0x385060a0, 0x675020a0, 0x675060a0, 0x685020a0, 0x685060a0]
FREE = [b for b in range(32) if not (CM >> b) & 1]

R = load(sys.argv[1] if len(sys.argv) > 1 else 'out/h_sub.bin')
EV = events(R)
null = (R[:, 0] & K_NULL) != 0
half = (R[:, F['tid']] & 1).astype(bool)
c1 = R[:, F['c1']]
par = (((c1 >> 11) ^ (c1 >> 12)) & 1) & (((c1 >> 20) ^ (c1 >> 22)) & 1)
for lab, bits in (('high free bits 23,24,28-31 (64 cells)', [23, 24, 28, 29, 30, 31]),
                  ('low free bits 2,4,5,6,9,10 (64 cells)', [2, 4, 5, 6, 9, 10]),
                  ('mid free bits 13,14,17,18,21 (32 cells)', [13, 14, 17, 18, 21])):
    cell = np.zeros(len(R), np.int64)
    for k, b in enumerate(bits):
        cell |= (((c1 >> np.uint32(b)) & np.uint32(1)).astype(np.int64)) << k
    nc = 1 << len(bits)
    m = EV['listed E1 outcome']
    # discovery ranking among parity-satisfying members (the parities are already a hot spot)
    dn = np.bincount(cell[m & ~half], minlength=nc) / max((m & ~half).sum(), 1)
    nn = np.bincount(cell[null & ~half & (par == 1)], minlength=nc) / max((null & ~half & (par == 1)).sum(), 1)
    dens = np.where(nn > 0, dn / np.maximum(nn, 1e-12), 0)
    order = np.argsort(-dens)
    hn = np.bincount(cell[null & half & (par == 1)], minlength=nc) / max((null & half & (par == 1)).sum(), 1)
    he = np.bincount(cell[m & half], minlength=nc) / max((m & half).sum(), 1)
    out = []
    for q in (1 / 2, 1 / 4, 1 / 8):
        k = max(1, int(round(q * nc)))
        sel = order[:k]
        out.append(f'keep {k}/{nc} cells: fraction {hn[sel].sum():.3f}, events {he[sel].sum():.3f}, gain x{he[sel].sum() / hn[sel].sum():.2f}')
    chi = ((np.bincount(cell[m], minlength=nc) - m.sum() * np.bincount(cell[null & (par == 1)], minlength=nc) / (null & (par == 1)).sum()) ** 2
           / np.maximum(m.sum() * np.bincount(cell[null & (par == 1)], minlength=nc) / (null & (par == 1)).sum(), 1e-9)).sum()
    print(f'E1 outcome over c1 {lab}, within the two parities: chi2 {chi:.0f} on {nc - 1}; held-out: ' + '; '.join(out))

# exact eps-only probability per cube member: P_d2[eps = eps* for some listed tau], vectorised DP over d2
free_vals = np.arange(2 ** 21, dtype=np.uint64)
cv = np.full(2 ** 21, CV, dtype=np.uint64)
for k, b in enumerate(FREE):
    cv |= ((free_vals >> np.uint64(k)) & np.uint64(1)) << np.uint64(b)
tot = np.zeros(2 ** 21)
for tau in TAUS:
    D = ror(tau, 8)
    cnt = np.zeros((2 ** 21, 4)); cnt[:, 0] = 1.0
    for i in range(32):
        x = ((cv >> np.uint64(i)) & np.uint64(1)).astype(np.int64)
        xb = x ^ ((CM >> i) & 1)
        new = np.zeros_like(cnt)
        for c in (0, 1):
            for cb in (0, 1):
                src = cnt[:, 2 * c + cb]
                for y in (0, 1):
                    yb = y ^ ((D >> i) & 1)
                    ok = ((x ^ y ^ c) ^ (xb ^ yb ^ cb)) == ((EPS >> i) & 1)
                    nc_ = (x & y) | (x & c) | (y & c)
                    ncb = (xb & yb) | (xb & cb) | (yb & cb)
                    d = 2 * nc_ + ncb
                    for dv in range(4):
                        mm = ok & (d == dv)
                        new[mm, dv] += src[mm]
        cnt = new
    tot += cnt.sum(1) / 2.0 ** 32
p = tot
pp = ((((cv >> np.uint64(11)) ^ (cv >> np.uint64(12))) & np.uint64(1)) == 1)
print(f'eps-only exact probability over the cube: mean 2^{np.log2(p.mean()):.3f}; zero for {(p == 0).mean():.3f} of members;'
      f' all zero members have c1[11]=c1[12]: {bool(((p == 0) == ~pp).all())}')
srt = np.sort(p)[::-1]
print('   keep best q of cube members by eps-only probability -> gain on the eps condition: ' +
      ' '.join(f'1/{int(1 / q)}:x{srt[:int(q * len(srt))].mean() / p.mean():.2f}' for q in (1 / 2, 1 / 4, 1 / 8, 1 / 16, 1 / 64)))
# does the eps-only score predict the real E1 outcome (held-out)?
idx = np.zeros(len(R), np.int64)
for k, b in enumerate(FREE):
    idx |= (((c1 >> np.uint32(b)) & np.uint32(1)).astype(np.int64)) << k
s = p[idx]
m = EV['listed E1 outcome']
sn = np.sort(s[null])
line = []
for q in (1 / 2, 1 / 4, 1 / 8, 1 / 16):
    thr = sn[int((1 - q) * len(sn))]
    qq = (s[null] >= thr).mean()
    line.append(f'q {qq:.3f}: x{(s[m] >= thr).mean() / qq:.2f}')
print('   real listed E1 outcomes (all data) kept by the eps-only score: ' + '; '.join(line))
