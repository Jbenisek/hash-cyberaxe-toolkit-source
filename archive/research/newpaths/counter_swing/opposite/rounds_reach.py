"""rounds_reach.py: item (3), how far the counter's freedom reaches at 2, 2.5 and 3 rounds.

The counter t = v12 is an input of round 0's first column call K0 only (verifier line 33: v12 is set once in
the initial state and overwritten by K0). The lever moves t together with w0 and w1 along the curve
    p = K0.a1 (free),  w0 = p - IV0 - IV4,  t = ROL(K0.d1, 16) ^ p,  w1 = S0 - p - K0.b1,
which leaves the whole of round 0 unchanged (checked numerically below). After round 0, p enters only through
the message words w0 and w1.

Part A (structure): for every intermediate value of every G call of rounds 1 and 2 (a1 d1 c1 b1 a2 d2 c2 b2),
  a label: F = fixed; C = "chain": computed from p by operations each of which has exactly ONE non-fixed operand,
  so it is a bijection of p that can be inverted in closed form (any target value can be PRESCRIBED, i.e.
  generated directly, at O(1) per trial); X = mixed: two non-fixed operands meet (no closed-form prescription;
  at best a filter).
  Checked numerically on real 32-bit words: N values of p per context, number of distinct values per
  intermediate (C must give N, F must give 1, X shows collisions like a random map: about N^2 / 2^33).
Part B: which digest words (CV words 0..7) are C, F or X at 2 rounds, 2.5 rounds (rounds 0, 1 and the column
  step of round 2, then the standard output fold) and 3 rounds.
Part C: the 55/63 free half at 2, 2.5 and 3 rounds on real pairs of the arrangement (own step-wise compression,
  checked equal to the organizer copy at 2 and 3 rounds).
usage: python -B rounds_reach.py LOG2N NCTX NPAIRS SEED
"""
import random
import sys

import numpy as np

sys.dont_write_bytecode = True
import arr
import blake3_ref as V

M = 0xFFFFFFFF
IV = V.IV
PERM = V.PERMUTATION
CALLS = ((0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15),
         (0, 5, 10, 15), (1, 6, 11, 12), (2, 7, 8, 13), (3, 4, 9, 14))
NAMES = (('K0', 'K1', 'K2', 'K3'), ('D0', 'D1', 'D2', 'D3'), ('C0', 'C1', 'C2', 'C3'), ('E0', 'E1', 'E2', 'E3'),
         ('R2c0', 'R2c1', 'R2c2', 'R2c3'), ('R2d0', 'R2d1', 'R2d2', 'R2d3'))
FIELDS = ('a1', 'd1', 'c1', 'b1', 'a2', 'd2', 'c2', 'b2')


def u(x):
    return np.uint32(x)


def nror(x, n):
    return (x >> u(n)) | (x << u(32 - n))


