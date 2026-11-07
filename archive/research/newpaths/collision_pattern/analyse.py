#!/usr/bin/env python3
"""analyse.py: do the found toy collisions follow a pattern beyond what the trial construction imposes?
Every test compares the hits with null trials drawn from the SAME runs by the same construction (feat.c):
  N0 = uniform trials of the run (counter arrangement: d1 uniform in its set, t != 0, the run's own filter)
  N1 = (W 8 only) trials weighted by the exact model's collision probability mass[member][E1.d1] / 2^40
Calibration ("CAL"): the same statistic with a pseudo-hit sample taken from N0 itself (one per hit), so the
multiple-comparison spread is measured, not assumed. Output: results.txt
"""
import glob, math, os, re, sys
from collections import Counter, defaultdict
import numpy as np
from scipy import stats
from load import hits, feats, col, HERE

rng = np.random.default_rng(20261008)
OUT = []


def P(*a):
    s = ' '.join(str(x) for x in a)
    OUT.append(s)
    print(s)


H = hits()


def words(a, W, names):
    return {n: col(a, n) for n in names}


def derived(a, W, hi):
    """search parameters of each trial: w5 = outer mod 2^W, S9 = (outer >> W) mod 2^W, x2, member k, u = outer/nouter"""
    g = col(a, 'g')
    nouter = np.array([int(H[i]['nouter']) for i in hi])
    d = dict(x2=g & ((1 << W) - 1), w5o=(g >> W) & ((1 << W) - 1), S9=(g >> (2 * W)) & ((1 << W) - 1),
             u=((g >> W) + 0.5) / nouter, k=col(a, 'k'))
    return d


def bitmat(cols, W, kbits=6):
    mats, names = [], []
    for n, v in cols.items():
        nb = kbits if n == 'k' else W
        for b in range(nb):
            mats.append((v >> b) & 1); names.append(f'{n}.{b}')
    return np.array(mats, dtype=np.int8).T, names


def neff(wn, n):
    return n if wn is None else wn.sum() ** 2 / (wn ** 2).sum()


def ztest_bits(Bh, Bn, wn=None):
    ph = Bh.mean(0)
    pn = Bn.mean(0) if wn is None else (wn[:, None] * Bn).sum(0) / wn.sum()
    nh, nn = len(Bh), neff(wn, len(Bn))
    v = pn * (1 - pn) * (1 / nh + 1 / nn)
    with np.errstate(divide='ignore', invalid='ignore'):
        z = np.where(v > 0, (ph - pn) / np.sqrt(v), 0.0)
    return z


def ztest_pairs(Bh, Bn, wn=None):
    """bias of every XOR of two bits (order-2 linear relations over GF(2))"""
    def xor_means(B, w=None):
        B = B.astype(np.float64)
        w = np.ones(len(B)) if w is None else w / w.mean()
        p = (w[:, None] * B).mean(0)
        E = (B * w[:, None]).T @ B / len(B)
        return p[:, None] + p[None, :] - 2 * E
    xh, xn = xor_means(Bh), xor_means(Bn, wn)
    v = xn * (1 - xn) * (1 / len(Bh) + 1 / neff(wn, len(Bn)))
    with np.errstate(divide='ignore', invalid='ignore'):
        z = np.where(v > 1e-12, (xh - xn) / np.sqrt(v), 0.0)
    iu = np.triu_indices(Bh.shape[1], 1)
    return z[iu], iu


def gf2_rank(B):
    basis = {}
    for row in B:
        x = int(''.join('1' if b else '0' for b in row), 2) if len(row) else 0
        while x:
            hb = x.bit_length() - 1
            if hb in basis:
                x ^= basis[hb]
            else:
                basis[hb] = x
                break
    return len(basis)


def chi2_vs_null(vh, vn, nbins, wn=None):
    ch = np.bincount(vh, minlength=nbins).astype(float)
    if wn is None:
        cn = np.bincount(vn, minlength=nbins).astype(float); ne = cn.sum()
    else:
        ne = neff(wn, len(vn)); cn = np.bincount(vn, weights=wn, minlength=nbins) * ne / wn.sum()
    pn = (cn + 0.5) / (cn.sum() + 0.5 * nbins)
    nh = ch.sum()
    e = nh * pn
    x2 = (((ch - e) ** 2) / (e * (1 + nh / ne))).sum()
    df = nbins - 1
    return x2, df, stats.chi2.sf(x2, df)


