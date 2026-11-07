"""Cost of chi5 + the digest round after the theta6 spread, DDS middle placement (COMPUTED).

C(a5) = -log2 P(digest collision | chi5 input difference a5), b5 uniform on S(a5), chi6 values uniform.
P = E_b5 [ prod over the 64 plane-0 rows R of PD(V_R)/32 ],  V_R affine in b5.
Rigorous lower bound C_lb: choose rows greedily whose non-constant bit forms are jointly linearly independent;
  on those rows the variable bits are independent and uniform, so P <= prod E[f_R] (other factors <= 1).
Estimate C_est: the same sum over ALL touched rows as if independent (heuristic, GUESS-grade).
Family total for one mid: P = 2^-w3 * avg_b4 P(coll | L(b4)) ; reported with the max over b4 (rigorous for the
family: avg <= max) and the 64 kernel-keeping mids summed (+6 bits at most).
Usage: python dds8.py <first_class> <last_class_exclusive> [max_w4=13]"""
import sys
import math
import time
import kk
import dds2 as D
from dds6 import row_forms

t0 = time.time()
lo, hi = int(sys.argv[1]), int(sys.argv[2])
MAXW4 = int(sys.argv[3]) if len(sys.argv) > 3 else 13
PI = kk.RHOPI


def row_expect(f):
    """E[PD(V)/32] for one row with forms f = [(coef, const)]*5, treating its variable bits as independent
    uniform (exact when its non-constant forms are linearly independent)."""
    var = [x for x in range(5) if f[x][0]]
    const = sum(f[x][1] << x for x in range(5) if not f[x][0])
    tot = 0.0
    for m in range(1 << len(var)):
        v = const
        for t, x in enumerate(var):
            if (m >> t) & 1:
                v |= 1 << x
        tot += kk.PD[v] / 32
    return tot / (1 << len(var))


def bounds(a5):
    dim, forms = row_forms(a5)
    items = []
    for z, f in forms.items():
        e = row_expect(f)
        if e == 0:
            return math.inf, math.inf, dim
        c = -math.log2(e)
        if c > 0:
            items.append((c, z, f))
    est = sum(c for c, z, f in items)
    items.sort(key=lambda t: -t[0])
    piv = {}
    lb = 0.0
    for c, z, f in items:
        trial = dict(piv)
        ok = True
        for x in range(5):
            v = f[x][0]
            if not v:
                continue
            while v:
                p = v.bit_length() - 1
                if p in trial:
                    v ^= trial[p]
                else:
                    trial[p] = v
                    break
            if not v:
                ok = False
                break
        if ok:
            piv = trial
            lb += c
    return lb, est, dim


if __name__ == "__main__":
    for n in range(lo, hi):
        S = set(D.classes[n])
        a3 = {PI[i] for i in S}
        w3 = kk.weight(a3)
        mids = [b for b in D.choices(a3) if D.in_kernel(b)]
        best_lb, best_est, cnt = math.inf, math.inf, 0
        for b3 in mids:
            a4 = {PI[i] for i in b3}
            if kk.weight(a4) > MAXW4:
                continue
            for b4 in D.choices(a4):
                cnt += 1
                lb, est, dim = bounds(kk.L_set(b4))
                if lb < best_lb:
                    best_lb = lb
                if est < best_est:
                    best_est = est
        print(f"class {n}: {cnt} chi4-output cases (mids with w4<={MAXW4}); min over b4 of C_lb = {best_lb:.1f}, "
              f"of C_est = {best_est:.1f}  ->  family T >= {w3} + {best_lb:.1f} - 6 = {w3 + best_lb - 6:.1f} (rigorous), "
              f"T ~ {w3} + {best_est:.1f} = {w3 + best_est:.1f} (estimate, single best path)  [{time.time() - t0:.1f}s]",
              flush=True)