def msg_for_step(m0, step):
    """message words used by step (0..5): round r = step // 2, columns (even) or diagonals (odd)."""
    m = list(m0)
    for _ in range(step // 2):
        m = [m[i] for i in PERM]
    return m


# ---------------- symbolic labels ----------------
def lab_op(*xs):
    """label of an operation with operands of labels xs ('F', 'C', 'X')."""
    nonfixed = [x for x in xs if x != 'F']
    if not nonfixed:
        return 'F'
    if len(nonfixed) == 1 and nonfixed[0] == 'C':
        return 'C'
    return 'X'


def g_labels(L, a, b, c, d, x, y):
    out = {}
    L[a] = lab_op(L[a], L[b], x); out['a1'] = L[a]
    L[d] = lab_op(L[d], L[a]); out['d1'] = L[d]
    L[c] = lab_op(L[c], L[d]); out['c1'] = L[c]
    L[b] = lab_op(L[b], L[c]); out['b1'] = L[b]
    L[a] = lab_op(L[a], L[b], y); out['a2'] = L[a]
    L[d] = lab_op(L[d], L[a]); out['d2'] = L[d]
    L[c] = lab_op(L[c], L[d]); out['c2'] = L[c]
    L[b] = lab_op(L[b], L[c]); out['b2'] = L[b]
    return out


def symbolic(nsteps):
    mlab = ['F'] * 16
    mlab[0] = mlab[1] = 'C'           # w0, w1 move with p; round 0 is fixed by construction
    L = ['F'] * 16                    # state after round 0 (fixed)
    rec = {}
    for step in range(2, nsteps):
        m = msg_for_step(mlab, step)
        for i in range(4):
            a, b, c, d = CALLS[4 * (step % 2) + i]
            o8 = 8 * (step % 2)
            rec[NAMES[step][i]] = g_labels(L, a, b, c, d, m[o8 + 2 * i], m[o8 + 2 * i + 1])
    outlab = [lab_op(L[i], L[i + 8]) for i in range(8)]
    return rec, outlab


# ---------------- numeric ----------------
def g_num(v, a, b, c, d, x, y, rec):
    v[a] = v[a] + v[b] + x; rec['a1'] = v[a]
    v[d] = nror(v[d] ^ v[a], 16); rec['d1'] = v[d]
    v[c] = v[c] + v[d]; rec['c1'] = v[c]
    v[b] = nror(v[b] ^ v[c], 12); rec['b1'] = v[b]
    v[a] = v[a] + v[b] + y; rec['a2'] = v[a]
    v[d] = nror(v[d] ^ v[a], 8); rec['d2'] = v[d]
    v[c] = v[c] + v[d]; rec['c2'] = v[c]
    v[b] = nror(v[b] ^ v[c], 7); rec['b2'] = v[b]


def compress_steps_np(cv, words, t_lo, t_hi, blen, flags, nsteps):
    """numpy, step-wise; words entries scalars or arrays. Returns (output 8 words, records, state after round 0)."""
    n = None
    for w in list(words) + [t_lo]:
        if isinstance(w, np.ndarray):
            n = len(w)
    full = lambda x: x if isinstance(x, np.ndarray) else np.full(n, u(x), dtype=np.uint32)
    v = [full(x) for x in list(cv) + list(IV[:4]) + [t_lo, t_hi, blen, flags]]
    words = [full(w) for w in words]
    rec = {}
    st0 = None
    with np.errstate(over='ignore'):
        for step in range(nsteps):
            m = msg_for_step(words, step)
            for i in range(4):
                a, b, c, d = CALLS[4 * (step % 2) + i]
                r = {}
                o8 = 8 * (step % 2)
                g_num(v, a, b, c, d, m[o8 + 2 * i], m[o8 + 2 * i + 1], r)
                rec[NAMES[step][i]] = r
            if step == 1:
                st0 = [x.copy() for x in v]
        out = [v[i] ^ v[i + 8] for i in range(8)]
    return out, rec, st0


def compress_steps_int(cv, words, counter, blen, flags, nsteps):
    out, _, _ = compress_steps_np(cv, [np.array([w], dtype=np.uint32) for w in words],
                                  np.array([counter & M], dtype=np.uint32), counter >> 32, blen, flags, nsteps)
    return tuple(int(x[0]) for x in out)


def part_ab(log2n, nctx, rng):
    N = 1 << log2n
    print(f'Part A/B: {nctx} random contexts of the counter arrangement, N = 2^{log2n} values of p = K0.a1 each')
    for nsteps, lab in ((4, '2 rounds'), (5, '2.5 rounds (rounds 0, 1 + round-2 columns)'), (6, '3 rounds')):
        rec_s, out_s = symbolic(nsteps)
        print(f'\n== {lab}: symbolic labels (F fixed, C chain = closed-form prescribable, X mixed) ==')
        for step in range(2, nsteps):
            for nm in NAMES[step]:
                print(f'  {nm:5s} ' + ' '.join(f'{f}:{rec_s[nm][f]}' for f in FIELDS))
        print(f'  digest (CV) words 0..7: ' + ' '.join(f'{i}:{out_s[i]}' for i in range(8)))
        cw = [f'{nm}.{f}' for step in range(2, nsteps) for nm in NAMES[step] for f in FIELDS if rec_s[nm][f] == 'C']
        last = [f'{nm}.{f}' for nm in NAMES[nsteps - 1] for f in FIELDS if rec_s[nm][f] == 'C']
        print(f'  chain words: {len(cw)}; chain words in the LAST step ({NAMES[nsteps - 1][0][:-1]}...): {last if last else "none"}')
    # numeric check (6 steps covers all records of the 4- and 5-step runs too: they are prefixes)
    rec_s6, _ = symbolic(6)
    bad_lab = 0
    worst = {}
    r0_const = 0
    for ci in range(nctx):
        o = arr.random_outer(rng)
        _, w = arr.inner(o, (arr.draw_c1(rng) - arr.Y11A) & M)
        p = np.unique(np.array([rng.getrandbits(32) for _ in range(N + N // 8)], dtype=np.uint32))[:N]
        p = p[np.random.default_rng(ci).permutation(len(p))]
        with np.errstate(over='ignore'):
            w0 = p - u(IV[0]) - u(IV[4])
            t = u(arr.rol(o['K0d1'], 16)) ^ p
            w1 = u(o['S0']) - p - u(o['K0b1'])
        words = [w0, w1] + [u(x) for x in w[2:]]
        out, rec, st0 = compress_steps_np(IV, words, t, 0, 55, 3, 6)
        r0_const += all(len(np.unique(x)) == 1 for x in st0)
        for step in range(2, 6):
            for nm in NAMES[step]:
                for f in FIELDS:
                    k = len(np.unique(rec[nm][f]))
                    L = rec_s6[nm][f]
                    ok = (L == 'F' and k == 1) or (L == 'C' and k == len(p)) or (L == 'X' and 1 < k)
                    bad_lab += not ok
                    if L == 'X':
                        worst.setdefault(f'{nm}.{f}', []).append(len(p) - k)
        if ci == 0:
            ndist = [len(np.unique(x)) for x in out]
    print(f'\nnumeric: round-0 output state constant along the curve in {r0_const}/{nctx} contexts')
    print(f'numeric: label consistency (F -> 1 value, C -> injective on N, X -> more than 1 value): '
          f'{bad_lab} inconsistencies over {nctx} contexts x {4 * 4 * 8} intermediates')
    xs = sorted(worst.items(), key=lambda kv: min(kv[1]))
    inj = [k for k, v in xs if min(v) == 0]
    print(f'numeric: X-labelled intermediates that were nevertheless injective on N in some context: {inj if inj else "none"}')
    exp = N * (N - 1) / 2 / 2 ** 32
    mean_coll = np.mean([np.mean(v) for _, v in xs])
    print(f'numeric: X-labelled intermediates, mean number of lost values (N - distinct) {mean_coll:.1f}; '
          f'a random map would lose about {exp:.1f}')


def part_c(npairs, rng):
    # self-check of the step-wise compression against the organizer copy
    ok2 = ok3 = 0
    for _ in range(50):
        w = [rng.getrandbits(32) for _ in range(16)]
        t = rng.getrandbits(40)
        ok2 += compress_steps_int(IV, w, t, 55, 3, 4) == V._compress(IV, w, t, 55, 3, 2)[:8]
        ok3 += compress_steps_int(IV, w, t, 55, 3, 6) == V._compress(IV, w, t, 55, 3, 3)[:8]
    print(f'\nPart C: own step-wise compression == organizer _compress: 2 rounds {ok2}/50, 3 rounds {ok3}/50')
    eq = {4: [0] * 8, 5: [0] * 8, 6: [0] * 8}
    half = {4: 0, 5: 0, 6: 0}
    for _ in range(npairs):
        o, ii, w, wb, t, A, B = arr.trial(rng)
        for ns in (4, 5, 6):
            a = compress_steps_int(IV, w, t, 55, 3, ns)
            b = compress_steps_int(IV, wb, t, 63, 3, ns)
            for i in range(8):
                eq[ns][i] += a[i] == b[i]
            half[ns] += all(a[i] == b[i] for i in (0, 2, 5, 7))
    for ns, lab in ((4, '2 rounds'), (5, '2.5 rounds'), (6, '3 rounds')):
        print(f'  {lab}: CV words equal (word: count of {npairs}) ' + ' '.join(f'{i}:{eq[ns][i]}' for i in range(8))
              + f'; words 0,2,5,7 all equal {half[ns]}/{npairs}')


def main():
    log2n, nctx, npairs, seed = (int(x) for x in sys.argv[1:5])
    rng = random.Random(seed)
    part_ab(log2n, nctx, rng)
    part_c(npairs, rng)


if __name__ == '__main__':
    main()
