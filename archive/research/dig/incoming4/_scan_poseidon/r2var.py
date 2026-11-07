
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

import sys, json, random, copy
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/orchard/lean_r1_fix'))
import poseidon_ref as ref
P = ref.P
R = 2
IDX = [0, 1, 2, 3] + [4 + i for i in range(R)] + [60, 61, 62, 63]
FULL = {0, 1, 2, 3, 60, 61, 62, 63}

def base_spec():
    spec = []
    for pos, idx in enumerate(IDX):
        spec.append(dict(c=list(ref.RC[idx]), e=[5, 5, 5] if idx in FULL else [5, 1, 1],
                         M=[list(r) for r in ref.MDS]))
    return spec

def run(spec, x):
    s = list(x)
    for rd in spec:
        s = [(s[i] + rd['c'][i]) % P for i in range(3)]
        s = [pow(s[i], rd['e'][i], P) if rd['e'][i] != 1 else s[i] for i in range(3)]
        s = [sum(rd['M'][i][j] * s[j] for j in range(3)) % P for i in range(3)]
    return s[0]

def inv(a):
    return pow(a, P - 2, P)

def line_test(spec):
    """canonical lines in the (X0,X1) plane after round-0 S-box layer; returns per j result"""
    r0, r1 = spec[0], spec[1]
    e0 = r0['e']
    K = pow((1 << 65) + r0['c'][2], e0[2], P) if e0[2] != 1 else ((1 << 65) + r0['c'][2]) % P
    M0 = r0['M']
    # y = M0 (X0,X1,K) + c1  (round-1 pre-S-box lanes)
    res = {}
    for j in range(3):
        k, l = [i for i in range(3) if i != j]
        out = dict(j=j)
        # point q with y_k = y_l = 0
        a, b, c, d = M0[k][0], M0[k][1], M0[l][0], M0[l][1]
        det = (a * d - b * c) % P
        if det == 0:
            out['status'] = 'no point (2x2 singular)'; res[j] = out; continue
        rk = (-(r1['c'][k] + M0[k][2] * K)) % P
        rl = (-(r1['c'][l] + M0[l][2] * K)) % P
        q0 = (d * rk - b * rl) * inv(det) % P
        q1 = (-c * rk + a * rl) * inv(det) % P
        dj0, dj1 = M0[j][0], M0[j][1]
        if dj0 == 0 and dj1 == 0:
            out['status'] = 'lane j constant on whole plane: pencil of lines'
            d0, d1 = 1, 1  # take one member
            # a member: any direction; pick one with (M0 d)_k,(M0 d)_l proportional anyway
        else:
            d0, d1 = dj1, (-dj0) % P
        def y(t):
            X0 = (q0 + t * d0) % P; X1 = (q1 + t * d1) % P
            X = [X0, X1, K]
            return [(sum(M0[i][m] * X[m] for m in range(3)) + r1['c'][i]) % P for i in range(3)]
        # check lane j constant, lanes k,l proportional to t
        ys = [y(t) for t in range(1, 5)]
        jconst = len({v[j] for v in ys}) == 1
        e1 = r1['e']
        def z(t):
            v = y(t)
            return [pow(v[i], e1[i], P) if e1[i] != 1 else v[i] for i in range(3)]
        found = None
        for ee in (1, 5, 7, 3):
            W = [pow(t, ee, P) for t in range(1, 5)]
            zs = [z(t) for t in range(1, 5)]
            ok = True
            for lane in range(3):
                # collinearity of (W, z_lane): slopes equal
                s01 = (zs[1][lane] - zs[0][lane]) * inv((W[1] - W[0]) % P) % P
                s12 = (zs[2][lane] - zs[1][lane]) * inv((W[2] - W[1]) % P) % P
                s23 = (zs[3][lane] - zs[2][lane]) * inv((W[3] - W[2]) % P) % P
                if not (s01 == s12 == s23): ok = False
            if ok:
                found = ee; break
        out['jconst'] = jconst
        out['affine_in_tau^e'] = found
        # degree tracker, degrees in the affine variable if found else in tau
        if found is not None:
            deg = [0 if lane == j else 1 for lane in range(3)]
        else:
            deg = [0 if lane == j else 1 for lane in range(3)]
            deg = [deg[i] * (e1[i] if deg[i] else 1) for i in range(3)]
            # (exact degree in tau; lane j constant)
        # exponent bookkeeping as log5 is not integral for e=7; track integer degrees
        def mds_deg(Mx, dg):
            return [max([dg[m] for m in range(3) if Mx[i][m] % P != 0] or [0]) for i in range(3)]
        dg = mds_deg(r1['M'], deg)
        for rd in spec[2:]:
            dg = [dg[i] * rd['e'][i] if dg[i] else 0 for i in range(3)]
            dg = mds_deg(rd['M'], dg)
        out['digest_degree'] = dg[0]
        out['status'] = out.get('status', 'ok')
        res[j] = out
    return res

