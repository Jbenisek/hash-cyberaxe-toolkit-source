#!/usr/bin/env python3
"""|L*| and |G| for a 38-step dense part S (scout2-1).  L*: every (W14, W15) obtained by changing the free bits of
E14, E15 (rows 0..13 of S kept) such that rows 14, 15 hold (A/E/W cells, '+' pairs), dW17 = 0 (s1 difference of
W15), dW30 = 0 (s0 difference of W15) and the row-16 modular differences dE16, dA16 equal the published pair's
(the r37 late_variants_r37.py definition, transcribed to r38; W14 carries no difference so dW16 = dW9 holds).
G: every W16 (member x) for which row 16 holds (cells, '+', two-bit conditions keyed at row 16) with S's rows
12..15 (vt38.py's G for the published S has 32 values).

  python lstar38.py published
  python lstar38.py FILE.sols.json [index ...]
"""
import sys, json, time
from r38core import *

def subsets(mask):
    bits = [b for b in range(32) if mask >> b & 1]
    for k in range(1 << len(bits)):
        x = 0
        for j, b in enumerate(bits):
            if k >> j & 1: x |= 1 << b
        yield x

def Arow(E, A, i): return (E - A[i-4] + S0(A[i-1]) + MAJ(A[i-1], A[i-2], A[i-3])) & M
def Wrow(A, E, i): return (E[i] - A[i-4] - E[i-4] - S1(E[i-1]) - CH(E[i-1], E[i-2], E[i-3]) - K[i]) & M

def cellok(k, i, x, y):
    m, v, d, _ = CELL[k][i]
    return x & m == v and x ^ y == d

def lstar(Ax):
    X, Y = dense_from_A(Ax)
    (A0x, E0x, W0x), (A0y, E0y, W0y) = X, Y
    m14, v14, d14, _ = CELL['E'][14]; m15, v15, d15, _ = CELL['E'][15]
    out = []; n14 = 0
    Ax_, Ex_, Wx_ = dict(A0x), dict(E0x), dict(W0x); Ay_, Ey_, Wy_ = dict(A0y), dict(E0y), dict(W0y)
    for e14 in subsets(~m14 & M):
        Ex_[14] = v14 | e14; Ey_[14] = Ex_[14] ^ d14
        if (Ex_[14] ^ Ex_[13]) & PLUS[14]: continue
        Ax_[14] = Arow(Ex_[14], Ax_, 14); Ay_[14] = Arow(Ey_[14], Ay_, 14)
        if not cellok('A', 14, Ax_[14], Ay_[14]): continue
        Wx_[14] = Wrow(Ax_, Ex_, 14); Wy_[14] = Wrow(Ay_, Ey_, 14)
        if not cellok('W', 14, Wx_[14], Wy_[14]): continue
        n14 += 1; w15s = []
        for e15 in subsets(~m15 & M):
            Ex_[15] = v15 | e15; Ey_[15] = Ex_[15] ^ d15
            if (Ex_[15] ^ Ex_[14]) & PLUS[15]: continue
            Ax_[15] = Arow(Ex_[15], Ax_, 15); Ay_[15] = Arow(Ey_[15], Ay_, 15)
            if not cellok('A', 15, Ax_[15], Ay_[15]): continue
            Wx_[15] = Wrow(Ax_, Ex_, 15); Wy_[15] = Wrow(Ay_, Ey_, 15)
            if not cellok('W', 15, Wx_[15], Wy_[15]): continue
            if md(s1(Wx_[15]), s1(Wy_[15])) != REF['s1W15'] or md(s0(Wx_[15]), s0(Wy_[15])) != REF['s0W15']: continue
            if md(Pf(Ax_, Ex_), Pf(Ay_, Ey_)) != REF['P'] or md(Rf(Ax_), Rf(Ay_)) != REF['R']: continue
            w15s.append((Wx_[15], Ax_[15], Ex_[15]))
        if w15s: out.append((Wx_[14], Ax_[14], Ex_[14], w15s))
    return out, n14

