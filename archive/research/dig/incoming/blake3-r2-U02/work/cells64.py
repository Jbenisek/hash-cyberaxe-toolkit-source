#!/usr/bin/env python3
"""U02 part 2: Fact P realizability of the 64 (Y3,Y11) cells (bits 18..16 of Y3 x bits 19,15,2 of Y11 around the record
8127c181/7af77f38), per-quarter stage flags, exact pin counts, and replay of constructed pins through c3()."""
import json, random
from factp import *
R = ror(0xfffffff8, 16)                      # the only compatible carry run (see factp.py)
CUB_A2, CUB_D1 = cube(D3, R), cube(D11, R)
A1S = [(0x7ffffff8 | lo | hi) & M for lo in range(8) for hi in (0, 0x80000000)]
for a in A1S:
    assert (a ^ ((a + 8) & M)) == 0xfffffff8
VS = json.load(open('structure.json'))['vs']
D1S = list(cube_iter(CUB_D1)); Y3S = list(cube_iter(CUB_A2))
assert len(A1S) == 16 and len(D1S) == 16 and len(Y3S) == 16

def stages(Y3, Y11):
    """flags per quarter + exact pin list for the cell (Y3,Y11)."""
    f = dict(q1=bool(CUB_A2 and CUB_D1), q3=Y3 in Y3S, q2=False, q4=False)
    v = Y11 ^ ((Y11 + D11) & M)
    u = rol(v, 12)
    bcub = cube((D3 - 8) & M, v)
    pins = []
    if f['q3']:
        for d1 in D1S:
            d2 = ror(d1 ^ Y3, 8); c1 = (Y11 - d2) & M
            if (c1 ^ ((c1 + D11) & M)) == u:
                f['q2'] = True
                if bcub:
                    for b1 in cube_iter(bcub):
                        for a1 in A1S:
                            w13 = (Y3 - a1 - b1) & M
                            f['q4_noW13'] = True
                            if w13 < (1 << 24):
                                f['q4'] = True; pins.append((a1, b1, c1, d1, w13))
    f.setdefault('q4_noW13', False)
    return f, pins

def pin_from(a1, b1, c1, d1, w13):
    X7 = rol(b1, 12) ^ c1; X11 = (c1 - d1) & M; X15 = rol(d1, 16) ^ a1; X3 = (a1 - X7 - W4) & M
    return X3, X7, X11, X15, w13

def replay(pin):
    X3, X7, X11, X15, w13 = pin
    A = c3(X3, X7, X11, X15, W4, w13); B = c3(X3, X7, X11, X15, W4B, w13)
    return (A['b2'] == B['b2'] and A['d2'] == B['d2'] and (B['a2'] - A['a2']) & M == D3 and (B['c2'] - A['c2']) & M == D11), A, B

base3, base11 = 0x8127c181, 0x7af77f38
cells = []
for p3 in range(8):
    Y3 = (base3 & ~0x70000) | (p3 << 16)
    for p11 in range(8):
        Y11 = base11
        for j, bit in enumerate((2, 15, 19)):
            Y11 = (Y11 & ~(1 << bit)) | (((p11 >> j) & 1) << bit)
        f, pins = stages(Y3, Y11)
        ok = f['q1'] and f['q2'] and f['q3'] and f['q4']
        nrep = 0; allok = True
        for pn in pins:
            r, A, B = replay(pin_from(*pn)); nrep += 1; allok &= r and A['a2'] == Y3 and A['c2'] == Y11
        cells.append(dict(Y3=f'{Y3:08x}', Y11=f'{Y11:08x}', flags=f, realizable=ok, n_pins=len(pins), replayed=nrep, replay_all_ok=allok))
# bit-31 flips and the full realizable set of the profile (not only the 64)
allreal = set()
for Y3 in Y3S:
    for v in VS:
        cb = cube(D11, v)
        if not cb: continue
        for Y11 in cube_iter(cb):
            f, pins = stages(Y3, Y11)
            if pins: allreal.add((Y3, Y11, len(pins)))
out = dict(cells=cells, n_real=sum(c['realizable'] for c in cells), all_realizable_profile=sorted(allreal))
json.dump(out, open('cells64.json', 'w'), indent=1)
print('cells', len(cells), 'realizable', out['n_real'])
for c in cells:
    if c['realizable']: print(c['Y3'], c['Y11'], c['n_pins'], c['replay_all_ok'])
print('all realizable (Y3,Y11,npins) over the whole profile:', len(allreal), 'distinct Y3', len({a for a, b, c in allreal}), 'distinct Y11', len({b for a, b, c in allreal}))
print('Y11 values:', sorted({hex(b) for a, b, c in allreal}))
from collections import Counter
print('failure pattern counts over 64 cells:', Counter(tuple(k for k in ('q1','q2','q3','q4') if not c['flags'][k]) for c in cells))