def zfromp(p):
    return stats.norm.isf(max(p, 1e-300))


def summarize(label, zs, zcal, ntests):
    zs, zcal = np.abs(zs), np.abs(zcal)
    bonf = 2 * stats.norm.sf(zs.max()) * ntests
    P(f'  {label:<44} tests {ntests:5d}  max|z| {zs.max():5.2f} (CAL {zcal.max():5.2f})  #|z|>4 {int((zs > 4).sum()):3d} '
      f'(CAL {int((zcal > 4).sum())})  Bonferroni p {min(1.0, bonf):.2g}')


def family_tests(name, W, h, n, ncal, hi, ni, cali, wn=None, groups_only=None):
    """h, n: feature arrays of hits and null (wn: weights of the null rows); ncal: pseudo-hits drawn from the same
    null; *i: hit numbers (run info)"""
    dh, dn, dc = derived(h, W, hi), derived(n, W, ni), derived(ncal, W, cali)
    msg = ['w0', 'w1', 'w2', 'w3', 'w6', 'w7', 'w8', 'w9', 'w10', 'w11', 'w12']
    internal = ['d1', 'b1', 'a2', 'e1', 'h1', 'Y1', 'Y6', 'Y9', 'Y12', 'Y14']
    groups = {
        'search parameters (w5,S9,X2,member)': lambda a, d: dict(w5o=d['w5o'], S9=d['S9'], x2=d['x2'], k=d['k']),
        'message words (w0..w12 free)': lambda a, d: {m: col(a, m) for m in msg},
        'message words except w8': lambda a, d: {m: col(a, m) for m in msg if m != 'w8'},
        'internal round-2 words (E1,E3 inputs)': lambda a, d: {m: col(a, m) for m in internal},
    }
    if (col(h, 'mode') == 1).any():
        groups['search parameters (w5,S9,X2,member)'] = lambda a, d: dict(w5o=d['w5o'], S9=d['S9'], x2=d['x2'], k=d['k'], t=col(a, 't'), d1=col(a, 'd1'))
    P(f'[{name}] per-bit bias (order 1) and XOR of two bits (order 2, GF(2) relations)')
    for gname, fn in groups.items():
        if groups_only and not any(gname.startswith(g) for g in groups_only):
            continue
        Bh, names = bitmat(fn(h, dh), W); Bn, _ = bitmat(fn(n, dn), W); Bc, _ = bitmat(fn(ncal, dc), W)
        keep = Bn.std(0) > 0
        Bh, Bn, Bc = Bh[:, keep], Bn[:, keep], Bc[:, keep]
        names = [x for x, k in zip(names, keep) if k]
        z1, zc1 = ztest_bits(Bh, Bn, wn), ztest_bits(Bc, Bn, wn)
        summarize(gname + ' bits', z1, zc1, len(z1))
        top = np.argsort(-np.abs(z1))[:4]
        P('     strongest bits: ' + ', '.join(f'{names[i]} z={z1[i]:+.1f}' for i in top))
        z2, iu = ztest_pairs(Bh, Bn, wn); zc2, _ = ztest_pairs(Bc, Bn, wn)
        summarize(gname + ' XOR pairs', z2, zc2, len(z2))
        if wn is None and (gname.startswith('search') or gname.startswith('message words (')):
            m = min(len(Bh), len(Bn))
            rh = gf2_rank(Bh[:m]); rn = gf2_rank(Bn[rng.choice(len(Bn), m, replace=False)])
            rha = gf2_rank(np.hstack([Bh[:m], np.ones((m, 1), np.int8)]))
            rna = gf2_rank(np.hstack([Bn[rng.choice(len(Bn), m, replace=False)], np.ones((m, 1), np.int8)]))
            P(f'     GF(2) rank over {Bh.shape[1]} bits, {m} rows: hits {rh} (affine {rha}), null {rn} (affine {rna})')
    # modular / additive relations between words
    nb = 1 << (min(W, 8) if wn is None else 4)      # weighted null (small effective size): 16 bins
    sh = W - (min(W, 8) if wn is None else 4)
    wl = ['w5o', 'S9', 'x2', 'y4'] + msg
    def wv(a, d, m):
        return d[m] if m in d else col(a, m)
    pv, pc = [], []
    for i in range(len(wl)):
        for j in range(i, len(wl)):
            ops = [('val', None)] if i == j else [('-', None), ('+', None), ('^', None)]
            for op, _ in ops:
                def f(a, d):
                    x, y = wv(a, d, wl[i]), wv(a, d, wl[j])
                    M = (1 << W) - 1
                    r = x if op == 'val' else ((x - y) & M if op == '-' else ((x + y) & M if op == '+' else x ^ y))
                    return (r >> sh).astype(np.int64)
                _, _, p = chi2_vs_null(f(h, dh), f(n, dn), nb, wn)
                _, _, q = chi2_vs_null(f(ncal, dc), f(n, dn), nb, wn)
                pv.append((p, f'{wl[i]}{"" if op == "val" else op + wl[j]}')); pc.append(q)
    pmin = min(pv)
    sig = sorted(x for x in pv if x[0] < 1e-4)
    P(f'[{name}] word values and (a-b, a+b, a^b) mod 2^W, chi-square vs null ({len(pv)} tests, {nb} bins): '
      f'min p {pmin[0]:.2g}, Bonferroni {min(1, pmin[0] * len(pv)):.2g}; p<1e-4: ' +
      (', '.join(f'{nm} {p:.1g}' for p, nm in sig) if sig else 'none') +
      f' (CAL min p {min(pc):.2g}, #p<1e-4 {sum(q < 1e-4 for q in pc)})')
    without_w8 = [x for x in pv if 'w8' not in x[1] and x[1] != 'y4']
    pm2 = min(without_w8)
    P(f'     the same without w8 and the member word y4 ({len(without_w8)} tests): min p {pm2[0]:.2g} ({pm2[1]}), Bonferroni {min(1, pm2[0] * len(without_w8)):.2g}')
    return dh, dn


