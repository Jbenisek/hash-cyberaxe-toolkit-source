#!/usr/bin/env python3
"""b3-misc/split.py -- cell const x join (GAPS item 5).

Question: can extra constants (one more pinned word, or any set of them) split
the front-line system so that E1's inputs and E3's inputs range independently
(a Cartesian product, so a list join on the 128-bit residual becomes possible)?

Method (word level, structural = generic counting, the guess-and-determine model):
  * Trace the reference 2-round compression (verifier/blake3.py) into word
    relations: each G call = 8 relations (a1=a+b+x, d1=ror(d^a1,16), c1=c+d1,
    b1=ror(b^c1,12), a2=a1+b1+y, d2=ror(d1^a2,8), c2=c1+d2, b2=ror(b1^c2,7)).
    Every relation is solvable for any one of its words given the others.
    The trace is checked against blake3._compress on random inputs.
  * System = round 0 (K0..K3, D0..D3) + round-1 columns (C0..C3).
    Fixed: init state, w4, w13, w14, w15, pins X3, X7, X11, X15; words forced by
    the fixed ones are propagated (so C3 is constant, as in the map).
  * Terminals: E1 inputs {Y1, Y6, Y12, w12, w5}; E3 inputs {Y4, Y9, Y14, w8}
    (Y3, Y11, w15 are constants).
  * A split labels every free word U (E1 side), V (E3 side) or S (constant /
    separator) and every relation U, V or S, with no relation touching both U
    and V. Structural dimensions: d_X = #words_X - #relations_X.
    d_U + d_V + d_S = dim (8 at the root, 9 with t_lo free, 10 with t free).
    The exact optimum over ALL labelings (so over every choice of extra
    constants) is found by an ILP (scipy milp / HiGHS).
  * Join cost floor: lists of L <= 2^(32*min(d_U,d_V)) per separator value,
    2^128/L^2 separator values -> at least 2^129/L list entries.
"""

# Publication path adapter: resolve data paths from the extracted source tree.
def _hca_public_path_text(value):
    if "__HCA_WORKSPACE__/" not in value:
        return value
    import os as _hca_os
    from pathlib import Path as _hca_Path
    root = _hca_os.environ.get("HASHCYBERAXE_WORKSPACE")
    if root is None:
        here = _hca_Path(__file__).resolve().parent
        root = next((str(p) for p in (here, *here.parents) if (p / "research").is_dir()), None)
    if root is None:
        raise FileNotFoundError("Extract the research source tree, or set HASHCYBERAXE_WORKSPACE to its archive directory.")
    return value.replace("__HCA_WORKSPACE__/", str(_hca_Path(root).resolve()).replace("\\", "/") + "/")

import sys, random, json, time
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/hash-smash/verifier'))
import blake3 as B
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds
from scipy.sparse import coo_matrix

MASK = 0xFFFFFFFF
OUT = _hca_public_path_text('__HCA_WORKSPACE__/research/newpaths/untried/b3-misc')


def ror(x, n):
    return ((x >> n) | (x << (32 - n))) & MASK


class Trace:
    def __init__(self):
        self.name, self.val, self.rel = [], [], []   # rel: (call, kind, ids)
        self.alias = {}

    def word(self, name, val):
        self.name.append(name)
        self.val.append(val & MASK)
        return len(self.name) - 1


def G(T, v, a, b, c, d, xi, yi, tag):
    va, vb, vc, vd = (T.val[v[k]] for k in (a, b, c, d))
    x, y = T.val[xi], T.val[yi]
    a1 = (va + vb + x) & MASK; A1 = T.word(tag + '.a1', a1); T.rel.append((tag, 'add3', (v[a], v[b], xi, A1)))
    d1 = ror(vd ^ a1, 16);     D1 = T.word(tag + '.d1', d1); T.rel.append((tag, 'xr16', (v[d], A1, D1)))
    c1 = (vc + d1) & MASK;     C1 = T.word(tag + '.c1', c1); T.rel.append((tag, 'add', (v[c], D1, C1)))
    b1 = ror(vb ^ c1, 12);     B1 = T.word(tag + '.b1', b1); T.rel.append((tag, 'xr12', (v[b], C1, B1)))
    a2 = (a1 + b1 + y) & MASK; A2 = T.word(tag + '.a2', a2); T.rel.append((tag, 'add3', (A1, B1, yi, A2)))
    d2 = ror(d1 ^ a2, 8);      D2 = T.word(tag + '.d2', d2); T.rel.append((tag, 'xr8', (D1, A2, D2)))
    c2 = (c1 + d2) & MASK;     C2 = T.word(tag + '.c2', c2); T.rel.append((tag, 'add', (C1, D2, C2)))
    b2 = ror(b1 ^ c2, 7);      B2 = T.word(tag + '.b2', b2); T.rel.append((tag, 'xr7', (B1, C2, B2)))
    v[a], v[b], v[c], v[d] = A2, B2, C2, D2


