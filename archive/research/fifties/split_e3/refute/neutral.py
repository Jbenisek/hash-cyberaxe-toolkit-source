'''Bit-level, basis-free test for cheap E3-holding moves (neutral bits), on the own model (b3.py).
Free input bits: T0, m0 m1 m2 m3 m5 m6 m7 m9 m10 m11 m12 (12 words = 384 bits) and, for counter 2, T1 bits 0..18.
Held: pins X3 X7 X11 X15 and E3 inputs Y4 Y9 Y14 (224 bits); m4 m13 m8 m14 m15 are constants (no difference).
XOR-linear model: every modular addition replaced by XOR (rotations and XORs are exact).  A move delta keeps every held
word exactly when it is in the kernel of the held-word map AND every addition that feeds a held word behaves linearly;
for z = x + y with input XOR differences (alpha, beta) that has probability 2^-wt((alpha|beta) & 0x7fffffff).
Code: for each such addition and bit i < 31 the coordinates (alpha_i, beta_i, alpha_i ^ beta_i); a codeword's Hamming
weight is then exactly 2 x its trail cost.  Low-weight codewords are searched by information-set decoding (random
information sets, Lee-Brickell p <= 2).  A move must also change E1's inputs (Y1 Y6 Y12 m12 m5).
usage: python neutral.py <counter> <iterations> <seed>'''
import sys, random, time
from b3 import CALLS, schedule, gname, W4, W13
FREE = ['T0', 'm0', 'm1', 'm2', 'm3', 'm5', 'm6', 'm7', 'm9', 'm10', 'm11', 'm12']
def rotr_v(x, r): return [x[(i + r) % 32] for i in range(32)]      # bit i of rotr(x,r) is bit i+r of x
def xor_v(*xs):
    out = [0] * 32
    for x in xs:
        for i in range(32): out[i] ^= x[i]
    return out
def model(counter):
    '''returns n, held rows (list of ints over input bits), addition blocks [(name, alpha_vec, beta_vec)], E1 rows'''
    inputs = [(w, 32) for w in FREE] + ([('T1', 19)] if counter == 2 else [])
    n = 0; word = {}
    for w, nb in inputs:
        word[w] = [(1 << (n + i)) if i < nb else 0 for i in range(32)]; n += nb
    Z = [0] * 32
    for w in ('m4', 'm13', 'm14', 'm15', 'm8'): word[w] = Z
    if counter == 1: word['T1'] = Z
    v = [Z] * 12 + [word['T0'], word['T1'], Z, Z]
    sch = schedule(2); adds = []; tr = {}
    for r in range(2):
        for i, (a, b, c, d) in enumerate(CALLS):
            if r == 1 and i >= 4: break
            n_ = gname(r, i); x, y = word['m%d' % sch[r][i][0]], word['m%d' % sch[r][i][1]]
            A, B, C, D = v[a], v[b], v[c], v[d]
            ab = xor_v(A, B); adds.append((n_ + '.a1s', A, B)); a1 = xor_v(ab, x); adds.append((n_ + '.a1', ab, x))
            d1 = rotr_v(xor_v(D, a1), 16); c1 = xor_v(C, d1); adds.append((n_ + '.c1', C, d1))
            b1 = rotr_v(xor_v(B, c1), 12)
            s = xor_v(a1, b1); adds.append((n_ + '.a2s', a1, b1)); a2 = xor_v(s, y); adds.append((n_ + '.a2', s, y))
            d2 = rotr_v(xor_v(d1, a2), 8); c2 = xor_v(c1, d2); adds.append((n_ + '.c2', c1, d2)); b2 = rotr_v(xor_v(b1, c2), 7)
            for k, val in zip(('a2', 'b2', 'c2', 'd2'), (a2, b2, c2, d2)): tr[n_ + '.' + k] = val
            v[a], v[b], v[c], v[d] = a2, b2, c2, d2
    held = ['R0D3.a2', 'R0D2.b2', 'R0D1.c2', 'R0D0.d2', 'R1C0.b2', 'R1C1.c2', 'R1C2.d2']
    rows = [x for h in held for x in tr[h]]
    # additions that feed a held word: all of round 0, round-1 C0 and C1; C2 except its c2 (feeds only Y10, Y6); not C3
    keep = [ad for ad in adds if ad[0].startswith('R0') or ad[0].startswith('R1C0') or ad[0].startswith('R1C1')
            or (ad[0].startswith('R1C2') and not ad[0].endswith('.c2'))]
    e1 = tr['R1C1.a2'] + tr['R1C2.b2'] + tr['R1C0.d2'] + word['m12'] + word['m5']
    return n, rows, keep, e1
