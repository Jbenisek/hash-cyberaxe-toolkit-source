#!/usr/bin/env python3
"""b3-misc/split2.py -- (1) sanity tests of split.solve on toy systems with known
answers; (2) the general word-level MITM split: words U / V / S, relations
U / V / S / X (X = crossed relation, matched as a 32-bit list key; every
add / xor-rotate relation is separable as f(U-words) = g(V-words)).

Quality q = min(d_U, d_V) - c  (c = number of crossed relations).
Cost floor for one 128-bit residual match with lists L <= 2^(32 min(d_U,d_V)):
  entries >= 2^(129 + 32c) / L >= 2^(129 - 32 q)   (DERIVED formula).
Constraints: E1 inputs in U or S, E3 inputs in V or S, d_S >= 0.
This model is permissive (structural counts may overstate useful freedom), so its
optimum is an UPPER bound on what any word-level split can reach.
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

import sys, time, json
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/newpaths/untried/b3-misc'))
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds
from scipy.sparse import coo_matrix
import split as SP

OUT = _hca_public_path_text('__HCA_WORKSPACE__/research/newpaths/untried/b3-misc')


def toy_tests(p):
    # toy 1: two sides joined only through s  -> split (dU,dV,dS) = (1,1,1) must be found
    W = ['a1', 'a2', 's', 'c1', 'c2']
    R = [('a1', 'a2', 's'), ('c1', 'c2', 's')]
    r = SP.solve(W, R, ['a1'], ['c1'], 1, 1)
    ok1 = r.get('status') == 0 and (r['dU'], r['dV'], r['dS']) == (1, 1, 1)
    # toy 2: a chain a - m - c where every word sits in 2 relations -> no split with both >= 1
    W2 = ['a', 'm', 'c', 'f']
    R2 = [('a', 'm', 'f'), ('m', 'c', 'f')]
    r2 = SP.solve(W2, R2, ['a'], ['c'], 1, 1)
    ok2 = r2.get('status') != 0 or min(r2['dU'], r2['dV']) >= 1   # dims: 4-2 = 2; split needs S={m,f}: dS=2 -> dU=dV=0
    # toy 2 exact expectation: infeasible
    ok2 = r2.get('status') != 0
    p('TOY 1 (separable, expect dU=dV=dS=1):', 'PASS' if ok1 else 'FAIL', {k: r.get(k) for k in ('status', 'dU', 'dV', 'dS')})
    p('TOY 2 (chain, expect infeasible):', 'PASS' if ok2 else 'FAIL', {k: r2.get(k) for k in ('status', 'dU', 'dV', 'dS')})
    return ok1 and ok2


def solve_cross(W, R, E1, E3, cmax=None, time_limit=200):
    widx = {w: i for i, w in enumerate(W)}
    nW, nR = len(W), len(R)
    # var layout: words 3*nW (u,v,s), relations 4*nR (u,v,s,x), tau
    uw = lambda i: 3 * i; vw = lambda i: 3 * i + 1; sw = lambda i: 3 * i + 2
    base = 3 * nW
    ur = lambda j: base + 4 * j; vr = lambda j: base + 4 * j + 1
    sr = lambda j: base + 4 * j + 2; xr = lambda j: base + 4 * j + 3
    tau = base + 4 * nR
    nv = tau + 1
    rows, cols, vals, lo, hi = [], [], [], [], []
    k = [0]

    def add(entries, l, h):
        for c, v in entries:
            rows.append(k[0]); cols.append(c); vals.append(v)
        lo.append(l); hi.append(h); k[0] += 1

    for i in range(nW):
        add([(uw(i), 1), (vw(i), 1), (sw(i), 1)], 1, 1)
    for j, r in enumerate(R):
        add([(ur(j), 1), (vr(j), 1), (sr(j), 1), (xr(j), 1)], 1, 1)
        for w in r:
            i = widx[w]
            add([(ur(j), 1), (vw(i), 1)], -np.inf, 1)
            add([(vr(j), 1), (uw(i), 1)], -np.inf, 1)
            add([(sr(j), 1), (sw(i), -1)], -np.inf, 0)
    dU = [(uw(i), 1) for i in range(nW)] + [(ur(j), -1) for j in range(nR)]
    dV = [(vw(i), 1) for i in range(nW)] + [(vr(j), -1) for j in range(nR)]
    dS = [(sw(i), 1) for i in range(nW)] + [(sr(j), -1) for j in range(nR)]
    add(dS, 0, np.inf)
    add(dU + [(tau, -1)], 0, np.inf)
    add(dV + [(tau, -1)], 0, np.inf)
    if cmax is not None:
        add([(xr(j), 1) for j in range(nR)], -np.inf, cmax)
    A = coo_matrix((vals, (rows, cols)), shape=(k[0], nv)).tocsr()
    lb = np.zeros(nv); ub = np.ones(nv)
    lb[tau] = -64; ub[tau] = 64
    for t in E1:
        ub[vw(widx[t])] = 0
    for t in E3:
        ub[uw(widx[t])] = 0
    c = np.zeros(nv)
    c[tau] = -1.0
    for j in range(nR):
        c[xr(j)] = 1.0
    res = milp(c, integrality=np.ones(nv), bounds=Bounds(lb, ub),
               constraints=LinearConstraint(A, lo, hi),
               options={'time_limit': time_limit, 'disp': False})
    if res.x is None:
        return {'status': int(res.status), 'message': res.message}
    z = np.round(res.x).astype(int)
    lab = {W[i]: 'U' if z[uw(i)] else ('V' if z[vw(i)] else 'S') for i in range(nW)}
    rl = ['U' if z[ur(j)] else ('V' if z[vr(j)] else ('S' if z[sr(j)] else 'X')) for j in range(nR)]
    cnt = lambda L, s: sum(1 for x in L if x == s)
    wl = list(lab.values())
    d = {s: cnt(wl, s) - cnt(rl, s) for s in 'USV'}
    cc = cnt(rl, 'X')
    for j, r in enumerate(R):     # independent re-check
        labs = {lab[w] for w in r}
        if rl[j] == 'U': assert 'V' not in labs
        if rl[j] == 'V': assert 'U' not in labs
        if rl[j] == 'S': assert labs == {'S'}
    q = min(d['U'], d['V']) - cc
    return {'status': int(res.status), 'optimal': res.status == 0, 'dU': d['U'], 'dV': d['V'], 'dS': d['S'],
            'c': cc, 'q': q, 'lab': lab, 'rl': rl, 'bound': -res.fun if res.fun is not None else None,
            'dual_bound': getattr(res, 'mip_dual_bound', None)}


def main():
    t0 = time.time()
    log = []
    p = lambda *a: (print(*a, flush=True), log.append(' '.join(str(x) for x in a)))
    ok = toy_tests(p)
    assert ok
    summary = {}
    for variant in ('root', 'ctr', 'ctr2'):
        T, W, R, E1, E3, cc, m, st = SP.build_system(variant)
        p('\n== variant %s (dim %d words)' % (variant, len(W) - len(R)))
        r = solve_cross(W, R, E1, E3, time_limit=90)
        if 'q' not in r:
            p('  no solution', r); continue
        p('  max q = min(dU,dV) - c = %d  [dU=%d dV=%d dS=%d crossed=%d] optimal=%s dual_bound=%s'
          % (r['q'], r['dU'], r['dV'], r['dS'], r['c'], r['optimal'], r['dual_bound']))
        X = [SP.nm(T, R[j][0]) + '..' for j, l in enumerate(r['rl']) if l == 'X']
        V = [SP.nm(T, w) for w, l in r['lab'].items() if l == 'V']
        S = [SP.nm(T, w) for w, l in r['lab'].items() if l == 'S']
        p('  V words (%d): %s' % (len(V), ', '.join(V)))
        p('  S words (%d): %s' % (len(S), ', '.join(S)))
        p('  cost floor >= 2^%d list entries per 128-bit match (DERIVED from q)' % (129 - 32 * r['q']))
        prof = []
        for cm in ((0, 1, 2, 4, 8) if variant == 'root' else ()):
            rr = solve_cross(W, R, E1, E3, cmax=cm, time_limit=40)
            if 'q' in rr:
                prof.append((cm, rr['q'], rr['dU'], rr['dV'], rr['dS'], rr['c']))
        p('  profile (c<=k: q, dU, dV, dS, c):', prof)
        summary[variant] = {'q': r['q'], 'dU': r['dU'], 'dV': r['dV'], 'dS': r['dS'], 'c': r['c'],
                            'optimal': r['optimal'], 'profile': prof,
                            'floor_log2_entries': 129 - 32 * r['q']}
    p('\nelapsed %.1f s' % (time.time() - t0))
    with open(OUT + r'\split2_out.json', 'w') as f:
        json.dump(summary, f, indent=1)
    with open(OUT + r'\split2_out.txt', 'w') as f:
        f.write('\n'.join(log) + '\n')


if __name__ == '__main__':
    main()