COLS = [(0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15)]
DIAG = [(0, 5, 10, 15), (1, 6, 11, 12), (2, 7, 8, 13), (3, 4, 9, 14)]


def traced_compress(words, counter, block_len, flags, rounds=2):
    T = Trace()
    init = list(B.IV) + list(B.IV[:4]) + [counter & MASK, counter >> 32, block_len, flags]
    v = [T.word('v%d' % i, init[i]) for i in range(16)]
    m = [T.word('w%d' % i, words[i]) for i in range(16)]
    msg = m[:]
    states = {}
    for r in range(rounds):
        cn, dn = ('K', 'D') if r == 0 else ('C', 'E')
        for j, (a, b, c, d) in enumerate(COLS):
            G(T, v, a, b, c, d, msg[2 * j], msg[2 * j + 1], '%s%d' % (cn, j))
        states['S' if r == 0 else 'Y'] = v[:]
        for j, (a, b, c, d) in enumerate(DIAG):
            G(T, v, a, b, c, d, msg[8 + 2 * j], msg[9 + 2 * j], '%s%d' % (dn, j))
        states['X' if r == 0 else 'Z'] = v[:]
        msg = [msg[i] for i in B.PERMUTATION]
    for s, ids in states.items():
        for i, wid in enumerate(ids):
            T.alias[wid] = T.alias.get(wid, []) + ['%s%d' % (s, i)]
    out = tuple(T.val[v[i]] ^ T.val[v[i + 8]] for i in range(8))
    out += tuple(T.val[v[i + 8]] ^ init[i] for i in range(8))
    return T, states, m, out


def check_relation(T, kind, ids):
    w = [T.val[i] for i in ids]
    if kind == 'add3':
        return w[3] == (w[0] + w[1] + w[2]) & MASK
    if kind == 'add':
        return w[2] == (w[0] + w[1]) & MASK
    n = int(kind[2:])
    return w[2] == ror(w[0] ^ w[1], n)


def validate(n=300, seed=1):
    rng = random.Random(seed)
    bad = 0
    for _ in range(n):
        words = [rng.getrandbits(32) for _ in range(16)]
        ctr = rng.getrandbits(64)
        bl, fl = rng.choice([(55, 3), (63, 11), (64, 0)])
        T, st, m, out = traced_compress(words, ctr, bl, fl)
        ref = B._compress(list(B.IV), words, ctr, bl, fl, 2)
        bad += (tuple(ref) != out)
        bad += sum(not check_relation(T, k, ids) for _, k, ids in T.rel)
    return n, bad


def nm(T, wid):
    a = T.alias.get(wid)
    return '%s(%s)' % (T.name[wid], '/'.join(a)) if a else T.name[wid]


def build_system(variant):
    """variant: 'root' (t fixed 0), 'ctr' (t_lo free), 'ctr2' (t_lo, t_hi free)."""
    rng = random.Random(7)
    T, st, m, _ = traced_compress([rng.getrandbits(32) for _ in range(16)], 0, 55, 11)
    calls = {'K0', 'K1', 'K2', 'K3', 'D0', 'D1', 'D2', 'D3', 'C0', 'C1', 'C2', 'C3'}
    rels = [ids for (c, k, ids) in T.rel if c in calls]
    words = sorted({w for ids in rels for w in ids})
    fixed = set(range(16))                     # init state v0..v15
    if variant in ('ctr', 'ctr2'):
        fixed.discard(12)
    if variant == 'ctr2':
        fixed.discard(13)
    fixed |= {m[4], m[13], m[14], m[15]}       # w4 = W4, w13 = W13, w14 = w15 = 0
    X = st['X']
    fixed |= {X[3], X[7], X[11], X[15]}        # pins
    # propagate: a relation with one unknown word determines it
    live = [list(ids) for ids in rels]
    used = [False] * len(live)
    changed = True
    while changed:
        changed = False
        for i, ids in enumerate(live):
            if used[i]:
                continue
            unk = [w for w in ids if w not in fixed]
            if len(unk) == 1:
                fixed.add(unk[0]); used[i] = True; changed = True
    const_checks = [i for i, ids in enumerate(live) if not used[i] and all(w in fixed for w in ids)]
    R = [tuple(w for w in ids if w not in fixed) for i, ids in enumerate(live) if not used[i]]
    R = [r for r in R if r]
    W = sorted({w for r in R for w in r})
    Y = st['Y']
    E1 = [Y[1], Y[6], Y[12], m[12], m[5]]
    E3 = [Y[4], Y[9], Y[14], m[8]]
    for t in E1 + E3:
        assert t in W, nm(T, t)
    assert Y[3] in fixed and Y[11] in fixed
    return T, W, R, E1, E3, const_checks, m, st