def kernel(n, rows):
    '''basis of {d : <row, d> = 0 for all rows} over GF(2), ints over n bits'''
    piv = {}                                  # pivot bit -> reduced row
    for r in rows:
        for p, pr in piv.items():
            if r >> p & 1: r ^= pr
        if r:
            p = r.bit_length() - 1
            for q in list(piv):
                if piv[q] >> p & 1: piv[q] ^= r
            piv[p] = r
    free = [i for i in range(n) if i not in piv]
    basis = []
    for f in free:
        d = 1 << f
        for p, pr in piv.items():
            if pr >> f & 1: d |= 1 << p
        basis.append(d)
    return basis
def dot(a, b): return (a & b).bit_count() & 1
def codeword(d, keep):
    cw = 0; pos = 0
    for _, al, be in keep:
        for i in range(31):
            x, y = dot(al[i], d), dot(be[i], d)
            cw |= (x << pos) | (y << (pos + 1)) | ((x ^ y) << (pos + 2)); pos += 3
    return cw
if __name__ == '__main__':
    counter, iters, seed = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    t0 = time.time()
    n, rows, keep, e1 = model(counter)
    B = kernel(n, rows)
    assert all(dot(r, d) == 0 for r in rows for d in B)
    N = 93 * len(keep)
    print('counter %d: input bits %d, held bits %d (rank %d), kernel dim %d, cost additions %d, code length %d' %
          (counter, n, len(rows), n - len(B), len(B), len(keep), N))
    import numpy as np
    d0 = len(B)
    CW = [codeword(d, keep) for d in B]
    G = np.array([[cw >> j & 1 for j in range(N)] for cw in CW], dtype=np.uint8)
    D = np.array([[d >> j & 1 for j in range(n)] for d in B], dtype=np.uint8)
    E1M = np.array([[r >> j & 1 for j in range(n)] for r in e1], dtype=np.uint8)      # E1 rows over input bits
    POP = np.array([bin(i).count('1') for i in range(256)], dtype=np.int32)
    rnd = np.random.default_rng(seed); best = {}
    def todelta(drow): return sum(1 << j for j in np.nonzero(drow)[0])
    def consider(cwrows, drows):
        w = POP[np.packbits(cwrows, axis=1)].sum(axis=1) // 2
        ch = (drows @ E1M.T % 2).any(axis=1)
        for flag in (True, False):
            sel = np.nonzero(ch == flag)[0]
            if len(sel) == 0: continue
            i = sel[np.argmin(w[sel])]
            if (flag not in best) or w[i] < best[flag][0]: best[flag] = (int(w[i]), todelta(drows[i]))
    for it in range(iters):
        cols = rnd.permutation(N); Mx = G.copy(); Dx = D.copy(); r = 0
        for c in cols:
            if r == d0: break
            nz = np.nonzero(Mx[r:, c])[0]
            if len(nz) == 0: continue
            p = r + nz[0]
            if p != r: Mx[[r, p]] = Mx[[p, r]]; Dx[[r, p]] = Dx[[p, r]]
            hit = np.nonzero(Mx[:, c])[0]; hit = hit[hit != r]
            Mx[hit] ^= Mx[r]; Dx[hit] ^= Dx[r]; r += 1
        consider(Mx, Dx)
        iu, ju = np.triu_indices(d0, 1)
        for s in range(0, len(iu), 4096):
            consider(Mx[iu[s:s+4096]] ^ Mx[ju[s:s+4096]], Dx[iu[s:s+4096]] ^ Dx[ju[s:s+4096]])
        if it % 10 == 0 or it == iters - 1:
            print('iter %d  %.0fs  min trail cost: moves changing E1 %s, moves not changing E1 %s' %
                  (it, time.time() - t0, best.get(True, (None,))[0], best.get(False, (None,))[0])); sys.stdout.flush()
    best = {(w, ch): d for ch, (w, d) in best.items()}
    for ch in (True, False):
        ws = sorted(w for w, c in best if c == ch)[:5]
        for w in ws:
            d = best[(w, ch)]
            names = []; pos = 0
            for word, nb in [(x, 32) for x in FREE] + ([('T1', 19)] if counter == 2 else []):
                m = (d >> pos) & ((1 << nb) - 1)
                if m: names.append('%s^%08x' % (word, m))
                pos += nb
            print('cost %d  E1 changes %s  move %s' % (w, ch, ' '.join(names)))
