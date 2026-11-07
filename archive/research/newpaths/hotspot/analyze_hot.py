#!/usr/bin/env python3
"""analyze_hot.py (hotspot; research only) - density of each partial event over each search parameter (bits) and over
pairs of parameter bits, against the null rate (uniform trial sample of the same run), with cluster-robust z (events
cluster by outer step). Discovery / held-out split FIXED BEFORE LOOKING: discovery = thread id even, held-out = odd.
  python -B analyze_hot.py out/h_sub.bin [out/h_all.bin ...]   -> prints the report (redirect to a .txt)
"""
import os, sys
import numpy as np
from ref import F, load, CM

K_NULL, K_TAU, K_RULE, K_ETA, K_OUT, K_E3, K_RZ, K_HW = 1, 2, 4, 8, 16, 32, 64, 128
B_LT, B_LO, B_RA, B_GA, B_E3, B_ETA, B_EARLY, B_RZ = 16, 17, 18, 19, 20, 21, 22, 23
CMASK = 0x03cf8303
Z_DISC, Z_HELD = 5.0, 3.0           # hot spot: |z| >= 5 on discovery, same sign |z| >= 3 on held-out (stated before looking)
PAIR_Z = 6.0
rng = np.random.default_rng(12345)


def free_bits(mask):
    return [b for b in range(32) if not (mask >> b) & 1]


def build_features(R, sub):
    cols, names, group = [], [], []

    def add(word, bits, label, grp):
        for b in bits:
            cols.append((R[:, F[word]] >> np.uint32(b)) & np.uint32(1))
            names.append(f'{label}[{b}]')
            group.append(grp)
    add('c1', free_bits(CM), 'c1', 'inner')
    add('i', range(12), 'i', 'inner')
    add('T0', range(32), 'T0', 'inner')
    e1free = [b for b in free_bits(CMASK) if not (sub and b in (21, 26))]
    add('e1', e1free, 'e1', 'Y4')
    for w in ('C0d1', 'D2a1', 'D2b1', 'S11', 'S4', 'X9', 'w6'):
        add(w, range(32), w, 'basis')
    for w in ('Y12', 'KY', 'C2b', 'C2c', 'C2a', 'C2d', 'K0d', 'w5', 'Y9', 'w8'):
        add(w, range(32), w, 'outer')
    for w in ('d1', 'a1', 'y6', 'y14', 'h1'):
        add(w, range(32), w, 'internal')
    X = np.stack(cols, axis=1).astype(np.uint8)
    return X, names, group


def events(R):
    f = R[:, 0]
    ev = lambda b: ((f >> np.uint32(b)) & 1).astype(bool)
    k = lambda m: (f & np.uint32(m)) != 0
    e3code = (R[:, 1] >> np.uint32(8)) & np.uint32(0xFF)
    return {
        'listed tau (sample)': k(K_TAU),
        'rule A (sample)': k(K_RULE),
        'eta condition (sample)': k(K_ETA),
        'listed E1 outcome': k(K_OUT),
        'E1 outcome & rule A': k(K_OUT) & ev(B_RA),
        'listed partial E3': k(K_E3),
        'partial E3 eps(beta*)': k(K_E3) & (e3code == 2),
        'partial E3 & rule A': k(K_E3) & ev(B_RA),
        'residual word 0 zero': k(K_RZ) & ev(B_RZ),
        'residual word 1 zero': k(K_RZ) & ev(B_RZ + 1),
        'residual word 2 zero': k(K_RZ) & ev(B_RZ + 2),
        'residual word 3 zero': k(K_RZ) & ev(B_RZ + 3),
        'HW(R) <= 23': k(K_HW),
    }


def cluster_key(R):
    ol = R[:, F['olaunch']].astype(np.int64)
    return ((ol >> 8) << 24) | (R[:, F['tid']].astype(np.int64) << 5) | (ol & 0xFF)


