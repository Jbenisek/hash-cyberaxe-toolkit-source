#!/usr/bin/env python3
"""verify_ctr.py ORDERFILE [N] [SEED]  (scout_recent, 2026-10-08; research only)

End-to-end check, at the real width (32 bits), of a solving order found by basis_sat_ctr.py with the chunk
counter word T0 free (COUNTER=1) and pin H8 (PIN_EXTRA=w14).  For N random assignments of the basis words
(Y4 drawn from the H8 eta class) it solves every line of the order, builds the two messages A (55 bytes) and
B (63 bytes) of the H8 length pair, and runs the REAL 2-round compression of a non-root single-block chunk at
chunk index t = T0 (counter v12 = T0, v13 = 0, flags CHUNK_START|CHUNK_END = 3).  Checked per assignment:
  (1) every solved/prescribed word equals its value in the real computation of A (all 105 words);
  (2) digest words 0, 2, 5, 7 of A and B agree (the half-collision of the filed path);
  (3) T0 < 2^32 (so the chunk index fits a message shorter than 2^42 bytes).
Pins and constants are copied from research\\h8\\design\\h8_ref.py (read only).
"""
import sys, random, re

MASK = 0xFFFFFFFF
IV = (0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19)
PERM = (2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8)
LEN_A, LEN_B, FLAGS = 55, 63, 3          # non-root chunk: CHUNK_START | CHUNK_END, no ROOT
X3, X7, X11, X15 = 0x29D4FA98, 0xBEE3AF28, 0x44036000, 0x40C58500
W4, W13 = 0x97475638, 0x0007C006
K = (IV[2] + IV[6]) & MASK
W4B = ((((K + W4) & MASK) ^ (LEN_A ^ LEN_B)) - K) & MASK
DELTA = (W4 - W4B) & MASK
ETA = 0x830303CF
ror = lambda v, n: ((v >> n) | (v << (32 - n))) & MASK
rol = lambda v, n: ((v << n) | (v >> (32 - n))) & MASK


def g(a, b, c, d, x, y):
    a1 = (a + b + x) & MASK; d1 = ror(d ^ a1, 16); c1 = (c + d1) & MASK; b1 = ror(b ^ c1, 12)
    a2 = (a1 + b1 + y) & MASK; d2 = ror(d1 ^ a2, 8); c2 = (c1 + d2) & MASK; b2 = ror(b1 ^ c2, 7)
    return (a1, d1, c1, b1), (a2, b2, c2, d2)


Y3A, _, Y11A, _ = g(X3, X7, X11, X15, W4, W13)[1]
PIN = {'X3': X3, 'X7': X7, 'X11': X11, 'X15': X15, 'w4': W4, 'w13': W13, 'w14': 0, 'w15': 0,
       'Y3': Y3A, 'Y11': Y11A}

# eta class of Y4 (copied logic of h8_ref.class_mask_value)
_Y3B = g(X3, X7, X11, X15, W4B, W13)[1][0]
_x = rol(ETA, 16); _v = (((_Y3B - Y3A) & MASK) + _x) & MASK
CMASK = _x & 0x7FFFFFFF; CVAL = ~(_v >> 1) & CMASK
CFREE = [i for i in range(32) if not CMASK >> i & 1]


def class_member(k):
    e1 = CVAL
    for j, i in enumerate(CFREE): e1 |= (k >> j & 1) << i
    return (e1 - Y3A) & MASK


# ---- relations: (name, kind, args); kind: ADD3, ADD2, R16, R12, R8, R7 (z = ror(p ^ q, r)) -------------
def gcall(tag, A, B, C, D, x, y, oa, ob, oc, od):
    t = lambda n: f'{tag}.{n}'
    return [(t('a1'), 'ADD3', (A, B, x)), (t('d1'), 'R16', (D, t('a1'))), (t('c1'), 'ADD2', (C, t('d1'))),
            (t('b1'), 'R12', (B, t('c1'))), (oa, 'ADD3', (t('a1'), t('b1'), y)), (od, 'R8', (t('d1'), oa)),
            (oc, 'ADD2', (t('c1'), od)), (ob, 'R7', (t('b1'), oc))]


