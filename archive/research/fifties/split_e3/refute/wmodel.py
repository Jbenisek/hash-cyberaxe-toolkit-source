'''Own word-level relation model of the E3-held system, generated from the G decomposition in b3.py (no team model).
G calls kept: round 0 (8) + round-1 columns C0, C1, C2 (C3 has only pinned inputs and is constant).
Constants: IV, block length 55, flags 3, m4 = W4, m13 = W13 (pins), m14 = m15 = 0 (padding), m8 (E3 input, held),
X3 X7 X11 X15 (pins), Y4 Y9 Y14 (E3 inputs, held); T1 constant in counter 1, a word in counter 2.
Each relation is the set of its unknown words; any one of them follows from the others (add or xor-rotate step).'''
import random
from b3 import CALLS, schedule, gname, point, W4, W13, PINS, E3IN, E1IN, M
HELD = set(PINS) | {E3IN['Y4'], E3IN['Y9'], E3IN['Y14']}
def build(counter):
    const = {'m4', 'm13', 'm14', 'm15', 'm8'} | ({'T1'} if counter == 1 else set())
    sch = schedule(2)
    v = ['IV'] * 12 + ['T0', 'T1', 'LEN', 'FLAGS']
    rels = []                       # (name, [words incl. constants], kind) kind: add3 / add2 / xr
    for r in range(2):
        for i, (a, b, c, d) in enumerate(CALLS):
            if r == 1 and i >= 3: break
            n = gname(r, i); x, y = 'm%d' % sch[r][i][0], 'm%d' % sch[r][i][1]
            A, B, C, D = v[a], v[b], v[c], v[d]; w = lambda k: n + '.' + k
            rels += [(w('a1'), [w('a1'), A, B, x], 'add3'), (w('d1'), [w('d1'), D, w('a1')], 'xr16'),
                     (w('c1'), [w('c1'), C, w('d1')], 'add2'), (w('b1'), [w('b1'), B, w('c1')], 'xr12'),
                     (w('a2'), [w('a2'), w('a1'), w('b1'), y], 'add3'), (w('d2'), [w('d2'), w('d1'), w('a2')], 'xr8'),
                     (w('c2'), [w('c2'), w('c1'), w('d2')], 'add2'), (w('b2'), [w('b2'), w('b1'), w('c2')], 'xr7')]
            v[a], v[b], v[c], v[d] = w('a2'), w('b2'), w('c2'), w('d2')
    isconst = lambda s: s in ('IV', 'LEN', 'FLAGS') or s in const or s in HELD
    R = [(nm, frozenset(s for s in ws if not isconst(s)), ws, kind) for nm, ws, kind in rels]
    W = sorted(set().union(*(r[1] for r in R)))
    return R, W
def selftest(counter, n=200):
    '''every relation holds on real traces (consistency of the symbolic model with b3).'''
    R, W = build(counter); rnd = random.Random(counter); bad = 0
    for _ in range(n):
        m = [rnd.getrandbits(32) for _ in range(16)]; m[4], m[13], m[14], m[15] = W4, W13, 0, 0
        tr = point(m, rnd.getrandbits(32), rnd.getrandbits(19) if counter == 2 else 0)
        # numeric check of every relation on the trace (constants IV/LEN/FLAGS resolved from the initial state)
        st = {}
        iv = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19]
        init = iv + iv[:4] + [tr['T0'], tr['T1'], 55, 3]
        for nm, ws, full, kind in R:
            g = nm.split('.')[0]; r_, i_ = int(g[1]), (int(g[3]) + (4 if g[2] == 'D' else 0))
            vals = []
            for pos, s in enumerate(full):
                if s in tr: vals.append(tr[s])
                else:       # IV / LEN / FLAGS: an input of a round-0 column G -> initial state word
                    a, b, c, d = CALLS[i_]; k = nm.split('.')[1]
                    idx = {('a1', 1): a, ('a1', 2): b, ('c1', 1): c, ('b1', 1): b, ('d1', 1): d}[(k, pos)]
                    vals.append(init[idx])
            o, rest = vals[0], vals[1:]
            if kind.startswith('add'): ok = o == sum(rest) & M
            else:
                rr = int(kind[2:]); x = rest[0] ^ rest[1]; ok = o == ((x >> rr) | (x << (32 - rr))) & M
            bad += not ok
        for s in W: bad += s not in tr
    return R, W, bad
if __name__ == '__main__':
    for c in (1, 2):
        R, W, bad = selftest(c)
        print('counter %d: unknown words %d, relations %d, DOF %d words; names missing from b3 trace: %d' % (c, len(W), len(R), len(W) - len(R), bad))