def robust_z(Xe, keys, p0, n0):
    """z of sum(bit) against n*p0, variance = sum over outer-step clusters of squared residuals + null-sample term"""
    n = len(Xe)
    order = np.argsort(keys, kind='stable')
    ks = keys[order]
    starts = np.flatnonzero(np.r_[True, ks[1:] != ks[:-1]])
    var = np.zeros(Xe.shape[1])
    k = Xe.sum(axis=0, dtype=np.float64)
    for j0 in range(0, Xe.shape[1], 64):
        blk = Xe[order, j0:j0 + 64].astype(np.float32) - p0[j0:j0 + 64].astype(np.float32)
        s = np.add.reduceat(blk, starts, axis=0).astype(np.float64)
        var[j0:j0 + 64] = (s * s).sum(axis=0)
    c = len(starts)
    var *= c / max(c - 1, 1)
    var += n * n * p0 * (1 - p0) / n0
    with np.errstate(divide='ignore', invalid='ignore'):
        z = (k - n * p0) / np.sqrt(var)
    return z, k / max(n, 1), c


def clusters_summary(keys):
    _, cnt = np.unique(keys, return_counts=True)
    return len(cnt), int(cnt.max()) if len(cnt) else 0, float((cnt[cnt >= 2]).sum() / max(cnt.sum(), 1))


def pair_scan(Xe, Xn, names, top=8):
    """2x2 cells of all bit pairs: raw z (cell against null) and residual z (cell against null x marginal enrichments)"""
    Xe = Xe.astype(np.float32); Xn = Xn.astype(np.float32)
    n, n0 = len(Xe), len(Xn)
    pe, p0 = Xe.mean(0), Xn.mean(0)
    E11 = Xe.T @ Xe / n; N11 = Xn.T @ Xn / n0
    out = []
    for (u, v) in ((1, 1), (1, 0), (0, 1), (0, 0)):
        if (u, v) == (1, 1):
            e, q = E11, N11
        elif (u, v) == (1, 0):
            e, q = pe[:, None] - E11, p0[:, None] - N11
        elif (u, v) == (0, 1):
            e, q = pe[None, :] - E11, p0[None, :] - N11
        else:
            e, q = 1 - pe[:, None] - pe[None, :] + E11, 1 - p0[:, None] - p0[None, :] + N11
        ma = (pe if u else 1 - pe) / np.maximum(p0 if u else 1 - p0, 1e-9)
        mb = (pe if v else 1 - pe) / np.maximum(p0 if v else 1 - p0, 1e-9)
        q = np.clip(q, 1e-9, 1)
        qm = np.clip(q * ma[:, None] * mb[None, :], 1e-9, 1)
        zr = (e - q) * n / np.sqrt(n * q * (1 - q) + n * n * q * (1 - q) / n0)
        zi = (e - qm) * n / np.sqrt(n * qm * (1 - qm) + n * n * qm * (1 - qm) / n0)
        iu = np.triu_indices(len(names), 1)
        for arr, kind in ((zr, 'raw'), (zi, 'beyond-marginals')):
            vals = arr[iu]
            idx = np.argsort(-np.abs(vals))[:top]
            for t in idx:
                a, b = iu[0][t], iu[1][t]
                out.append((kind, abs(vals[t]), vals[t], names[a], u, names[b], v, float(e[a, b] / q[a, b])))
    return out