def solve(W, R, E1, E3, mU=1, mV=1, maxS=None, maximin=False, time_limit=120):
    """Exact ILP over labelings. Returns dict or None (infeasible)."""
    widx = {w: i for i, w in enumerate(W)}
    nW, nR = len(W), len(R)
    N = nW + nR
    nv = 2 * N + (1 if maximin else 0)
    X = lambda n: 2 * n
    Yv = lambda n: 2 * n + 1
    rows, cols, vals, lo, hi = [], [], [], [], []
    k = [0]

    def add(entries, l, h):
        for c, v in entries:
            rows.append(k[0]); cols.append(c); vals.append(v)
        lo.append(l); hi.append(h); k[0] += 1

    for n in range(N):
        add([(Yv(n), 1), (X(n), -1)], -np.inf, 0)
    for j, r in enumerate(R):
        rn = nW + j
        for w in r:
            wn = widx[w]
            add([(X(rn), 1), (X(wn), -1)], -np.inf, 0)
            add([(Yv(wn), 1), (Yv(rn), -1)], -np.inf, 0)
    # d_U = (nW - nR) - sum x_w + sum x_r ; d_V = sum y_w - sum y_r
    dU = [(X(n), -1) for n in range(nW)] + [(X(nW + j), 1) for j in range(nR)]
    dV = [(Yv(n), 1) for n in range(nW)] + [(Yv(nW + j), -1) for j in range(nR)]
    dS = [(X(n), 1) for n in range(nW)] + [(Yv(n), -1) for n in range(nW)] + \
         [(X(nW + j), -1) for j in range(nR)] + [(Yv(nW + j), 1) for j in range(nR)]
    if maximin:
        tau = 2 * N
        add(dU + [(tau, -1)], -(nW - nR), np.inf)
        add(dV + [(tau, -1)], 0, np.inf)
    else:
        add(dU, mU - (nW - nR), np.inf)
        add(dV, mV, np.inf)
    if maxS is not None:
        add(dS, -np.inf, maxS)
    A = coo_matrix((vals, (rows, cols)), shape=(k[0], nv)).tocsr()
    lb = np.zeros(nv); ub = np.ones(nv)
    for t in E1:
        ub[Yv(widx[t])] = 0          # E1 inputs never on the E3 side
    for t in E3:
        lb[X(widx[t])] = 1           # E3 inputs never on the E1 side
    c = np.zeros(nv)
    if maximin:
        lb[2 * N] = -64; ub[2 * N] = 64
        c[2 * N] = -1.0
        for col, v in dS:            # tie-break: smaller d_S
            c[col] += v * 1e-3
    else:
        for col, v in dS:
            c[col] += v
    res = milp(c, integrality=np.ones(nv), bounds=Bounds(lb, ub),
               constraints=LinearConstraint(A, lo, hi),
               options={'time_limit': time_limit, 'disp': False})
    if res.status != 0 or res.x is None:
        return {'status': int(res.status), 'message': res.message}
    z = np.round(res.x).astype(int)
    lab = {}
    for n in range(nW):
        lab[W[n]] = 'U' if z[X(n)] == 0 else ('S' if z[Yv(n)] == 0 else 'V')
    rl = []
    for j in range(nR):
        n = nW + j
        rl.append('U' if z[X(n)] == 0 else ('S' if z[Yv(n)] == 0 else 'V'))
    cnt = lambda L, s: sum(1 for x in L if x == s)
    wl = list(lab.values())
    d = {s: cnt(wl, s) - cnt(rl, s) for s in 'USV'}
    # independent re-check of the separation property
    for j, r in enumerate(R):
        labs = {lab[w] for w in r}
        assert not ('U' in labs and 'V' in labs)
        if rl[j] == 'U':
            assert 'V' not in labs
        if rl[j] == 'V':
            assert 'U' not in labs
        if rl[j] == 'S':
            assert labs == {'S'}
    return {'status': 0, 'dU': d['U'], 'dV': d['V'], 'dS': d['S'], 'lab': lab, 'rl': rl,
            'mip_gap': getattr(res, 'mip_gap', None)}


