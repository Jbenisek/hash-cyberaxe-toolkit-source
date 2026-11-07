"""Exact linear-consistency filter for word-level message-only routes (one process, capped).

The truncated model (trunc_search.c) treats every cancellation as possible.  Here every word also
carries its modular difference as a linear form over GF(p) (p = 2^61-1, a proxy for the integers):
  - message word m_j: its own variable (the SAME variable in round 0 and round 1);
  - an addition: the exact sum of its input forms; a cancellation adds the constraint "sum = 0";
  - an xor-rotate output: a fresh variable (no linear relation assumed: optimistic);
  - every active value must stay nonzero (not forced to 0 by the constraints).
A route is linearly infeasible when the constraints force an active value to 0.

Refined round-1 cost (model B'): xor cancellations and fold cancellations count 1; an addition
cancellation counts 1 when its reduced constraint involves a fresh variable (a condition on values),
0 when it only relates message differences (a free choice of differences) or is already implied.

Search: depth-first over the 16 G calls and all op-level cancellation choices, pruned by the exact
truncated model-B cost-to-go (round-0 conditions free, round-1 + fold counted) and by linear
infeasibility.  So it is exhaustive over routes whose truncated model-B cost is <= budget.

  python -B exact_routes.py <M> <budget> [node_cap]
"""
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from analyze import COLW, DIAW, INF, PERM, POP, LO, FOLD_OK, T0, T1, apply_call  # noqa: E402

P = (1 << 61) - 1


def build_combos():
    C = {}
    for inp in range(16):
        a, b, c, d = (inp >> 0) & 1, (inp >> 1) & 1, (inp >> 2) & 1, (inp >> 3) & 1
        for m in range(4):
            x, y = m & 1, (m >> 1) & 1
            lst = []

            def rec(k, v, canc):
                if k == 8:
                    out = v[4] | (v[7] << 1) | (v[6] << 2) | (v[5] << 3)
                    lst.append((tuple(v), tuple(canc), out, sum(canc)))
                    return
                n = [lambda: a + b + x, lambda: d + v[0], lambda: c + v[1], lambda: b + v[2],
                     lambda: v[0] + v[3] + y, lambda: v[1] + v[4], lambda: v[2] + v[5],
                     lambda: v[3] + v[6]][k]()
                if n <= 1:
                    rec(k + 1, v + [n], canc + [0])
                else:
                    rec(k + 1, v + [1], canc + [0])
                    rec(k + 1, v + [0], canc + [1])
            rec(0, [], [])
            C[(inp, m)] = lst
    return C


COMBOS = build_combos()
ADD_OPS = {0, 2, 4, 6}     # a1, c1, a2, c2 are additions; 1, 3, 5, 7 are xor-rotates


def calls(M):
    out = []
    for k in range(16):
        step, g = divmod(k, 4)
        if step == 0:
            W, wx, wy = COLW[g], 2 * g, 2 * g + 1
        elif step == 1:
            W, wx, wy = DIAW[g], 8 + 2 * g, 9 + 2 * g
        elif step == 2:
            W, wx, wy = COLW[g], PERM[2 * g], PERM[2 * g + 1]
        else:
            W, wx, wy = DIAW[g], PERM[8 + 2 * g], PERM[9 + 2 * g]
        msg = ((M >> wx) & 1) | (((M >> wy) & 1) << 1)
        out.append(("KDCE"[step] + str(g), W, wx, wy, msg, 0 if step < 2 else 1))
    return out


def ctg_arrays(M):
    """Exact truncated model-B cost-to-go before each call (and the fold array at index 16)."""
    cl = calls(M)
    fold = np.where(FOLD_OK, POP[LO], INF).astype(np.int64)
    arrs = [None] * 17
    arrs[16] = fold
    cur = fold
    for k in range(15, -1, -1):
        name, W, wx, wy, msg, rnd = cl[k]
        Tw = (T1 if rnd else T0)[:, msg, :]
        cur = apply_call(cur, W, np.ascontiguousarray(Tw.T))
        arrs[k] = cur
    return cl, arrs


def fadd(*fs):
    r = {}
    for f in fs:
        for v, c in f.items():
            n = (r.get(v, 0) + c) % P
            if n:
                r[v] = n
            else:
                r.pop(v, None)
    return r


def reduce(f, basis):
    f = dict(f)
    for piv, row in basis.items():
        c = f.get(piv)
        if c:
            for v, rc in row.items():
                n = (f.get(v, 0) - c * rc) % P
                if n:
                    f[v] = n
                else:
                    f.pop(v, None)
    return f


def add_constraint(cons, basis, reqs):
    """Returns (basis, reqs, kind) with kind in {'implied','msg','value'}; None if infeasible."""
    c = reduce(cons, basis)
    if not c:
        return basis, reqs, "implied"
    kind = "value" if any(v >= 16 for v in c) else "msg"
    piv = max(c)
    inv = pow(c[piv], P - 2, P)
    c = {v: cv * inv % P for v, cv in c.items()}
    nb = {}
    for p2, row in basis.items():
        if piv in row:
            k = row[piv]
            row = {v: n for v in set(row) | set(c) for n in [(row.get(v, 0) - k * c.get(v, 0)) % P] if n}
        nb[p2] = row
    nb[piv] = c
    nr = []
    for r in reqs:
        if piv in r:
            k = r[piv]
            r = {v: n for v in set(r) | set(c) for n in [(r.get(v, 0) - k * c.get(v, 0)) % P] if n}
            if not r:
                return None
        nr.append(r)
    return nb, nr, kind


