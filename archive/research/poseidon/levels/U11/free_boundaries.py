"""U11 real field: how many level boundaries can be forced to 'equal lane 0' by one univariate root-finding?
Pair (A,B),(A',t): lane 0 after level k is a polynomial in t of degree 5^k. Roots via gcd(t^p - t, f).
Single process. Usage: python free_boundaries.py r maxlevel_index trials_csv
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

import sys, time, random
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/orchard/impl'))
import poseidon_ref as H
from flint import fmpz_mod_ctx, fmpz_mod_poly_ctx
P = H.P; RC = H.RC; MDS = H.MDS
ctx = fmpz_mod_ctx(P); pctx = fmpz_mod_poly_ctx(ctx)
X = pctx.gen()
D5 = pow(5, -1, P - 1)
K = pow((H.CAPACITY + RC[0][2]) % P, 5, P)

def rounds_for(r): return list(range(1, 4)) + list(range(4, 4 + r)) + list(range(60, 64))

def apply_round_poly(st, idx):
    full = idx < 4 or idx >= 60
    st = [st[i] + RC[idx][i] for i in range(3)]
    for i in (range(3) if full else range(1)):
        st[i] = st[i].pow_mod(5, X ** (st[i].degree() * 5 + 2)) if False else st[i] ** 5
    return [st[0] * MDS[i][0] + st[1] * MDS[i][1] + st[2] * MDS[i][2] for i in range(3)]

def lane0_poly_upto(Aprime, r, upto):
    """lane 0 after the round with original index `upto` (upto=0 means after R0.M), as poly in t=B'."""
    st = [X * MDS[i][1] + (MDS[i][0] * Aprime + MDS[i][2] * K) % P for i in range(3)]
    for idx in rounds_for(r):
        if upto == 0: break
        st = apply_round_poly(st, idx)
        if idx == upto: break
    return st[0]

def point_levels(nk, rho, r):
    """states after each round's M for the real hash input."""
    s = [nk, rho, H.CAPACITY]; out = []
    for idx in H.schedule(r):
        s = H.round_full(s, idx) if (idx < 4 or idx >= 60) else H.round_partial(s, idx)
        out.append((idx, list(s)))
    return out

def roots_of(f):
    xp = X.pow_mod(P, f)
    g = (xp - X).gcd(f)
    return g.degree(), g

def main(r, maxidx, trials):
    random.seed(20261012)
    order = [0] + rounds_for(r)
    print(f"# r={r}; level order: {order}")
    for lvl in order:
        if lvl > maxidx and not (60 <= lvl): pass
        ntr = trials.get(lvl, 3)
        if ntr == 0: continue
        degs = []; times = []; found = []
        for tr in range(ntr):
            nk = random.randrange(P); rho = random.randrange(P)
            a = (nk + RC[0][0]) % P; b = (rho + RC[0][1]) % P
            A = pow(a, 5, P); B = pow(b, 5, P)
            lv = point_levels(nk, rho, r)
            tgt = [s for (i, s) in lv if i == lvl][0][0]
            Ap = random.randrange(P)
            t0 = time.time()
            f = lane0_poly_upto(Ap, r, lvl) - tgt
            d = f.degree()
            nroot, g = roots_of(f)
            dt = time.time() - t0
            rts = [int(rt[0]) for rt in g.roots()] if nroot else []
            degs.append((d, nroot)); times.append(dt)
            for Bp in rts:
                nk2 = (pow(Ap, D5, P) - RC[0][0]) % P; rho2 = (pow(Bp, D5, P) - RC[0][1]) % P
                lv2 = point_levels(nk2, rho2, r)
                ok = [s for (i, s) in lv2 if i == lvl][0][0] == tgt
                found.append((ok, (nk2, rho2) != (nk, rho)))
                if tr == 0 and found[-1][0]: pass
        print(f"level R{lvl}: poly degree {degs[0][0]}, trials {ntr}, roots per trial {[n for _, n in degs]}, verified {all(o for o,_ in found)} ({len(found)} pairs), distinct {all(dd for _,dd in found)}, time/trial {sum(times)/len(times):.2f}s", flush=True)

if __name__ == '__main__':
    r = int(sys.argv[1]); maxidx = int(sys.argv[2])
    trials = {int(k): int(v) for k, v in (x.split(':') for x in sys.argv[3].split(','))}
    main(r, maxidx, trials)
