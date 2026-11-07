
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

import sys, os, random, subprocess, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tests'))
import flint
from fh import P, R, X, write_poly, read_poly, coeffs
HERE = os.path.dirname(os.path.abspath(__file__))
WSL = _hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/certb_fast/minpoly')
os.makedirs(os.path.join(HERE, 'data'), exist_ok=True)

def run_mp(Fbin, out, seed=1):
    sh = os.path.join(HERE, '_run.sh')
    open(sh, 'w', newline='\n').write('#!/bin/bash\ncd %s\nnice -n 10 ./mp --F %s --out %s --seed %d\n' % (WSL, Fbin, out, seed))
    r = subprocess.run(['wsl', 'bash', WSL + '/_run.sh'], capture_output=True, text=True)
    last = [l for l in r.stdout.splitlines() if '"result"' in l]
    if not last:
        print(r.stdout, r.stderr); raise SystemExit('mp failed')
    import json
    return json.loads(last[0])

def make_random(n, rng):
    return R([rng.randrange(P) for _ in range(n + 1)])

def make_planted(n, rng):
    D = n - 1
    us = [rng.randrange(P) for _ in range(D - 1)]
    Q = R([1])
    for u in us: Q = Q * R([-u % P, 1])
    QI = Q.integral(); XQI = (Q * X).integral()
    u1, u2 = us[0], us[1]
    I0 = (QI(u1) - QI(u2)); I1 = (XQI(u1) - XQI(u2))
    t = I1 / I0
    Fp = Q * R([-int(t) % P, 1])
    F = Fp.integral() + R([rng.randrange(P)])
    return F

def make_even(n, rng):
    G = [rng.randrange(P) for _ in range(n // 2 + 1)]
    c = [0] * (n + 1)
    for i, v in enumerate(G): c[2 * i] = v
    return R(c)

def ref_distinct_count(F):
    D = F.degree() - 1
    Fp = F.derivative()
    pts = list(range(D + 1))
    ys = []
    for j in pts:
        ys.append(int(Fp.resultant(R([j]) - F)))
    # Lagrange: M(T) = prod (T - j)
    M = R([1])
    for j in pts: M = M * R([-j % P, 1])
    fact = [1]
    for i in range(1, D + 2): fact.append(fact[-1] * i % P)
    Rt = R([0])
    for j in pts:
        den = fact[j] * fact[D - j] % P
        if (D - j) % 2: den = (-den) % P
        wj = pow(den, -1, P)
        Rt = Rt + (M.exact_division(R([-j % P, 1]))) * (ys[j] * wj % P)
    assert Rt.degree() == D, Rt.degree()
    return Rt.degree(), Rt.radical().degree(), Rt.is_squarefree()

def check_annihilator(F, out):
    D = F.degree() - 1
    g = F.derivative().monic()
    fr = R(read_poly(out + '_fr.bin'))
    C = read_poly(out + '_C.bin')
    L = len(C) - 1
    Q = R([C[L - i] for i in range(L + 1)])
    return Q.compose_mod(fr, g) == R([0])

def check_seq(F, out, ks):
    D = F.degree() - 1
    g = F.derivative().monic()
    fr = R(read_poly(out + '_fr.bin')); w = read_poly(out + '_w.bin'); s = read_poly(out + '_s.bin')
    ok = True
    for k in ks:
        a = fr.pow_mod(k, g) if k > 0 else R([1])
        cf = coeffs(a) if a.degree() >= 0 else []
        exp = sum(w[i] * cf[i] for i in range(len(cf))) % P
        ok = ok and (exp == s[k])
    return ok

if __name__ == '__main__':
    rng = random.Random(77)
    cases = []
    for n in (26, 126, 626):
        cases.append(('random', n, make_random(n, rng)))
        cases.append(('planted1', n, make_planted(n, rng)))
    cases.append(('even', 26, make_even(26, rng)))
    cases.append(('even', 126, make_even(126, rng)))
    for kind, n, F in cases:
        D = n - 1
        assert F.degree() == n
        fb = 'data/F_%s_%d.bin' % (kind, n)
        write_poly(os.path.join(HERE, fb), coeffs(F))
        t = time.time()
        res = run_mp(fb, 'data/o_%s_%d' % (kind, n))
        res2 = run_mp(fb, 'data/o2_%s_%d' % (kind, n), seed=2)
        dD, rad, sqf = ref_distinct_count(F)
        ann = check_annihilator(F, os.path.join(HERE, 'data/o_%s_%d' % (kind, n)))
        sq = check_seq(F, os.path.join(HERE, 'data/o_%s_%d' % (kind, n)), [0, 1, 2, 5, 2 * D - 1, 3 * D // 2])
        print('%-9s n=%4d D=%4d  gpu_deg=%d,%d  ref_distinct_values=%d  ref_squarefree=%s  annihilates=%s  seq_ok=%s  match=%s  (%.1fs)' % (
            kind, n, D, res['degree'], res2['degree'], rad, sqf, ann, sq, res['degree'] == rad == res2['degree'], time.time() - t), flush=True)