def run(path):
    R = load(path)
    sub = bool(((R[:, F['e1']] & np.uint32(0x04200000)) == 0).all())
    txt = path[:-4] + '.txt'
    finished = os.path.exists(txt) and 'RUN' in open(txt).read()
    launch = R[:, F['olaunch']] >> np.uint32(8)
    nl = int(launch.max()) + 1
    if not finished:      # drop the launch that may have been cut by the timeout
        keep = launch < nl - 1
        R, nl = R[keep], nl - 1
    trials = nl * 2 ** 33
    print(f'===== {os.path.basename(path)}: {"sub-class" if sub else "whole eta class"}; launches {nl}; trials 2^{np.log2(trials):.2f};'
          f' records {len(R)}; finished={finished}')
    X, names, group = build_features(R, sub)
    EV = events(R)
    null = (R[:, 0] & K_NULL) != 0
    keys = cluster_key(R)
    half = (R[:, F['tid']] & 1).astype(bool)          # False = discovery, True = held-out
    p0 = {h: X[null & (half == h)].mean(0).astype(np.float64) for h in (False, True)}
    n0 = {h: int((null & (half == h)).sum()) for h in (False, True)}
    print(f'null sample: discovery {n0[False]}, held-out {n0[True]}')
    var_ok = (p0[False] > 0.002) & (p0[False] < 0.998)
    res = {}
    for ename, m in EV.items():
        md, mh = m & ~half, m & half
        nd, nh = int(md.sum()), int(mh.sum())
        if nd < 10:
            print(f'\n-- {ename}: discovery n={nd}, held-out n={nh} (too few to map)')
            continue
        idx = np.flatnonzero(md)
        if len(idx) > 150000:
            idx = np.sort(rng.choice(idx, 150000, replace=False))
        zd, fd, cd = robust_z(X[idx], keys[idx], p0[False], n0[False])
        idh = np.flatnonzero(mh)
        if len(idh) > 150000:
            idh = np.sort(rng.choice(idh, 150000, replace=False))
        zh, fh, ch = robust_z(X[idh], keys[idh], p0[True], n0[True]) if len(idh) else (np.zeros_like(zd), zd * 0, 0)
        ncl, mx, frac2 = clusters_summary(keys[m])
        print(f'\n-- {ename}: discovery n={nd} ({cd} outer steps), held-out n={nh}; all: {ncl} outer steps, max per step {mx},'
              f' share in steps with >=2 events {frac2:.3f}')
        zd = np.where(var_ok, zd, 0)
        order = np.argsort(-np.abs(zd))
        hot = []
        for j in order[:12]:
            e_d = fd[j] / p0[False][j] if zd[j] > 0 else (1 - fd[j]) / (1 - p0[False][j])
            e_h = fh[j] / p0[True][j] if zd[j] > 0 else (1 - fh[j]) / (1 - p0[True][j])
            v = 1 if zd[j] > 0 else 0
            conf = abs(zd[j]) >= Z_DISC and np.sign(zh[j]) == np.sign(zd[j]) and abs(zh[j]) >= Z_HELD
            if conf:
                hot.append((names[j], v))
            print(f'   {names[j]:10s} [{group[j]:8s}] ={v}: P(bit|E) {fd[j]:.3f} vs null {p0[False][j]:.3f}; enrich x{e_d:.2f}'
                  f' z {zd[j]:+7.1f} | held-out x{e_h:.2f} z {zh[j]:+6.1f}{"  CONFIRMED" if conf else ""}')
        nsig = int((np.abs(zd) >= Z_DISC).sum())
        grp_sig = {}
        for j in np.flatnonzero(np.abs(zd) >= Z_DISC):
            grp_sig[group[j]] = grp_sig.get(group[j], 0) + 1
        print(f'   bits with |z|>={Z_DISC} on discovery: {nsig} of {int(var_ok.sum())}; by group {grp_sig}')
        res[ename] = dict(zd=zd, zh=zh, fd=fd, fh=fh, hot=hot, md=md, mh=mh)
    return R, X, names, group, EV, null, half, keys, p0, n0, res, trials


def region_eval(X, names, lits, m, null_m):
    sel = np.ones(len(X), bool)
    for (nm, v) in lits:
        j = names.index(nm)
        sel &= X[:, j] == v
    f = sel[null_m].mean() if null_m.sum() else float('nan')
    pe = sel[m].mean() if m.sum() else float('nan')
    n = int(m.sum())
    g = pe / f if f > 0 else float('nan')
    zz = (pe - f) * n / np.sqrt(n * f * (1 - f)) if n and 0 < f < 1 else float('nan')
    return g, f, n, int((sel & m).sum()), zz


def greedy(X, names, group, m_d, null_d, keys, groups_allowed, depth=4, fmin=2 ** -10):
    lits = []
    sel_e = m_d.copy(); sel_n = null_d.copy()
    allowed = np.array([g in groups_allowed for g in group])
    for _ in range(depth):
        ne, nn = sel_e.sum(), sel_n.sum()
        if ne < 30 or nn < 200:
            break
        pe = X[sel_e].mean(0); pn = X[sel_n].mean(0)
        best = None
        for v in (1, 0):
            a = pe if v else 1 - pe
            b = pn if v else 1 - pn
            with np.errstate(divide='ignore', invalid='ignore'):
                z = (a - b) * ne / np.sqrt(ne * b * (1 - b))
                lg = np.log2(np.where(b > 0, a / b, 0))
            ok = allowed & (z >= Z_DISC + 1) & (b * sel_n.mean() * null_d.sum() / max(null_d.sum(), 1) >= 0)
            # fraction kept overall after adding this literal
            fk = b * (nn / null_d.sum())
            ok &= fk >= fmin
            if not ok.any():
                continue
            j = int(np.argmax(np.where(ok, lg, -1e9)))
            if best is None or lg[j] > best[0]:
                best = (lg[j], j, v)
        if best is None:
            break
        _, j, v = best
        lits.append((names[j], v))
        sel_e &= X[:, j] == v; sel_n &= X[:, j] == v
    return lits