def join_floor_log2(m):
    """log2 of list entries needed for one 128-bit match, L <= 2^(32m) per side."""
    if m <= 0:
        return float('inf')
    return 129 - 32 * min(m, 2)


def main():
    t0 = time.time()
    log = []
    p = lambda *a: (print(*a), log.append(' '.join(str(x) for x in a)))
    n, bad = validate()
    p('VALIDATE traced compression vs blake3._compress (2 rounds): %d random inputs, %d mismatches/failed relations' % (n, bad))
    assert bad == 0
    summary = {}
    for variant in ('root', 'ctr', 'ctr2'):
        T, W, R, E1, E3, cc, m, st = build_system(variant)
        dim = len(W) - len(R)
        p('\n== variant %s: free words %d, relations %d, structural dim %d words (%d bits); constant checks %d'
          % (variant, len(W), len(R), dim, 32 * dim, len(cc)))
        out = {'dim': dim}
        # (a) GAPS item 5 literally: one extra constant (d_S <= 1), both sides varying
        r1 = solve(W, R, E1, E3, 1, 1, maxS=1)
        p('  (a) one extra pinned word (d_S<=1), d_U>=1, d_V>=1:', 'FEASIBLE' if r1.get('status') == 0 else 'INFEASIBLE (%s)' % r1.get('message'))
        out['one_extra_pin_feasible'] = r1.get('status') == 0
        # (b) least separator dimension for any non-degenerate split
        r2 = solve(W, R, E1, E3, 1, 1)
        if r2.get('status') == 0:
            p('  (b) min d_S with d_U>=1, d_V>=1: d_S=%d, d_U=%d, d_V=%d' % (r2['dS'], r2['dU'], r2['dV']))
            S = [nm(T, w) for w, l in r2['lab'].items() if l == 'S']
            V = [nm(T, w) for w, l in r2['lab'].items() if l == 'V']
            p('      S words (%d): %s' % (len(S), ', '.join(S)))
            p('      V words (%d): %s' % (len(V), ', '.join(V)))
            out['min_dS'] = r2['dS']; out['at_min_dS'] = (r2['dU'], r2['dV'])
        else:
            p('  (b) no non-degenerate split at all:', r2)
            out['min_dS'] = None
        # (c) max over labelings of min(d_U, d_V)
        r3 = solve(W, R, E1, E3, maximin=True)
        if r3.get('status') == 0:
            mm = min(r3['dU'], r3['dV'])
            p('  (c) max min(d_U,d_V) = %d (d_U=%d, d_V=%d, d_S=%d)' % (mm, r3['dU'], r3['dV'], r3['dS']))
            out['maximin'] = mm; out['maximin_at'] = (r3['dU'], r3['dV'], r3['dS'])
        # (d) Pareto: for each mU, the best d_V
        par = []
        for mU in range(1, dim + 1):
            best = None
            for mV in range(dim, 0, -1):
                r = solve(W, R, E1, E3, mU, mV)
                if r.get('status') == 0:
                    best = (mU, mV, r['dS']); break
            if best is None:
                break
            par.append(best)
        p('  (d) Pareto (d_U>=a, max d_V=b, d_S at that point):', par)
        out['pareto'] = par
        mm = out.get('maximin', 0)
        p('  join floor: min(d_U,d_V)=%d words -> >= 2^%s list entries per 128-bit match (DERIVED)' % (mm, join_floor_log2(mm)))
        out['join_floor_log2_entries'] = join_floor_log2(mm)
        summary[variant] = out
    p('\nelapsed %.1f s' % (time.time() - t0))
    with open(OUT + r'\split_out.json', 'w') as f:
        json.dump(summary, f, indent=1)
    with open(OUT + r'\split_out.txt', 'w') as f:
        f.write('\n'.join(log) + '\n')


if __name__ == '__main__':
    main()