def summarize(spec, label):
    r = line_test(spec)
    valid = [j for j in r if r[j].get('affine_in_tau^e') is not None and r[j].get('jconst')]
    degs = sorted({r[j]['digest_degree'] for j in valid})
    allr = {j: (r[j].get('status'), r[j].get('jconst'), r[j].get('affine_in_tau^e'), r[j].get('digest_degree')) for j in r}
    return dict(label=label, valid_lines=valid, n_valid=len(valid), digest_degrees=degs, detail=allr)

def mod(spec, edits):
    s = copy.deepcopy(spec)
    for (pos, kind, lane, val) in edits:
        if kind == 'c': s[pos]['c'][lane] = val
        elif kind == 'e': s[pos]['e'][lane] = val
        elif kind == 'Mrow': s[pos]['M'][lane] = val
        elif kind == 'Mid': s[pos]['M'] = val
    return s

if __name__ == '__main__':
    rnd = random.Random(20261012)
    base = base_spec()
    # validation: reproduces reference hash
    ok = True
    for _ in range(5):
        nk, rho = rnd.randrange(P), rnd.randrange(P)
        ok &= run(base, [nk, rho, 1 << 65]) == ref.hash_reduced(nk, rho, 2)
    kat = []
    for ln in open(_hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/orchard/impl/known_answers_reduced.txt')):
        t = ln.split()
        if len(t) >= 5 and t[0] == '2':
            nk, rho = int(t[1]), int(t[2])
            h = int(t[3], 16)  # hex is big-endian or little: test both
            hv = run(base, [nk, rho, 1 << 65])
            kat.append((hv == h, hv.to_bytes(32, 'little').hex() == t[3], hv.to_bytes(32, 'big').hex() == t[3] or hv.to_bytes(32, 'little').hex() == t[4]))
    print('validation vs poseidon_ref:', ok, 'KAT(r=2 lines):', kat)
    out = {'validation': ok, 'kat': kat}
    out['base'] = summarize(base, 'base')
    rm = [[0, 0, 1], [0, 1, 0], [1, 0, 0]]
    ident = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    rr = lambda: [rnd.randrange(1, P) for _ in range(3)]
    V = {}
    # ---- R0 (pos 0), R1 (pos 1)
    for pos in (0, 1):
        for lane in range(3):
            tag = 'R%d.L%d' % (pos, lane)
            if pos == 1 and lane == 2: continue
            # ARC
            V[tag + '.ARC.Q2'] = mod(base, [(pos, 'c', lane, 0)])
            V[tag + '.ARC.Q4'] = mod(base, [(pos, 'c', lane, rnd.randrange(P))])
            # SBOX
            V[tag + '.SBOX.Q2'] = mod(base, [(pos, 'e', lane, 1)])
            V[tag + '.SBOX.Q4'] = mod(base, [(pos, 'e', lane, 7)])
            # MDS row
            V[tag + '.MDS.Q2'] = mod(base, [(pos, 'Mrow', lane, [1 if m == lane else 0 for m in range(3)])])
            V[tag + '.MDS.Q4'] = mod(base, [(pos, 'Mrow', lane, rr())])
    res = {}
    for k, s in V.items():
        res[k] = summarize(s, k)
    out['variants'] = res
    # relabel checks for R0 ARC on lanes 0,1 (input shift) and lane 2
    chk = {}
    for lane in (0, 1):
        s = mod(base, [(0, 'c', lane, 0)])
        good = True
        for _ in range(5):
            nk, rho = rnd.randrange(P), rnd.randrange(P)
            x = [nk, rho, 1 << 65]
            xs = list(x); xs[lane] = (xs[lane] + ref.RC[0][lane]) % P
            good &= run(s, xs) == run(base, x)
        chk['R0.L%d.ARC drop == input shift' % lane] = good
    # R0 S-box lane 0/1 dropped: relabel (nk,rho)->(A,B)
    for lane in (0, 1):
        s = mod(base, [(0, 'e', lane, 1)])
        good = True
        for _ in range(5):
            nk, rho = rnd.randrange(P), rnd.randrange(P)
            x = [nk, rho, 1 << 65]
            # base(x) with lane value v = (x+c)^5 - c  equals s(x') where x'_lane = v (since s adds c then no sbox)
            xs = list(x); v = pow((x[lane] + ref.RC[0][lane]) % P, 5, P); xs[lane] = (v - ref.RC[0][lane]) % P
            good &= run(s, xs) == run(base, x)
        chk['R0.L%d.SBOX drop == bijective relabel (x+c)^5' % lane] = good
    out['relabel_checks'] = chk
    json.dump(out, open(sys.argv[1], 'w'), indent=1)
    print(json.dumps({k: (v['n_valid'], v['digest_degrees']) for k, v in res.items()}))
    print('base', out['base']['n_valid'], out['base']['digest_degrees'], 390625)
    print(chk)
