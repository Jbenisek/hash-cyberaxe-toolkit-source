#!/usr/bin/env python3
"""verify_ctr_toy.py ORDERFILE [W] [N] [SEED]  (scout_recent; research only)

Toy-width replay of a solving order from basis_sat_ctr.py (chunk counter word T0 free).  Toy BLAKE3: word size
W (default 8), rotations floor(r*W/32) of (16,12,8,7), IV = low W bits of the BLAKE3 IV, flags 3, block length 55,
counter v12 = T0 (any W-bit value is a valid chunk index), v13 = 0.  The pinned words of pin H8 have no toy
analogue, so random toy values are used for X3, X7, X11, X15, w4, w13 (w14 = w15 = 0), and Y3, Y11 are computed
from the toy C3 call so that the pins are consistent.  Checked: every solved and prescribed word equals the real
toy compression (so the arrangement is an exact parametrisation at width W; the half-collision of the 55/63 pair
needs a real toy pin and is NOT checked here).  Also counts distinct (T0, message) outputs over all 2^W values
of one basis word with the others fixed (injectivity of the parametrisation).
"""
import sys, random, re

W = int(sys.argv[2]) if len(sys.argv) > 2 else 8
N = int(sys.argv[3]) if len(sys.argv) > 3 else 2000
rng = random.Random(int(sys.argv[4]) if len(sys.argv) > 4 else 5)
M = (1 << W) - 1
RS = {16: 16 * W // 32, 12: 12 * W // 32, 8: 8 * W // 32, 7: 7 * W // 32}
IV = [x & M for x in (0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19)]
PERM = (2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8)
LEN, FLAGS = 55 & M, 3
ror = lambda v, n: ((v >> n) | (v << (W - n))) & M if n else v
rol = lambda v, n: ((v << n) | (v >> (W - n))) & M if n else v


def g(a, b, c, d, x, y):
    a1 = (a + b + x) & M; d1 = ror(d ^ a1, RS[16]); c1 = (c + d1) & M; b1 = ror(b ^ c1, RS[12])
    a2 = (a1 + b1 + y) & M; d2 = ror(d1 ^ a2, RS[8]); c2 = (c1 + d2) & M; b2 = ror(b1 ^ c2, RS[7])
    return (a1, d1, c1, b1), (a2, b2, c2, d2)


X3, X7, X11, X15, W4, W13 = (rng.randrange(1 << W) for _ in range(6))
Y3, _, Y11, _ = g(X3, X7, X11, X15, W4, W13)[1]
PIN = {'X3': X3, 'X7': X7, 'X11': X11, 'X15': X15, 'w4': W4, 'w13': W13, 'w14': 0, 'w15': 0, 'Y3': Y3, 'Y11': Y11}


def gcall(tag, A, B, C, D, x, y, oa, ob, oc, od):
    t = lambda n: f'{tag}.{n}'
    return [(t('a1'), 'ADD', (A, B, x)), (t('d1'), 16, (D, t('a1'))), (t('c1'), 'ADD', (C, t('d1'))),
            (t('b1'), 12, (B, t('c1'))), (oa, 'ADD', (t('a1'), t('b1'), y)), (od, 8, (t('d1'), oa)),
            (oc, 'ADD', (t('c1'), od)), (ob, 7, (t('b1'), oc))]


R = []
R += gcall('K0', IV[0], IV[4], IV[0], 'T0', 'w0', 'w1', 'S0', 'S4', 'S8', 'S12')
R += gcall('K1', IV[1], IV[5], IV[1], 0, 'w2', 'w3', 'S1', 'S5', 'S9', 'S13')
R += gcall('K2', IV[2], IV[6], IV[2], LEN, 'w4', 'w5', 'S2', 'S6', 'S10', 'S14')
R += gcall('K3', IV[3], IV[7], IV[3], FLAGS, 'w6', 'w7', 'S3', 'S7', 'S11', 'S15')
R += gcall('D0', 'S0', 'S5', 'S10', 'S15', 'w8', 'w9', 'X0', 'X5', 'X10', 'X15')
R += gcall('D1', 'S1', 'S6', 'S11', 'S12', 'w10', 'w11', 'X1', 'X6', 'X11', 'X12')
R += gcall('D2', 'S2', 'S7', 'S8', 'S13', 'w12', 'w13', 'X2', 'X7', 'X8', 'X13')
R += gcall('D3', 'S3', 'S4', 'S9', 'S14', 'w14', 'w15', 'X3', 'X4', 'X9', 'X14')
R += gcall('C0', 'X0', 'X4', 'X8', 'X12', 'w2', 'w6', 'Y0', 'Y4', 'Y8', 'Y12')
R += gcall('C1', 'X1', 'X5', 'X9', 'X13', 'w3', 'w10', 'Y1', 'Y5', 'Y9', 'Y13')
R += gcall('C2', 'X2', 'X6', 'X10', 'X14', 'w7', 'w0', 'Y2', 'Y6', 'Y10', 'Y14')
R += [('E1.a1', 'ADD', ('Y1', 'Y6', 'w12')), ('E1.d1', 16, ('Y12', 'E1.a1')), ('E1.c1', 'ADD', ('Y11', 'E1.d1')),
      ('E1.b1', 12, ('Y6', 'E1.c1')), ('E1.a2', 'ADD', ('E1.a1', 'E1.b1', 'w5')),
      ('E3.a1', 'ADD', ('Y3', 'Y4', 'w15')), ('E3.h1', 16, ('Y14', 'E3.a1')), ('E3.g1', 'ADD', ('Y9', 'E3.h1')),
      ('E3.f1', 12, ('Y4', 'E3.g1')), ('E3.e2', 'ADD', ('E3.a1', 'E3.f1', 'w8'))]
RED = {'E1.b1': {'E1.b1', 'Y6', 'E1.d1'}, 'E3.h1': {'E3.h1', 'Y14', 'Y4'}, 'E3.e2': {'E3.e2', 'Y4', 'E3.f1', 'w8'}}


def solve(rel, tgt, val):
    name, kind, args = rel
    gv = lambda a: a if isinstance(a, int) else val[a]
    if kind == 'ADD':
        if tgt == name: return sum(gv(a) for a in args) & M
        rest = list(args); rest.remove(tgt); return (gv(name) - sum(gv(a) for a in rest)) & M
    r = RS[kind]
    if tgt == name: return ror(gv(args[0]) ^ gv(args[1]), r)
    return rol(gv(name), r) ^ gv(args[1] if tgt == args[0] else args[0])


def helpers(val):
    if 'E1.d1' in val: val['E1.c1'] = (Y11 + val['E1.d1']) & M
    if 'Y4' in val: val['E3.a1'] = (Y3 + val['Y4']) & M


def run_order(lines, basis, bv):
    val = dict(PIN); val.update(bv); helpers(val)
    for V, deps in lines:
        need = set(deps) | {V}
        cand = [r for r in R if (RED.get(r[0]) or ({r[0]} | {a for a in r[2] if isinstance(a, str)}) - set(PIN)) == need
                and (V == r[0] or V in r[2] or (r[0] in RED and V in RED[r[0]]))]
        assert len(cand) == 1, (V, deps, cand)
        rel = cand[0]
        if rel[0] == 'E1.b1' and V == 'E1.d1':
            val['E1.c1'] = solve(rel, 'E1.c1', val); val['E1.d1'] = (val['E1.c1'] - Y11) & M
        elif rel[0] == 'E3.h1' and V == 'Y4':
            val['E3.a1'] = solve(rel, 'E3.a1', val); val['Y4'] = (val['E3.a1'] - Y3) & M
        else:
            val[V] = solve(rel, V, val)
        helpers(val)
    return val


def real(words, t):
    rec = {}; v = IV[:] + IV[:4] + [t, 0, LEN, FLAGS]; m = list(words); step = 0
    for _ in range(2):
        for half, idxs in ((0, ((0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15))),
                           (1, ((0, 5, 10, 15), (1, 6, 11, 12), (2, 7, 8, 13), (3, 4, 9, 14)))):
            tag, on = 'KDCE'[step], 'SXYZ'[step]
            for j, (a, b, c, d) in enumerate(idxs):
                (a1, d1, c1, b1), (a2, b2, c2, d2) = g(v[a], v[b], v[c], v[d], m[8 * half + 2 * j], m[8 * half + 2 * j + 1])
                rec.update({f'{tag}{j}.a1': a1, f'{tag}{j}.d1': d1, f'{tag}{j}.c1': c1, f'{tag}{j}.b1': b1})
                v[a], v[b], v[c], v[d] = a2, b2, c2, d2
            for i in range(16): rec[f'{on}{i}'] = v[i]
            step += 1
        m = [m[p] for p in PERM]
    rec.update({'E3.h1': rec['E3.d1'], 'E3.g1': rec['E3.c1'], 'E3.f1': rec['E3.b1'], 'E1.a2': rec['Z1'], 'E3.e2': rec['Z3']})
    return rec


txt = open(sys.argv[1]).read().splitlines()
basis = re.search(r'basis = ([^|]*)', txt[0]).group(1).split()
lines = [(l.split('<-')[0].replace('*', ' ').strip(), l.split('<-')[1].split()) for l in txt[1:] if '<-' in l and 'cone of' not in l]
bad = 0; checked = 0
for _ in range(N):
    val = run_order(lines, basis, {b: rng.randrange(1 << W) for b in basis})
    rec = real([val[f'w{i}'] for i in range(16)], val['T0'])
    ks = [k for k in val if k in rec]; checked = len(ks)
    bad += any(rec[k] != val[k] for k in ks)
# injectivity: vary the first basis word over all values, others fixed
fixed = {b: rng.randrange(1 << W) for b in basis}
outs = set()
for x in range(1 << W):
    fixed[basis[0]] = x
    val = run_order(lines, basis, dict(fixed))
    outs.add((val['T0'],) + tuple(val[f'w{i}'] for i in range(16)))
print(f'W={W} rotations {RS}: {N} random basis assignments, {checked} words each checked against the real toy '
      f'compression (counter = T0, flags 3): mismatches {bad}; varying {basis[0]} over 2^{W} values gives '
      f'{len(outs)} distinct (T0, message) pairs')
