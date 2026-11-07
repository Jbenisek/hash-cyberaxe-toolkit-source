"""Why the digest round fails after the theta6 spread (COMPUTED diagnosis, exact).

For chi5 input difference a5, b5 ranges over S(a5).  Each plane-0 chi6 row value is an affine function of b5.
(i)  rows whose value is CONSTANT over S(a5) and not an allowed digest pattern -> P(collision | a5) = 0 exactly.
(ii) otherwise an exact depth-first search over the allowed row patterns with incremental GF(2) elimination
     decides feasibility (any b5 with every plane-0 row allowed), and returns the cheapest pattern cost found.
Usage: python dds6.py <first_class> <last_class_exclusive> [max_w4=13]"""
import sys
import math
import time
import kk
import dds2 as D
from dds5 import row_affine

t0 = time.time()
lo, hi = int(sys.argv[1]), int(sys.argv[2])
MAXW4 = int(sys.argv[3]) if len(sys.argv) > 3 else 13
PI = kk.RHOPI
ALLOWED = {a: -math.log2(kk.PD[a] / 32) for a in range(32) if kk.PD[a]}
ALLOWED[0] = 0.0


def row_forms(a5):
    """returns (dim, forms) ; forms[(z)] = list of 5 (coef_int, const_bit) for plane-0 row z bits x=0..4."""
    rw = kk.rows(a5)
    base_set, dirs = set(), []
    for (y, z), v in rw.items():
        b0, basis = row_affine(v)
        base_set ^= kk.unrows({(y, z): b0})
        for u in basis:
            dirs.append(kk.unrows({(y, z): u}))
    coef = {}  # (x, z) -> int over directions
    for j, d in enumerate(dirs):
        for i in kk.L_set(d):
            x, y, z = kk.xyz(i)
            if y == 0:
                coef[(x, z)] = coef.get((x, z), 0) ^ (1 << j)
    const = {}
    for i in kk.L_set(base_set):
        x, y, z = kk.xyz(i)
        if y == 0:
            const[(x, z)] = const.get((x, z), 0) ^ 1
    forms = {z: [(coef.get((x, z), 0), const.get((x, z), 0)) for x in range(5)] for z in range(64)}
    return len(dirs), forms


def feasible(forms, budget=200000):
    """DFS over plane-0 rows; each row value must be in ALLOWED.  Linear system kept in echelon form.
    Returns (min_cost or inf, nodes) ; stops early at the first solution of cost <= 2*rows? no: full min."""
    rows = sorted(forms, key=lambda z: -sum(1 for c, k in forms[z] if c))
    best = [math.inf]
    nodes = [0]

    def reduce(piv, c, k):
        while c:
            p = c.bit_length() - 1
            if p not in piv:
                return c, k
            pc, pk = piv[p]
            c ^= pc
            k ^= pk
        return c, k

    def dfs(t, piv, cost):
        nodes[0] += 1
        if nodes[0] > budget or cost >= best[0]:
            return
        if t == len(rows):
            best[0] = cost
            return
        z = rows[t]
        for val, cv in sorted(ALLOWED.items(), key=lambda kv: kv[1]):
            newp = dict(piv)
            ok = True
            for x in range(5):
                c, k = forms[z][x]
                want = (val >> x) & 1
                c, k = reduce(newp, c, k ^ want)
                if c == 0:
                    if k:
                        ok = False
                        break
                else:
                    newp[c.bit_length() - 1] = (c, k)
            if ok:
                dfs(t + 1, newp, cost + cv)
    dfs(0, {}, 0.0)
    return best[0], nodes[0]


if __name__ == "__main__":
    for n in range(lo, hi):
        S = set(D.classes[n])
        a3 = {PI[i] for i in S}
        mids = [b for b in D.choices(a3) if D.in_kernel(b)]
        stats = dict(b4=0, const_bad=0, dfs_infeasible=0, feasible=0, budget_hit=0)
        best = None
        for b3 in mids:
            a4 = {PI[i] for i in b3}
            if kk.weight(a4) > MAXW4:
                continue
            for b4 in D.choices(a4):
                stats["b4"] += 1
                a5 = kk.L_set(b4)
                dim, forms = row_forms(a5)
                bad = any(all(c == 0 for c, k in forms[z]) and
                          sum(k << x for x, (c, k) in enumerate(forms[z])) not in ALLOWED for z in forms)
                if bad:
                    stats["const_bad"] += 1
                    continue
                cost, nodes = feasible(forms)
                if nodes > 200000:
                    stats["budget_hit"] += 1
                if cost == math.inf:
                    stats["dfs_infeasible"] += 1
                else:
                    stats["feasible"] += 1
                    if best is None or cost < best[0]:
                        best = (cost, kk.weight(a5), dim)
        print(f"class {n}: {stats}  best feasible (digest cost, w5): {best}  [{time.time() - t0:.1f}s]", flush=True)