def relations():
    R = []
    R += gcall('K0', IV[0], IV[4], IV[0], 'T0', 'w0', 'w1', 'S0', 'S4', 'S8', 'S12')
    R += gcall('K1', IV[1], IV[5], IV[1], 0, 'w2', 'w3', 'S1', 'S5', 'S9', 'S13')
    R += gcall('K2', IV[2], IV[6], IV[2], LEN_A, 'w4', 'w5', 'S2', 'S6', 'S10', 'S14')
    R += gcall('K3', IV[3], IV[7], IV[3], FLAGS, 'w6', 'w7', 'S3', 'S7', 'S11', 'S15')
    R += gcall('D0', 'S0', 'S5', 'S10', 'S15', 'w8', 'w9', 'X0', 'X5', 'X10', 'X15')
    R += gcall('D1', 'S1', 'S6', 'S11', 'S12', 'w10', 'w11', 'X1', 'X6', 'X11', 'X12')
    R += gcall('D2', 'S2', 'S7', 'S8', 'S13', 'w12', 'w13', 'X2', 'X7', 'X8', 'X13')
    R += gcall('D3', 'S3', 'S4', 'S9', 'S14', 'w14', 'w15', 'X3', 'X4', 'X9', 'X14')
    R += gcall('C0', 'X0', 'X4', 'X8', 'X12', 'w2', 'w6', 'Y0', 'Y4', 'Y8', 'Y12')
    R += gcall('C1', 'X1', 'X5', 'X9', 'X13', 'w3', 'w10', 'Y1', 'Y5', 'Y9', 'Y13')
    R += gcall('C2', 'X2', 'X6', 'X10', 'X14', 'w7', 'w0', 'Y2', 'Y6', 'Y10', 'Y14')
    # E1 = G(Y1, Y6, Y11, Y12; w12, w5), E3 = G(Y3, Y4, Y9, Y14; w15, w8): first halves, with the internal
    # helper words E1.c1 = Y11 + E1.d1 and E3.a1 = Y3 + Y4 + w15 written out
    R += [('E1.a1', 'ADD3', ('Y1', 'Y6', 'w12')), ('E1.d1', 'R16', ('Y12', 'E1.a1')),
          ('E1.c1', 'ADD2', ('Y11', 'E1.d1')), ('E1.b1', 'R12', ('Y6', 'E1.c1')),
          ('E1.a2', 'ADD3', ('E1.a1', 'E1.b1', 'w5')),
          ('E3.a1', 'ADD3', ('Y3', 'Y4', 'w15')), ('E3.h1', 'R16', ('Y14', 'E3.a1')),
          ('E3.g1', 'ADD2', ('Y9', 'E3.h1')), ('E3.f1', 'R12', ('Y4', 'E3.g1')),
          ('E3.e2', 'ADD3', ('E3.a1', 'E3.f1', 'w8'))]
    return R


RELS = relations()
ROT = {'R16': 16, 'R12': 12, 'R8': 8, 'R7': 7}


def words_of(rel):
    return {rel[0]} | {a for a in rel[2] if isinstance(a, str)}


def solve_rel(rel, target, val):
    name, kind, args = rel
    gv = lambda a: a if isinstance(a, int) else val[a]
    if kind in ('ADD3', 'ADD2'):
        if target == name: return sum(gv(a) for a in args) & MASK
        rest = list(args); rest.remove(target)
        return (gv(name) - sum(gv(a) for a in rest)) & MASK
    r = ROT[kind]
    if target == name: return ror(gv(args[0]) ^ gv(args[1]), r)
    other = args[1] if target == args[0] else args[0]
    return rol(gv(name), r) ^ gv(other)


def expand(val):
    """helper words used by the reduced E-relations of basis_search (not in its word list)"""
    if 'E1.d1' in val and 'E1.c1' not in val: val['E1.c1'] = (Y11A + val['E1.d1']) & MASK
    if 'Y4' in val and 'E3.a1' not in val: val['E3.a1'] = (Y3A + val['Y4'] + 0) & MASK


def solve_order(lines, basis, rng):
    val = dict(PIN)
    for b in basis:
        val[b] = class_member(rng.randrange(1 << len(CFREE))) if b == 'Y4' else rng.randrange(1 << 32)
    expand(val)
    for V, deps in lines:
        # basis_search reduced E1.b1 (Y6, E1.d1) and E3.* through pinned words: map them to our relations
        cand = []
        need = set(deps) | {V}
        for rel in RELS:
            ws = {w for w in words_of(rel) if w not in PIN}
            ws_red = set(ws)
            if rel[0] == 'E1.b1': ws_red = {'E1.b1', 'Y6', 'E1.d1'}
            if rel[0] == 'E3.h1': ws_red = {'E3.h1', 'Y14', 'Y4'}
            if rel[0] == 'E3.e2': ws_red = {'E3.e2', 'Y4', 'E3.f1', 'w8'}
            if ws_red == need and (V == rel[0] or V in rel[2]): cand.append(rel)
        assert len(cand) == 1, (V, deps, cand)
        rel = cand[0]
        tgt = V
        if rel[0] == 'E1.b1' and V == 'E1.d1':
            val['E1.c1'] = solve_rel(rel, 'E1.c1', val); val['E1.d1'] = (val['E1.c1'] - Y11A) & MASK; continue
        if rel[0] == 'E1.b1' and V == 'Y6' and 'E1.c1' not in val:
            val['E1.c1'] = (Y11A + val['E1.d1']) & MASK
        if rel[0] == 'E3.h1' and V == 'Y4':
            val['E3.a1'] = solve_rel(rel, 'E3.a1', val); val['Y4'] = (val['E3.a1'] - Y3A) & MASK; continue
        if rel[0] == 'E3.h1' and V == 'Y14':
            val['E3.a1'] = (Y3A + val['Y4']) & MASK
        if rel[0] == 'E3.e2' and V != 'E3.e2':
            val['E3.a1'] = (Y3A + val['Y4']) & MASK
        val[tgt] = solve_rel(rel, tgt, val)
        expand(val)
    return val


