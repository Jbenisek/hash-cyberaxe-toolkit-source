'''Validation of the XOR-linear model of neutral.py: in a copy of the 2-round compression with every modular addition
replaced by XOR (rotations and XORs unchanged), every kernel vector must leave all 7 held words unchanged, and random
non-kernel vectors must not.  Then the real compression (b3) on the same kernel vectors: fraction keeping the held words.'''
import random, sys
from b3 import CALLS, schedule, gname, rotr, W4, W13, point, M
from neutral import model, kernel, FREE
HELD = ['R0D3.a2', 'R0D2.b2', 'R0D1.c2', 'R0D0.d2', 'R1C0.b2', 'R1C1.c2', 'R1C2.d2']
IV = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19]
def xor_point(m, T0, T1):
    v = IV + IV[:4] + [T0, T1, 55, 3]; tr = {}
    for r, sch in enumerate(schedule(2)):
        for i, (a, b, c, d) in enumerate(CALLS):
            x, y = m[sch[i][0]], m[sch[i][1]]; n = gname(r, i)
            a1 = v[a] ^ v[b] ^ x; d1 = rotr(v[d] ^ a1, 16); c1 = v[c] ^ d1; b1 = rotr(v[b] ^ c1, 12)
            a2 = a1 ^ b1 ^ y; d2 = rotr(d1 ^ a2, 8); c2 = c1 ^ d2; b2 = rotr(b1 ^ c2, 7)
            for k, val in zip(('a2', 'b2', 'c2', 'd2'), (a2, b2, c2, d2)): tr[n + '.' + k] = val
            v[a], v[b], v[c], v[d] = a2, b2, c2, d2
    return tr
def apply(m, T0, T1, d, counter):
    m = list(m); pos = 0
    for w in FREE:
        x = (d >> pos) & M; pos += 32
        if w == 'T0': T0 ^= x
        else: m[int(w[1:])] ^= x
    if counter == 2: T1 ^= (d >> pos) & ((1 << 19) - 1)
    return m, T0, T1
rnd = random.Random(9)
for counter in (1, 2):
    n, rows, keep, e1 = model(counter); B = kernel(n, rows)
    okx = okr = bad_nonk = 0; trials = 300
    for t in range(trials):
        m = [rnd.getrandbits(32) for _ in range(16)]; m[4], m[13], m[14], m[15] = W4, W13, 0, 0
        T0, T1 = rnd.getrandbits(32), rnd.randrange(1, 1 << 19)
        d = 0
        for b in B:
            if rnd.getrandbits(1): d ^= b
        x0 = xor_point(m, T0, T1); x1 = xor_point(*apply(m, T0, T1, d, counter))
        okx += all(x0[h] == x1[h] for h in HELD)
        r0 = point(m, T0, T1); r1 = point(*apply(m, T0, T1, d, counter))
        okr += all(r0[h] == r1[h] for h in HELD)
        dn = rnd.getrandbits(n)
        if any((r & dn).bit_count() & 1 for r in rows):
            y1 = xor_point(*apply(m, T0, T1, dn, counter)); bad_nonk += all(x0[h] == y1[h] for h in HELD)
    print('counter %d: kernel dim %d | XOR-model: held words kept by %d/%d random kernel moves, by %d non-kernel moves | '
          'real compression: kept by %d/%d' % (counter, len(B), okx, trials, bad_nonk, okr, trials))