def stages(Ax):
    """Counts of (E14, E15) candidates surviving each L* filter in turn (rows 0..13 of S kept)."""
    X, Y = dense_from_A(Ax)
    (A0x, E0x, W0x), (A0y, E0y, W0y) = X, Y
    m14, v14, d14, _ = CELL['E'][14]; m15, v15, d15, _ = CELL['E'][15]
    names = ['E14 cand', 'plus14', 'A14 cell', 'W14 cell', 'E15 cand', 'plus15', 'A15 cell', 'W15 cell',
             's1W15', 's0W15', 'P (dE16)', 'R (dA16)']
    cnt = dict.fromkeys(names, 0)
    Ax_, Ex_, Wx_ = dict(A0x), dict(E0x), dict(W0x); Ay_, Ey_, Wy_ = dict(A0y), dict(E0y), dict(W0y)
    for e14 in subsets(~m14 & M):
        cnt['E14 cand'] += 1
        Ex_[14] = v14 | e14; Ey_[14] = Ex_[14] ^ d14
        if (Ex_[14] ^ Ex_[13]) & PLUS[14]: continue
        cnt['plus14'] += 1
        Ax_[14] = Arow(Ex_[14], Ax_, 14); Ay_[14] = Arow(Ey_[14], Ay_, 14)
        if not cellok('A', 14, Ax_[14], Ay_[14]): continue
        cnt['A14 cell'] += 1
        Wx_[14] = Wrow(Ax_, Ex_, 14); Wy_[14] = Wrow(Ay_, Ey_, 14)
        if not cellok('W', 14, Wx_[14], Wy_[14]): continue
        cnt['W14 cell'] += 1
        for e15 in subsets(~m15 & M):
            cnt['E15 cand'] += 1
            Ex_[15] = v15 | e15; Ey_[15] = Ex_[15] ^ d15
            if (Ex_[15] ^ Ex_[14]) & PLUS[15]: continue
            cnt['plus15'] += 1
            Ax_[15] = Arow(Ex_[15], Ax_, 15); Ay_[15] = Arow(Ey_[15], Ay_, 15)
            if not cellok('A', 15, Ax_[15], Ay_[15]): continue
            cnt['A15 cell'] += 1
            Wx_[15] = Wrow(Ax_, Ex_, 15); Wy_[15] = Wrow(Ay_, Ey_, 15)
            if not cellok('W', 15, Wx_[15], Wy_[15]): continue
            cnt['W15 cell'] += 1
            if md(s1(Wx_[15]), s1(Wy_[15])) != REF['s1W15']: continue
            cnt['s1W15'] += 1
            if md(s0(Wx_[15]), s0(Wy_[15])) != REF['s0W15']: continue
            cnt['s0W15'] += 1
            if md(Pf(Ax_, Ex_), Pf(Ay_, Ey_)) != REF['P']: continue
            cnt['P (dE16)'] += 1
            if md(Rf(Ax_), Rf(Ay_)) != REF['R']: continue
            cnt['R (dA16)'] += 1
    return cnt

def gset(X, Y):
    """All W16 (member x) for which row 16 holds, rows 12..15 of (X, Y)."""
    (Ax, Ex, Wx), (Ay, Ey, Wy) = X, Y
    Px, Py = Pf(Ax, Ex), Pf(Ay, Ey); Rx, Ry = Rf(Ax), Rf(Ay)
    m16, v16, d16, _ = CELL['E'][16]; mw, vw, dw, _ = CELL['W'][16]
    conds = XROW.get(16, ())
    G = []
    for e in subsets(~m16 & M):
        ex = v16 | e; ey = ex ^ d16
        if (ex ^ Ex[15]) & PLUS[16]: continue
        w16x = (ex - Px - K[16]) & M; w16y = (ey - Py - K[16]) & M
        if not cellok('W', 16, w16x, w16y): continue
        a16x = (ex - Ax[12] + Rx) & M; a16y = (ey - Ay[12] + Ry) & M
        if not cellok('A', 16, a16x, a16y): continue
        V = {'A': {14: Ax[14], 15: Ax[15], 16: a16x}, 'E': {15: Ex[15], 16: ex}, 'W': {16: w16x}}
        if all(((V[k1][i1] >> b1) ^ (V[k2][i2] >> b2)) & 1 == ne for k1, i1, b1, ne, k2, i2, b2 in conds):
            G.append(w16x)
    return G

def report(name, Ax):
    t = time.time()
    ls, n14 = lstar(Ax)
    n = sum(len(w) for *_, w in ls)
    X, Y = dense_from_A(Ax)
    own = (X[2][14], X[2][15])
    own_in = any(w14 == own[0] and any(w15 == own[1] for w15, _, _ in w) for w14, _, _, w in ls)
    gs = [len(gset(*dense_from_A({**{i: Ax[i] for i in range(14)}, 14: a14, 15: a15}))) for w14, a14, e14, w in ls
          for w15, a15, e15 in w]
    print('%s: |L*| = %d (W14 values %d, row-14 survivors %d), own (W14,W15) in L*: %s, |G| per L* element %s  %.1fs'
          % (name, n, len(ls), n14, own_in, gs, time.time() - t))
    return {'name': name, 'Lstar': n, 'W14s': len(ls), 'G': gs, 'own_in': own_in,
            'L': [('%08x' % w14, ['%08x' % w15 for w15, _, _ in w]) for w14, _, _, w in ls]}

if __name__ == '__main__':
    res = []
    if sys.argv[1] == 'stages':
        S = {'published': {i: TX[0][i] for i in range(16)}}
        for fn in sys.argv[2:]:
            for j, s in enumerate(json.load(open(fn))): S['%s[%d]' % (fn, j)] = {int(i): v for i, v in s['Ax'].items()}
        for k, Ax in S.items():
            print(k, stages(Ax))
        sys.exit(0)
    if sys.argv[1] == 'published':
        r = report('published S', {i: TX[0][i] for i in range(16)})
        g = gset(*dense_from_A({i: TX[0][i] for i in range(16)}))
        print('published G check (vt38 G = 32 values from GBASE 35f29010):', len(g), '%08x' % min(g) if g else '')
        res.append(r)
    else:
        sols = json.load(open(sys.argv[1]))
        idx = [int(a) for a in sys.argv[2:]] or range(len(sols))
        for j in idx:
            s = sols[j]
            res.append(report('%s[%d] %s' % (sys.argv[1], j, s.get('out', '')), {int(i): v for i, v in s['Ax'].items()}))
    json.dump(res, open('lstar_last.json', 'w'), indent=1)