def member_tests(name, W, h, n0, n1, hi):
    sets_h = col(h, 'set'); kh = col(h, 'k')
    cells = Counter(zip(sets_h, kh))
    def exp_from(n):
        c = Counter(zip(col(n, 'set'), col(n, 'k')))
        tot = Counter(col(n, 'set'))
        nh_set = Counter(sets_h)
        return c, tot, nh_set
    for lab, n in (('N0 (uniform trials)', n0), ('N1 (exact mass model)', n1)):
        if n is None:
            continue
        c, tot, nhs = exp_from(n)
        x2 = 0.0; df = 0
        for s in nhs:
            ks = sorted({k for (ss, k) in c if ss == s} | {k for (ss, k) in cells if ss == s})
            for k in ks:
                e = nhs[s] * (c.get((s, k), 0) + 0.5) / (tot[s] + 0.5 * len(ks))
                o = cells.get((s, k), 0)
                x2 += (o - e) ** 2 / (e * (1 + nhs[s] / tot[s])); df += 1
            df -= 1
        p = stats.chi2.sf(x2, df)
        P(f'[{name}] member index per set vs {lab}: chi-square {x2:.0f} on {df}, p {p:.2g}')


def mass_tests(name, h, n0, n1):
    mh, m0, m1 = col(h, 'mass'), col(n0, 'mass'), col(n1, 'mass')
    P(f'[{name}] exact model cell (member, E1.d1): hits in cells of mass 0: {int((mh == 0).sum())} of {len(mh)}; '
      f'N0 trials in mass-0 cells: {np.mean(m0 == 0):.3f}')
    # within-set normalised mass: hits vs N1 should agree (KS), vs N0 not
    def norm(a, m):
        s = col(a, 'set')
        mu = defaultdict(list)
        for ss, mm in zip(s, m):
            mu[ss].append(mm)
        return m
    ks1 = stats.ks_2samp(mh, m1); ks0 = stats.ks_2samp(mh, m0)
    P(f'   distribution of the cell mass: hits vs N1 KS p {ks1.pvalue:.2g}; hits vs N0 KS p {ks0.pvalue:.2g}')
    # beta structure: share of hits in the heaviest-beta cells is what the counter lever buys
    return


