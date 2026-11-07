#!/usr/bin/env python3
"""b3-misc/r0tri.py -- cell r0 x cost, exact version of the w8-outer lever test.

Does ANY choice of the 7 outer words make the system (round 0 + round-1
columns + E1 first half, t_lo free) solvable one assignment at a time with
w8 an outer word, y = Y4 the member and c1 = E1.c1 the trial word?
ILP: each relation determines exactly one of its words (a matching), each word
is determined at most once, levels forbid cycles (l_w >= l_u + 1 whenever the
relation determining w contains u). Free words = the 9 unmatched words.
Control: the front-line set (map 2.5) must come out feasible.
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

import sys, json
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/newpaths/untried/b3-misc'))
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds
from scipy.sparse import coo_matrix
import r0swap as RS
import split as SP

OUT = _hca_public_path_text('__HCA_WORKSPACE__/research/newpaths/untried/b3-misc')


def tri(rels, fixed, must_free, must_det=(), time_limit=240):
    R = [tuple(w for w in ids if w not in fixed) for c, ids in rels]
    W = sorted({w for r in R for w in r})
    wi = {w: i for i, w in enumerate(W)}
    A_idx = []                      # (r, w) pairs
    for j, r in enumerate(R):
        for w in r:
            A_idx.append((j, w))
    na = len(A_idx); nW = len(W)
    nv = na + nW                    # assignment binaries, then levels
    M = nW + 2
    rows, cols, vals, lo, hi = [], [], [], [], []
    k = [0]

    def add(ent, l, h):
        for c, v in ent:
            rows.append(k[0]); cols.append(c); vals.append(v)
        lo.append(l); hi.append(h); k[0] += 1

    byr = {}
    byw = {}
    for a, (j, w) in enumerate(A_idx):
        byr.setdefault(j, []).append(a)
        byw.setdefault(w, []).append(a)
    for j in range(len(R)):
        add([(a, 1) for a in byr[j]], 1, 1)
    for w in W:
        h = 0 if w in must_free else 1
        l = 1 if w in must_det else 0
        add([(a, 1) for a in byw[w]], l, h)
    for a, (j, w) in enumerate(A_idx):
        for u in R[j]:
            if u == w:
                continue
            # l_w - l_u - M*a >= 1 - M
            add([(na + wi[w], 1), (na + wi[u], -1), (a, -M)], 1 - M, np.inf)
    A = coo_matrix((vals, (rows, cols)), shape=(k[0], nv)).tocsr()
    lb = np.zeros(nv); ub = np.ones(nv)
    ub[na:] = M
    integ = np.ones(nv); integ[na:] = 0
    res = milp(np.zeros(nv), integrality=integ, bounds=Bounds(lb, ub),
               constraints=LinearConstraint(A, lo, hi), options={'time_limit': time_limit, 'disp': False})
    if res.x is None:
        return {'status': int(res.status), 'message': res.message}
    z = res.x
    det = {w for a, (j, w) in enumerate(A_idx) if z[a] > 0.5}
    free = [w for w in W if w not in det]
    return {'status': int(res.status), 'free': free}


def main():
    log = []
    p = lambda *a: (print(*a, flush=True), log.append(' '.join(str(x) for x in a)))
    T, rels, byname, fixed, calls0 = RS.setup()
    base = ['C0.d1', 'D2.a1', 'D2.b1', 'S11', 'S4', 'X9', 'w6']
    y, c1, w8 = byname['Y4'], byname['E1.c1'], byname['w8']
    # control: front line's 9 free words forced free
    ctl = tri(rels, fixed, must_free={byname[n] for n in base} | {y, c1})
    p('control (front-line free set forced):', ctl.get('status'), [SP.nm(T, w) for w in ctl.get('free', [])] or ctl.get('message'))
    # lever: w8, y, c1 free; other 6 outer words free choice
    lev = tri(rels, fixed, must_free={w8, y, c1})
    p('lever (w8, Y4, E1.c1 free; 6 outer words free choice):', lev.get('status'),
      [SP.nm(T, w) for w in lev.get('free', [])] or lev.get('message'))
    out = {'control': ctl.get('status'), 'lever': lev.get('status')}
    if lev.get('free'):
        outer = [SP.nm(T, w).split('(')[0] for w in lev['free'] if w not in (y, c1)]
        al = []
        for w in lev['free']:
            if w in (y, c1):
                continue
            a = T.alias.get(w)
            al.append(a[0] if a else T.name[w])
        r = RS.evaluate(T, rels, byname, fixed, calls0, al)
        p('  propagation check of that set:', r)
        out['lever_set'] = al; out['lever_eval'] = r
    json.dump(out, open(OUT + r'\r0tri_out.json', 'w'), indent=1)
    open(OUT + r'\r0tri_out.txt', 'w').write('\n'.join(log) + '\n')


if __name__ == '__main__':
    main()
