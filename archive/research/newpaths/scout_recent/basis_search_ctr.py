#!/usr/bin/env python3
"""Which words of a trial can be prescribed together?  (research tool, 2026-10-06 morning)

The half-collision construction has nine free words. The filed trial uses the basis
(S5, X2, X6, X9, X12, X13, X14, alpha = X10, Y4): every assignment of these nine words gives a valid message
by solving one equation at a time. This program asks for OTHER such bases: sets of nine words from which
every other word of round 0, of the column calls of round 1 and of the first halves of E1 and E3 follows by
solving single equations (each G assignment can be solved for any one of its words). A basis that contains
several of the seven residual words would prescribe them for free.

    basis_search.py T1,T2,..  [--max N] [--avoid V1,V2,..]
lists up to N bases that contain the given targets. Names: w0..w15, S0..S15, X0..X15, Y0..Y15 (Y of C0, C1,
C2 only), internals K<j>.<n>, D<j>.<n>, C<j>.<n> with n in a1 d1 c1 b1, and E1.a1 E1.d1 E1.b1 E1.a2,
E3.h1 E3.g1 E3.f1 E3.e2.
"""
import sys, itertools

import os
PINNED = {'X3', 'X7', 'X11', 'X15', 'w4', 'w13', 'w15', 'Y3', 'Y11', 'CONST'}
# further message words forced to a constant (other length pairs force zero words): PIN_EXTRA=w14,w12
PINNED |= {v for v in os.environ.get('PIN_EXTRA', '').split(',') if v}

def g_eqs(tag, ins, words, outs):
    a, b, c, d = ins; x, y = words; oa, ob, oc, od = outs
    t = lambda n: f'{tag}.{n}'
    return [(t('a1'), a, b, x), (t('d1'), d, t('a1')), (t('c1'), c, t('d1')), (t('b1'), b, t('c1')),
            (oa, t('a1'), t('b1'), y), (od, t('d1'), oa), (oc, t('c1'), od), (ob, t('b1'), oc)]

def system():
    eqs = []
    tcol = ['CONST'] * 4
    # scout_recent change: COUNTER=0 (default, as the original), 1 = the chunk counter's low word T0 is a free
    # unknown in K0's d input (a non-root chunk at index t, t < 2^32), 2 = also T1 (t's high word) in K1.
    # CVWORDS=i,j,..: these chaining-value words (v_i, i<8) are free unknowns (2-block chunk, table-backed CV).
    ctr = int(os.environ.get('COUNTER', '0'))
    cvw = {int(x) for x in os.environ.get('CVWORDS', '').split(',') if x != ''}
    for j in range(4):   # column step of round 0: inputs are constants
        a_in = f'CV{j}' if j in cvw else 'CONST'
        b_in = f'CV{4+j}' if (4 + j) in cvw else 'CONST'
        d_in = 'T0' if (j == 0 and ctr >= 1) else 'T1' if (j == 1 and ctr >= 2) else 'CONST'
        eqs += g_eqs(f'K{j}', (a_in, b_in, 'CONST', d_in), (f'w{2*j}', f'w{2*j+1}'),
                     (f'S{j}', f'S{4+j}', f'S{8+j}', f'S{12+j}'))
    diag = [(0, 5, 10, 15), (1, 6, 11, 12), (2, 7, 8, 13), (3, 4, 9, 14)]
    for j, idx in enumerate(diag):   # diagonal step of round 0
        eqs += g_eqs(f'D{j}', tuple(f'S{i}' for i in idx), (f'w{8+2*j}', f'w{9+2*j}'), tuple(f'X{i}' for i in idx))
    sched1 = [2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8]
    nopin = bool(os.environ.get('NO_PIN'))   # NO_PIN=1: plain compression, nothing pinned, all four column calls
    for j in range(4 if nopin else 3):   # column calls C0, C1, C2 of round 1 (C3 is pinned unless NO_PIN)
        idx = (j, 4 + j, 8 + j, 12 + j)
        eqs += g_eqs(f'C{j}', tuple(f'X{i}' for i in idx), (f'w{sched1[2*j]}', f'w{sched1[2*j+1]}'),
                     tuple(f'Y{i}' for i in idx))
    # first halves of E1 = G(Y1, Y6, Y11, Y12; w12, w5) and E3 = G(Y3, Y4, Y9, Y14; w15, w8)
    # HALF=A (with NO_PIN): add the last diagonal calls E0 and E2 in full and the equations "digest word fixed"
    # for digest words HALFWORDS (default 0,2,5,7: all of that half); HALF=B: E1, E3 and words 1,3,4,6.
    # A basis of that system parametrises messages that all share those digest words.
    half = os.environ.get('HALF', '')
    if nopin and half in ('A', 'B', 'AB'):
        dg = [(0, 5, 10, 15), (1, 6, 11, 12), (2, 7, 8, 13), (3, 4, 9, 14)]
        for j in ((0, 2) if half == 'A' else (1, 3) if half == 'B' else (0, 1, 2, 3)):
            eqs += g_eqs(f'E{j}', tuple(f'Y{i}' for i in dg[j]), (f'w{sched1[8 + 2*j]}', f'w{sched1[9 + 2*j]}'),
                         tuple(f'Z{i}' for i in dg[j]))
        words = [int(x) for x in os.environ.get('HALFWORDS', '0,2,5,7' if half == 'A' else '1,3,4,6').split(',') if x != '']
        for i in words:
            eqs.append((f'Z{i}', f'Z{i + 8}'))        # o[i] = Z[i] xor Z[i+8] = constant
    if not nopin:
        eqs += [('E1.a1', 'Y1', 'Y6', 'w12'), ('E1.d1', 'Y12', 'E1.a1'), ('E1.b1', 'Y6', 'E1.d1'),
                ('E1.a2', 'E1.a1', 'E1.b1', 'w5')]
        eqs += [('E3.h1', 'Y14', 'Y4'), ('E3.g1', 'Y9', 'E3.h1'), ('E3.f1', 'Y4', 'E3.g1'),
                ('E3.e2', 'Y4', 'E3.f1', 'w8')]
    pinned = {'CONST'} if nopin else PINNED
    eqs = [tuple(v for v in e if v not in pinned) for e in eqs]
    names = sorted({v for e in eqs for v in e})
    return eqs, names