class Search:
    def __init__(self, M, budget, cap):
        self.M, self.budget, self.cap = M, budget, cap
        self.cl, self.ctg = ctg_arrays(M)
        self.nodes = 0
        self.fresh = 16
        self.found = []          # (refined_r1, truncated_r1, r0_value_conditions, trail)
        self.infeasible_leaves = 0
        self.capped = False

    def run(self):
        forms = [dict() for _ in range(16)]
        reqs = [{j: 1} for j in range(16) if (self.M >> j) & 1]
        self.dfs(0, 0, forms, {}, reqs, 0, 0, 0, [])

    def dfs(self, k, s, forms, basis, reqs, tcost, rcost, r0val, trail):
        if self.nodes >= self.cap:
            self.capped = True
            return
        self.nodes += 1
        if tcost + self.ctg[k][s] > self.budget:
            return
        if k == 16:
            lo, hi = s & 0xFF, s >> 8
            if lo != hi:
                return
            nf = bin(lo).count("1")
            self.found.append((rcost + nf, tcost + nf, r0val, list(trail)))
            return
        name, W, wx, wy, msg, rnd = self.cl[k]
        inp = sum(((s >> W[j]) & 1) << j for j in range(4))
        xf = {wx: 1} if (self.M >> wx) & 1 else {}
        yf = {wy: 1} if (self.M >> wy) & 1 else {}
        a, b, c, d = (forms[W[0]], forms[W[1]], forms[W[2]], forms[W[3]])
        for v, canc, out, cost in COMBOS[(inp, msg)]:
            t2 = tcost + (cost if rnd else 0)
            s2 = s
            for j in range(4):
                s2 = (s2 & ~(1 << W[j])) | (((out >> j) & 1) << W[j])
            if t2 + self.ctg[k + 1][s2] > self.budget:
                continue
            res = self.apply(v, canc, a, b, c, d, xf, yf, basis, reqs, rnd)
            if res is None:
                self.infeasible_leaves += 1
                continue
            vals, nb, nr, rc, r0 = res
            nforms = list(forms)
            nforms[W[0]], nforms[W[1]], nforms[W[2]], nforms[W[3]] = vals[4], vals[7], vals[6], vals[5]
            trail.append((name, inp, out, cost, rc))
            self.dfs(k + 1, s2, nforms, nb, nr, t2, rcost + rc, r0val + r0, trail)
            trail.pop()
            if self.nodes >= self.cap:
                return

    def apply(self, v, canc, a, b, c, d, xf, yf, basis, reqs, rnd):
        vals = [None] * 8
        rc = 0
        r0 = 0
        for k in range(8):
            if k == 0:
                ins = (a, b, xf)
            elif k == 1:
                ins = (d, vals[0])
            elif k == 2:
                ins = (c, vals[1])
            elif k == 3:
                ins = (b, vals[2])
            elif k == 4:
                ins = (vals[0], vals[3], yf)
            elif k == 5:
                ins = (vals[1], vals[4])
            elif k == 6:
                ins = (vals[2], vals[5])
            else:
                ins = (vals[3], vals[6])
            nact = sum(1 for f in ins if f)
            if k in ADD_OPS:
                sf = fadd(*ins)
                if canc[k]:
                    r = add_constraint(sf, basis, reqs)
                    if r is None:
                        return None
                    basis, reqs, kind = r
                    if kind == "value":
                        if rnd:
                            rc += 1
                        else:
                            r0 += 1
                    vals[k] = {}
                elif v[k]:
                    if nact >= 2:
                        red = reduce(sf, basis)
                        if not red:
                            return None
                        reqs = reqs + [red]
                    vals[k] = sf
                else:
                    vals[k] = {}
            else:
                if canc[k]:
                    if rnd:
                        rc += 1
                    else:
                        r0 += 1
                    vals[k] = {}
                elif v[k]:
                    fv = self.fresh
                    self.fresh += 1
                    vals[k] = {fv: 1}
                    reqs = reqs + [{fv: 1}]
                else:
                    vals[k] = {}
        return vals, basis, reqs, rc, r0


def main():
    M = int(sys.argv[1])
    budget = int(sys.argv[2])
    cap = int(sys.argv[3]) if len(sys.argv) > 3 else 2_000_000
    t0 = time.time()
    S = Search(M, budget, cap)
    S.run()
    words = [j for j in range(16) if (M >> j) & 1]
    print(f"M={M} m{words} truncated-budget={budget} nodes={S.nodes} capped={S.capped} "
          f"linearly-infeasible branches={S.infeasible_leaves} time={time.time() - t0:.1f}s")
    if not S.found:
        print("  no linearly consistent route within the truncated budget")
        return
    S.found.sort(key=lambda r: (r[0], r[1]))
    print(f"  consistent complete routes: {len(S.found)}; refined round-1 cost min {S.found[0][0]}, "
          f"truncated round-1 cost of that route {S.found[0][1]}, round-0 value conditions {S.found[0][2]}")
    lab = "abcd"
    best = S.found[0][3]
    for name, inp, out, cost, rc in best:
        if inp or out or cost:
            ins = "".join(lab[j] for j in range(4) if (inp >> j) & 1) or "-"
            outs = "".join(lab[j] for j in range(4) if (out >> j) & 1) or "-"
            print(f"    {name}: in {ins:4s} -> out {outs:4s} cancellations {cost} genuine-round1 {rc}")


if __name__ == "__main__":
    main()