if __name__ == '__main__':
    paths = sys.argv[1:] or ['out/h_sub.bin', 'out/h_all.bin']
    for p in paths:
        if not os.path.exists(p):
            continue
        R, X, names, group, EV, null, half, keys, p0, n0, res, trials = run(p)
        # pairs (discovery only, then the top cells re-tested on held-out)
        print('\n== pairs of parameter bits (discovery; search parameters only: inner, Y4, basis, outer words)')
        sp = [j for j, g in enumerate(group) if g != 'internal']
        spn = [names[j] for j in sp]
        Xs = X[:, sp]
        for ename in ('listed E1 outcome', 'listed partial E3', 'eta condition (sample)', 'residual word 1 zero', 'HW(R) <= 23',
                      'listed tau (sample)', 'rule A (sample)', 'residual word 0 zero'):
            if ename not in res:
                continue
            md = res[ename]['md']
            idx = np.flatnonzero(md)
            if len(idx) > 40000:
                idx = rng.choice(idx, 40000, replace=False)
            nd = np.flatnonzero(null & ~half)
            if len(nd) > 120000:
                nd = rng.choice(nd, 120000, replace=False)
            out = pair_scan(Xs[idx], Xs[nd], spn, top=4)
            print(f'-- {ename} (n={len(idx)}):')
            seen = set()
            for kind, az, zz, a, u, b, v, enr in sorted(out, key=lambda t: -t[1])[:10]:
                key = (kind, a, u, b, v)
                if key in seen:
                    continue
                seen.add(key)
                g_h, f_h, n_h, k_h, z_h = region_eval(X, names, [(a, u), (b, v)], res[ename]['mh'], null & half)
                print(f'   {kind:16s} {a}={u} & {b}={v}: z {zz:+6.1f} enrich x{enr:.2f} | held-out x{g_h:.2f} (z {z_h:+5.1f}, f {f_h:.3f})')
        # greedy conjunction hot spots on search parameters, discovery -> held-out, and cross-check on other events
        print('\n== greedy hot spots (conjunctions of up to 4 bit conditions on SEARCH parameters; chosen on discovery, measured on held-out)')
        for ename in ('listed partial E3', 'listed E1 outcome', 'eta condition (sample)', 'listed tau (sample)', 'rule A (sample)',
                      'residual word 1 zero', 'residual word 0 zero', 'HW(R) <= 23'):
            if ename not in res:
                continue
            for grps, lab in (({'inner', 'Y4', 'basis', 'outer'}, 'any search parameter'), ({'inner'}, 'inner only (c1, i, T0)')):
                lits = greedy(X, names, group, res[ename]['md'], null & ~half, keys, grps)
                if not lits:
                    print(f'-- {ename} [{lab}]: no literal passes z >= {Z_DISC + 1} with fraction >= 2^-10')
                    continue
                g_d, f_d, _, _, z_d = region_eval(X, names, lits, res[ename]['md'], null & ~half)
                g_h, f_h, n_h, k_h, z_h = region_eval(X, names, lits, res[ename]['mh'], null & half)
                print(f'-- {ename} [{lab}]: {" & ".join(f"{a}={v}" for a, v in lits)}')
                print(f'   discovery: gain x{g_d:.2f} at fraction {f_d:.4f} (2^{np.log2(f_d):.2f}); held-out: gain x{g_h:.2f}'
                      f' (2^{np.log2(max(g_h, 1e-9)):.2f}), fraction {f_h:.4f}, {k_h}/{n_h} events inside, z {z_h:+.1f}')
                for other in EV:
                    if other == ename:
                        continue
                    mo = EV[other] & half
                    if mo.sum() < 5:
                        continue
                    g_o, f_o, n_o, k_o, z_o = region_eval(X, names, lits, mo, null & half)
                    print(f'      held-out {other:26s}: gain x{g_o:6.2f} ({k_o}/{n_o} inside, z {z_o:+.1f})')
        # naive-Bayes score over the bits of OUTER-step parameters (Y4 member, basis words, outer words) trained on
        # discovery, then gain at keep fractions on held-out, for the event itself and for the other events
        print('\n== outer-step score (per-bit log ratios of bits with |z|>=4 on discovery; outer-step parameters only)'
              '\n   gain = P(score in top q | event) / q on HELD-OUT data, q = kept fraction of outer steps')
        outer_j = np.array([g in ('Y4', 'basis', 'outer') for g in group])
        qs = [2 ** -k for k in (1, 2, 3, 4, 6, 8, 10)]
        for ename in ('listed partial E3', 'listed E1 outcome', 'eta condition (sample)', 'listed tau (sample)', 'rule A (sample)',
                      'residual word 1 zero', 'HW(R) <= 23'):
            if ename not in res:
                continue
            zd, fd = res[ename]['zd'], res[ename]['fd']
            sel = outer_j & (np.abs(zd) >= 4)
            if not sel.any():
                print(f'-- {ename}: no outer-step bit with |z| >= 4 on discovery')
                continue
            pn = np.clip(p0[False], 1e-4, 1 - 1e-4); pe = np.clip(fd, 1e-4, 1 - 1e-4)
            w1, w0 = np.log2(pe / pn), np.log2((1 - pe) / (1 - pn))
            js = np.flatnonzero(sel)
            sc = (X[:, js] * w1[js] + (1 - X[:, js]) * w0[js]).sum(1)
            sn = np.sort(sc[null & half])
            line = []
            for other in [ename] + [o for o in EV if o != ename]:
                mo = EV[other] & half
                if mo.sum() < 5:
                    continue
                gl = []
                for q in qs:
                    thr = sn[int((1 - q) * len(sn))] if len(sn) else 0
                    kept = (sc[mo] >= thr).mean()
                    qq = (sn >= thr).mean()
                    gl.append(f'{kept / max(qq, 1e-12):6.2f}')
                line.append(f'   {other:26s} (n={int(mo.sum()):6d}): ' + ' '.join(gl))
            print(f'-- score of {ename} on {len(js)} bits ({", ".join(sorted({names[j].split("[")[0] for j in js}))});'
                  f' gains at q = 1/2 1/4 1/8 1/16 1/64 1/256 1/1024:')
            print('\n'.join(line))
        # per-value maps of the inner index, counter t and c1 sub-cube (chi-square against the null distribution)
        print('\n== value maps (all data): chi-square of the event distribution against the null sample')
        nul = null
        vals = {
            'inner index i (16 bins)': (R[:, F['i']] >> np.uint32(8)).astype(int),
            'counter t: floor(log2 t) (bins 0..31)': np.floor(np.log2(np.maximum(R[:, F['T0']], 1))).astype(int),
            'counter t: top 4 bits': (R[:, F['T0']] >> np.uint32(28)).astype(int),
            'c1 top 5 free bits (sub-cube)': ((R[:, F['c1']] >> np.uint32(28)) & np.uint32(0xF)).astype(int) * 2 + ((R[:, F['c1']] >> np.uint32(24)) & np.uint32(1)).astype(int),
        }
        for ename in ('listed E1 outcome', 'listed partial E3', 'eta condition (sample)', 'listed tau (sample)', 'rule A (sample)',
                      'residual word 1 zero', 'HW(R) <= 23', 'E1 outcome & rule A'):
            m = EV[ename]
            if m.sum() < 20:
                continue
            line = []
            for vn, v in vals.items():
                nb = int(v.max()) + 1
                pn = np.bincount(v[nul], minlength=nb) / nul.sum()
                ce = np.bincount(v[m], minlength=nb)
                ok = pn * m.sum() >= 5
                ex = pn[ok] * m.sum()
                chi = float(((ce[ok] - ex) ** 2 / ex).sum())
                df = int(ok.sum()) - 1
                zc = (chi - df) / np.sqrt(2 * df) if df > 0 else float('nan')
                line.append(f'{vn}: chi2 {chi:.0f}/{df} (z {zc:+.1f})')
            print(f'-- {ename} (n={int(m.sum())}): ' + '; '.join(line))
        print(f'\ntrials in this file: 2^{np.log2(trials):.2f}')