def main():
    args = sys.argv[1:]
    targets = [t for t in args[0].split(',') if t] if args else []
    maxn = int(args[args.index('--max') + 1]) if '--max' in args else 20
    avoid = set(args[args.index('--avoid') + 1].split(',')) if '--avoid' in args else set()
    quiet = '--quiet' in args
    eqs, names = system()
    ix = {n: i for i, n in enumerate(names)}
    masks = [sum(1 << ix[v] for v in e) for e in eqs]
    nfree = len(names) - len(eqs)
    full = (1 << len(names)) - 1
    avoid_mask = sum(1 << ix[v] for v in avoid)

    def propagate(known, used):
        changed = True
        while changed:
            changed = False
            for k, m in enumerate(masks):
                if used >> k & 1: continue
                u = m & ~known
                if u == 0: return None
                if u & (u - 1) == 0:
                    known |= u; used |= 1 << k; changed = True
        return known, used

    found = []
    def dfs(known, used, basis, excl):
        if len(found) >= maxn: return
        if known == full:
            found.append(list(basis)); return
        if len(basis) == nfree: return
        cand = full & ~known & ~excl & ~avoid_mask
        if bin(cand).count('1') < nfree - len(basis): return
        # branch on the unknown word that occurs in the unused equation with the fewest unknown words
        best = None
        for k, m in enumerate(masks):
            if used >> k & 1: continue
            u = m & ~known
            c = u & cand
            if c and (best is None or bin(u).count('1') < best[0]): best = (bin(u).count('1'), c)
        if best is None: return
        v = best[1] & -best[1]
        r = propagate(known | v, used)
        if r is not None:
            basis.append(names[v.bit_length() - 1]); dfs(r[0], r[1], basis, excl); basis.pop()
        dfs(known, used, basis, excl | v)

    k0 = sum(1 << ix[t] for t in targets)
    r = propagate(k0, 0)
    if r is None:
        print('targets', targets, ': dependent (an equation is over-determined)'); return 1
    if '--random' in args:
        # randomized greedy completion: add random unknown words that cause no conflict; many restarts
        import random
        tries = int(args[args.index('--random') + 1]); rng = random.Random(1)
        seen = set(); stuck = 0
        for _ in range(tries):
            known, used = r; basis = list(targets)
            while known != full and len(basis) < nfree:
                cand = [i for i in range(len(names)) if not known >> i & 1 and not avoid_mask >> i & 1]
                rng.shuffle(cand)
                for i in cand:
                    q = propagate(known | 1 << i, used)
                    if q is not None:
                        known, used = q; basis.append(names[i]); break
                else:
                    break
            if known == full: seen.add(tuple(sorted(basis)))
            else: stuck += 1
        print(f'targets {targets}: {len(seen)} distinct bases in {tries} random completions ({stuck} stuck)')
        if not quiet:
            for b in sorted(seen)[:maxn]: print('  ', ' '.join(b))
        return 0
    dfs(r[0], r[1], list(targets), 0)
    print(f'{len(names)} words, {len(eqs)} equations, {nfree} free; targets {targets}: {len(found)} bases (limit {maxn})')
    if not quiet:
        for b in found[:maxn]: print('  ', ' '.join(b))
    return 0

if __name__ == '__main__':
    sys.exit(main())