def cluster_and_spacing(name, W, h, hi):
    runs = defaultdict(list)
    for row, i in zip(h, hi):
        r = H[i]
        key = (r['src'], r['W'], r['arr'], r['set'], r['ser'], r['seed'])
        ncls = int(r['ncls']); nmid = int(r['nouter']) << W
        nd = 1
        pos = ((int(col(row[None, :], 'g')[0]) * ncls + int(row[3])) + 0.5) / (nmid * ncls)
        runs[key].append((pos, int(r['outer']), int(col(row[None, :], 'g')[0]), int(r['nouter'])))
    pos = np.array([p for v in runs.values() for p, *_ in v])
    ks = stats.kstest(pos, 'uniform')
    # same outer step / same middle step, observed vs expected (uniform positions)
    same_o = same_g = 0; e_o = e_g = 0.0
    nn, close_obs = [], 0
    for v in runs.values():
        m = len(v)
        if m < 2:
            continue
        no = v[0][3]
        e_o += m * (m - 1) / 2 / no; e_g += m * (m - 1) / 2 / (no << W)
        os_ = Counter(o for _, o, _, _ in v); gs = Counter(g for _, _, g, _ in v)
        same_o += sum(c * (c - 1) // 2 for c in os_.values()); same_g += sum(c * (c - 1) // 2 for c in gs.values())
        ps = np.sort([p for p, *_ in v])
        nn.extend(np.diff(ps) * (m + 1))   # gaps scaled; uniform spacings ~ Exp(1) approx
    # Monte Carlo null for the gaps: same number of points per run, uniform positions
    sims, allsim = [], []
    for rep in range(200):
        g_ = []
        for v in runs.values():
            m = len(v)
            if m >= 2:
                g_.extend(np.diff(np.sort(rng.random(m))) * (m + 1))
        g_ = np.array(g_)
        sims.append(np.mean(g_ < 0.05))
        if rep < 20:
            allsim.append(g_)
    obs_close = np.mean(np.array(nn) < 0.05) if nn else float('nan')
    zc = (obs_close - np.mean(sims)) / (np.std(sims) + 1e-12)
    P(f'[{name}] search order: {len(pos)} hits in {len(runs)} runs; position in run uniform? KS p {ks.pvalue:.2g}; '
      f'pairs in the same outer step {same_o} (expected {e_o:.2f}), same middle step {same_g} (expected {e_g:.3f}); '
      f'close pairs (gap < 0.05 of mean) {obs_close:.4f} vs {np.mean(sims):.4f} (z {zc:+.1f})')
    if nn:
        ksg = stats.ks_2samp(np.array(nn), np.concatenate(allsim))
        P(f'   gaps between consecutive hits in a run vs simulated uniform gaps: KS p {ksg.pvalue:.2g} (n {len(nn)})')


def smooth_pairs(name, W, h, n, ncal, dh, dn, dc, extra=()):
    pairs = [('u', 'x2'), ('u', 'k'), ('x2', 'k'), ('u', 'S9'), ('w5o', 'x2')] + list(extra)
    def getv(a, d, m):
        return d[m] if m in d else col(a, m).astype(float)
    out = []
    for a_, b_ in pairs:
        xh, yh = getv(h, dh, a_), getv(h, dh, b_)
        xn, yn = getv(n, dn, a_), getv(n, dn, b_)
        rh = stats.spearmanr(xh, yh).statistic; rn = stats.spearmanr(xn, yn).statistic
        zr = (np.arctanh(rh) - np.arctanh(rn)) / math.sqrt(1 / (len(xh) - 3) + 1 / (len(xn) - 3))
        # 2-D 8x8 histogram by null quantiles, chi-square vs the null's 2-D histogram
        qx = np.quantile(xn, np.linspace(0, 1, 9)[1:-1]); qy = np.quantile(yn, np.linspace(0, 1, 9)[1:-1])
        ch = np.searchsorted(qx, xh, 'right') * 8 + np.searchsorted(qy, yh, 'right')
        cn = np.searchsorted(qx, xn, 'right') * 8 + np.searchsorted(qy, yn, 'right')
        oh = np.bincount(ch, minlength=64).reshape(8, 8).astype(float)
        e = np.bincount(cn, minlength=64).reshape(8, 8).astype(float) + 0.5
        for _ in range(50):
            e *= (oh.sum(1, keepdims=True) / e.sum(1, keepdims=True))
            e *= (oh.sum(0, keepdims=True) / e.sum(0, keepdims=True))
        ok = e > 0
        x2 = ((oh - e)[ok] ** 2 / e[ok]).sum(); df = int(ok.sum()) - 15
        p = stats.chi2.sf(x2, max(df, 1))
        # best smooth fit: quadratic y ~ x, compare R^2 of hits with the null's
        cfh = np.polyfit(xh, yh, 2); r2h = 1 - np.var(yh - np.polyval(cfh, xh)) / np.var(yh)
        cfn = np.polyfit(xn, yn, 2); r2n = 1 - np.var(yn - np.polyval(cfn, xn)) / np.var(yn)
        out.append(f'{a_}~{b_}: rho {rh:+.3f} (null {rn:+.3f}, z {zr:+.1f}), quad R2 {r2h:.4f} (null {r2n:.4f}), 2-D chi2 p {p:.2g}')
    P(f'[{name}] smooth relations between two parameters:')
    for s in out:
        P('   ' + s)


def within_run():
    """do hits of one run sit closer together than uniform positions would? Monte Carlo with the same number of hits
    per run: span of the hits, and pairs in the same block (absolute 2^12/2^14/2^16 outer steps; 1/2, 1/4, 1/8 run)"""
    groups = [('W=8 server L=0.5', lambda r: r['W'] == '8' and r['src'] == 'T5' and r['ser'] == '0'),
              ('W=8 server L=1.7', lambda r: r['W'] == '8' and r['src'] == 'T5' and r['ser'] == '1'),
              ('W=8 local', lambda r: r['W'] == '8' and r['src'] == 'T5L'),
              ('W=8 counter toy (all)', lambda r: r['src'] == 'CT'),
              ('W=10 server', lambda r: r['W'] == '10' and r['src'] == 'T5')]
    for label, sel in groups:
        runs, meta = defaultdict(list), {}
        for r in H:
            if not sel(r):
                continue
            key = (r['src'], r['arr'], r['set'], r['ser'], r['seed'])
            W = int(r['W']); no = int(r['nouter']); n = int(r['ncls'])
            runs[key].append(int(r['outer']) + (int(r['x2']) * n + int(r['member']) + 0.5) / ((1 << W) * n))
            meta[key] = no
        keys = [k for k in runs if len(runs[k]) >= 2]
        def stat(pd):
            out = {'span': 0.0}
            for k in keys:
                v = np.sort(pd[k]); no = meta[k]; m = len(v)
                out['span'] += (v[-1] - v[0]) / no
                for sc in (12, 14, 16):
                    _, c = np.unique(np.floor(v / (1 << sc)), return_counts=True); out[f'2^{sc}'] = out.get(f'2^{sc}', 0) + int((c * (c - 1) // 2).sum())
                for q in (2, 4, 8):
                    _, c = np.unique(np.floor(v / no * q), return_counts=True); out[f'1/{q}'] = out.get(f'1/{q}', 0) + int((c * (c - 1) // 2).sum())
            return out
        o = stat({k: np.array(runs[k]) for k in keys})
        B = defaultdict(list)
        for _ in range(400):
            for kk, vv in stat({k: rng.random(len(runs[k])) * meta[k] for k in keys}).items():
                B[kk].append(vv)
        P(f'[within-run clustering, {label}] {len(keys)} runs with >=2 hits: ' + '  '.join(
            f'{kk} {o[kk]:.0f}/{np.mean(B[kk]):.0f} z{(o[kk] - np.mean(B[kk])) / (np.std(B[kk]) + 1e-12):+.1f}' for kk in o))


def run_level():
    """run seeds (context words C0.c1, C0.d1, D3.d1, S15) against per-run collision counts: task 5 server runs"""
    T5 = os.path.join(HERE, '..', '..', '..', 'astra-jobs', 'server_tasks_2026-10-06', 'task5_small_h8', 'out')
    for W in (8, 10):
        seeds, obs, exp = [], [], []
        for fn in glob.glob(os.path.join(T5, f'w{W}_set*.txt')):
            for line in open(fn):
                if line.startswith('RUN '):
                    f = line.split()
                    i = f.index('seed')
                    seeds.append([int(x, 16) for x in f[i + 1:i + 5]])
                    obs.append(int(f[f.index('coll') + 1])); exp.append(float(f[f.index('L') + 1]))
        S = np.array(seeds); O = np.array(obs, float); E = np.array(exp)
        E = E * O.sum() / E.sum()          # remove the overall level (3.3% at W 8); test the shape only
        zs, names = [], []
        for wi, wn in enumerate(['C0.c1', 'C0.d1', 'D3.d1', 'S15']):
            for b in range(W):
                m = ((S[:, wi] >> b) & 1) == 1
                zs.append((O[m].sum() - E[m].sum()) / math.sqrt(E[m].sum() * (1 - E[m].sum() / E.sum())))
                names.append(f'{wn}.{b}')
        zs = np.array(zs)
        pv = []
        for wi in range(4):
            bins = S[:, wi] >> (W - 6)
            o = np.bincount(bins, weights=O, minlength=64); e = np.bincount(bins, weights=E, minlength=64)
            pv.append(stats.chi2.sf(((o - e) ** 2 / e).sum(), 63))
        P(f'[run seeds W={W}] {len(O)} runs, {int(O.sum())} collisions: per seed-word bit max|z| {np.abs(zs).max():.2f} '
          f'({names[int(np.abs(zs).argmax())]}), Bonferroni p {min(1, 2 * stats.norm.sf(np.abs(zs).max()) * len(zs)):.2g}; '
          f'per seed-word value (64 bins) chi-square p ' + ', '.join(f'{p:.2g}' for p in pv))
        disp = ((O - E) ** 2 / E).sum() / (len(O) - 1)
        P(f'   per-run count dispersion (shape-only expectation) {disp:.3f}')


def classifier(name, W, h, n, dh, dn, use):
    """naive linear score (log-odds of each bit, fitted on half, tested on the other half): AUC"""
    def B(a, d):
        cols = {}
        for u in use:
            cols[u] = d[u] if u in d else col(a, u)
        return bitmat(cols, W)[0].astype(float)
    Xh, Xn = B(h, dh), B(n, dn)
    ih = rng.permutation(len(Xh)); inn = rng.permutation(len(Xn))
    th, vh = ih[: len(ih) // 2], ih[len(ih) // 2:]; tn, vn = inn[: len(inn) // 2], inn[len(inn) // 2:]
    ph = (Xh[th].sum(0) + 1) / (len(th) + 2); pn = (Xn[tn].sum(0) + 1) / (len(tn) + 2)
    w1 = np.log(ph / pn); w0 = np.log((1 - ph) / (1 - pn))
    sc = lambda X: X @ w1 + (1 - X) @ w0
    sh, sn = sc(Xh[vh]), sc(Xn[vn])
    auc = stats.mannwhitneyu(sh, sn).statistic / (len(sh) * len(sn))
    # gain of the best threshold: keep a fraction f of trials holding a fraction c of the collisions
    thr = np.quantile(sn, [0.5, 0.75, 0.9, 0.97])
    gains = [(np.mean(sh > t) / max(np.mean(sn > t), 1e-9)) for t in thr]
    se = math.sqrt(auc * (1 - auc) * (1 / len(sh) + 1 / len(sn)) * 2)
    P(f'[{name}] held-out AUC of a per-bit score on {"+".join(use)}: {auc:.3f} (+- {se:.3f}); kept-collision/kept-trial '
      f'ratio at keep 50/25/10/3%: ' + ' '.join(f'{g:.2f}' for g in gains))


def pick_cal(N, Ni):
    """one null trial per hit (same run) becomes a pseudo-hit; the rest stays null"""
    pick = np.zeros(len(N), bool)
    first = {}
    for j, i in enumerate(Ni):
        first.setdefault(i, j)
    pick[list(first.values())] = True
    return N[pick], Ni[pick], N[~pick], Ni[~pick]


def load_p3():
    d = {}
    fn = os.path.join(HERE, 'p3_out.txt')
    if os.path.exists(fn):
        for l in open(fn):
            t, c = l.split()
            if t[0] == 'c' and not t.startswith('chk'):
                s_, k, d1, w8 = map(int, t[1:].split('_'))
                d[(s_, k, d1, w8)] = int(c)
    return d


def p3w(a, P3):
    return np.array([P3.get((int(r[1]), int(r[3]), int(r[5]), int(r[9 + 8])), 0) if r[-1] > 0 else 0 for r in a], float)


def main():
    P3 = load_p3()
    for W in (8, 10):
        F = feats(W)
        hi, h = F['h']
        n0i, n0 = F['n0']
        n1i, n1 = F['n1'] if 'n1' in F else (None, None)
        modes = col(h, 'mode')
        for arrname, msel in (('filed', 0), ('counter', 1)):
            sel = modes == msel
            if not sel.any():
                continue
            hs, his = h[sel], hi[sel]
            m0 = np.isin(n0i, his)
            cal, cali, N0r, N0ri = pick_cal(n0[m0], n0i[m0])
            name = f'W={W} {arrname} ({len(hs)} hits)'
            P('')
            P(f'==== {name}: null N0 {len(N0r)} trials + CAL {len(cal)}' + (f', N1 {int(np.isin(n1i, his).sum())}' if n1 is not None else ''))
            dh, dn = family_tests(name + ' vs N0', W, hs, N0r, cal, his, N0ri, cali)
            dc = derived(cal, W, cali)
            N1 = N1i = None
            if n1 is not None:
                m1 = np.isin(n1i, his)
                cal1, cal1i, N1, N1i = pick_cal(n1[m1], n1i[m1])
                family_tests(name + ' vs N1', W, hs, N1, cal1, his, N1i, cal1i)
                mass_tests(name, hs, N0r, N1)
                if P3:
                    wh = p3w(hs, P3); w0 = p3w(N0r, P3)
                    # per-set normalisation: each set's null weight = its number of hits (the set mix is matched)
                    sN, sH = col(N0r, 'set'), Counter(col(hs, 'set').tolist())
                    for st in np.unique(sN):
                        m_ = sN == st
                        tot = w0[m_].sum()
                        w0[m_] = w0[m_] * sH.get(int(st), 0) / tot if tot > 0 else 0.0
                    P(f'[{name}] exact model given (member, E1.d1, w8): hits in cells of probability 0: {int((wh == 0).sum())} of {len(hs)}; '
                      f'N0 trials with weight > 0: {int((w0 > 0).sum())}, effective null size {neff(w0, len(w0)):.0f}')
                    c2 = rng.choice(len(N0r), len(hs), p=w0 / w0.sum())
                    family_tests(name + ' vs N2 (model incl. w8)', W, hs, N0r, N0r[c2], his, N0ri, N0ri[c2], wn=w0,
                                 groups_only=['search', 'message'])
                    r2 = rng.choice(len(N0r), 20 * len(hs), p=w0 / w0.sum())
                    N2s, N2si = N0r[r2], N0ri[r2]
            member_tests(name, W, hs, N0r, N1, his)
            cluster_and_spacing(name, W, hs, his)
            extra = [('d1', 't'), ('u', 't'), ('k', 't')] if msel == 1 else []
            smooth_pairs(name + ' vs N0', W, hs, N0r, cal, dh, dn, dc, extra)
            use = ['w5o', 'S9', 'x2', 'k']
            msg = ['w0', 'w1', 'w2', 'w3', 'w6', 'w7', 'w8', 'w9', 'w10', 'w11', 'w12']
            classifier(name + ' vs N0', W, hs, N0r, dh, dn, use)
            classifier(name + ' vs N0', W, hs, N0r, dh, dn, ['k', 'd1'])
            if N1 is not None:
                d1n = derived(N1, W, N1i)
                classifier(name + ' vs N1', W, hs, N1, dh, d1n, use)
                classifier(name + ' vs N1', W, hs, N1, dh, d1n, msg)
                classifier(name + ' vs N1', W, hs, N1, dh, d1n, ['w8'])
                # (no classifier against N2: its resample repeats ~1,300 distinct trials, so train/test would share rows)
            else:
                classifier(name + ' vs N0', W, hs, N0r, dh, dn, msg)
    P('')
    within_run()
    P('')
    run_level()
    # filed layout (X14 middle word): search order only (its construction is not in feat.c)
    P('')
    fl = [r for r in H if r['src'] == 'FL']
    for W in (8, 10):
        rr = [r for r in fl if int(r['W']) == W]
        u = np.array([(int(r['outer']) + 0.5) / int(r['nouter']) for r in rr])
        ks = stats.kstest(u, 'uniform')
        mk = Counter(int(r['member']) for r in rr)
        P(f'[filed layout W={W}, {len(rr)} hits] outer step / nouter uniform? KS p {ks.pvalue:.2g}; '
          f'runs with >=2 hits in the same outer step: {sum(1 for c in Counter((r["set"], r["ser"], r["seed"], r["outer"]) for r in rr).values() if c > 1)}')
    open(os.path.join(HERE, 'results.txt'), 'w').write('\n'.join(OUT) + '\n')


if __name__ == '__main__':
    main()