def real_run(words, t, n):
    """real 2-round compression, recording every internal word under the names of relations()"""
    rec = {}
    v = list(IV) + list(IV[:4]) + [t & MASK, t >> 32, n, FLAGS]
    m = list(words)
    names = [('K', 'S', 'w'), ('D', 'X', None), ('C', 'Y', None), ('E', 'Z', None)]
    cols = ((0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15))
    diag = ((0, 5, 10, 15), (1, 6, 11, 12), (2, 7, 8, 13), (3, 4, 9, 14))
    step = 0
    for r in range(2):
        for half, idxs in ((0, cols), (1, diag)):
            tag = 'KDCE'[step]; outn = 'SXYZ'[step]
            for j, (a, b, c, d) in enumerate(idxs):
                (a1, d1, c1, b1), (a2, b2, c2, d2) = g(v[a], v[b], v[c], v[d], m[2 * (4 * half + j)], m[2 * (4 * half + j) + 1])
                rec.update({f'{tag}{j}.a1': a1, f'{tag}{j}.d1': d1, f'{tag}{j}.c1': c1, f'{tag}{j}.b1': b1})
                v[a], v[b], v[c], v[d] = a2, b2, c2, d2
            for i in range(16): rec[f'{outn}{i}'] = v[i]
            step += 1
        m = [m[p] for p in PERM]
    # E3's first half uses helper names of relations()
    rec['E3.h1'] = rec['E3.d1']; rec['E3.g1'] = rec['E3.c1']; rec['E3.f1'] = rec['E3.b1']
    rec['E1.a2'] = rec['Z1']; rec['E3.e2'] = rec['Z3']
    return rec, [v[i] ^ v[i + 8] for i in range(8)]


def main():
    path = sys.argv[1]; N = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
    rng = random.Random(int(sys.argv[3]) if len(sys.argv) > 3 else 1)
    txt = open(path).read().splitlines()
    basis = re.search(r'basis = ([^|]*)', txt[0]).group(1).split()
    lines = []
    for ln in txt[1:]:
        if '<-' not in ln or 'cone of' in ln: continue
        left, right = ln.replace('*', ' ').split('<-')
        lines.append((left.strip(), right.split()))
    bad1 = bad2 = bad3 = 0; tmax = 0
    for it in range(N):
        val = solve_order(lines, basis, rng)
        wA = [val[f'w{i}'] for i in range(16)]
        t = val['T0']
        wB = list(wA); wB[4] = W4B; wB[5] = (wA[5] + DELTA) & MASK
        recA, dA = real_run(wA, t, LEN_A)
        _, dB = real_run(wB, t, LEN_B)
        mism = [k for k in val if k in recA and recA[k] != val[k]]
        if mism: bad1 += 1
        if any(dA[i] != dB[i] for i in (0, 2, 5, 7)): bad2 += 1
        if not 0 <= t < 1 << 32: bad3 += 1
        tmax = max(tmax, t)
        if it == 0:
            checked = [k for k in val if k in recA]
            print(f'basis {basis}; words checked against the real run: {len(checked)}; prescribed '
                  f'{[b for b in basis if b in ("Y4", "E1.d1", "E3.h1", "E3.g1", "E3.e2", "Y14", "Y6")]}')
            print(f'example: T0 = {t:#010x}, w = {" ".join(f"{x:08x}" for x in wA)}')
            if mism: print('  first mismatches:', mism[:8])
    print(f'{N} assignments: internal-word mismatches {bad1}, half-collision (0,2,5,7) failures {bad2}, '
          f'counter out of range {bad3}; largest T0 {tmax:#x}')


if __name__ == '__main__':
    main()
