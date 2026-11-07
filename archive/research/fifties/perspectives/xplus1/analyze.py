#!/usr/bin/env python3
"""xplus1 lens on the front-line residual R = K1 ^ K3 (digest words 1,3,4,6).

Read-only on ../data.  Writes analyze_out.txt next to this file.  Every test has a CONTROL
(the same statistic on uniform random u32 words of the same count, seeded) and a train/test split
(rand/: rows [0,N/2) vs [N/2,N); ctx/: contexts 0-7 vs 8-15, or j-halves inside a group).
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

import sys
sys.dont_write_bytecode = True
import os, math, time
import numpy as np
from scipy import stats
import xplus1lib as L
from xplus1lib import U32, U64, ror, digits, val, low_digits, parity

DATA = _hca_public_path_text('__HCA_WORKSPACE__/research/fifties/perspectives/data')
HERE = os.path.dirname(os.path.abspath(__file__))
ETA = 0x830303CF
Y3A, Y3B, Y11A, Y11B = 0x8127C181, 0x7EDF3E7E, 0x7AF77F38, 0x850000C3
WN = (1, 3, 4, 6)
RNG = np.random.default_rng(0x5850315F31)   # control seed (fixed)
LOG = []


def out(*a):
    s = ' '.join(str(x) for x in a)
    print(s, flush=True)
    LOG.append(s)


def load(st, name, cols):
    return np.fromfile(os.path.join(DATA, st, name), '<u4').reshape(-1, cols)


def unif(shape):
    return RNG.integers(0, 2**32, size=shape, dtype=np.uint64).astype(U32)


# ---------------- statistics helpers ----------------
def geo_test(v, kmax=None):
    """valuation histogram vs the uniform law P(v=k)=2^-(k+1)."""
    N = len(v)
    if kmax is None:
        kmax = max(2, int(math.floor(math.log2(N / 64))))
    obs = np.bincount(np.minimum(v, kmax), minlength=kmax + 1)[:kmax + 1].astype(float)
    exp = np.array([N * 2.0 ** -(k + 1) for k in range(kmax)] + [N * 2.0 ** -kmax])
    chi2 = float(((obs - exp) ** 2 / exp).sum())
    p = float(stats.chi2.sf(chi2, kmax))
    zbin = (obs - exp) / np.sqrt(exp * (1 - exp / N))
    mean = float(v.mean())
    zmean = (mean - (1 - 2.0 ** -32)) / math.sqrt(2.0 / N)
    return dict(N=N, kmax=kmax, obs=obs, exp=exp, chi2=chi2, df=kmax, p=p, zbin=zbin, mean=mean, zmean=zmean)


def fmt_geo(name, g):
    zb = g['zbin']
    i = int(np.argmax(np.abs(zb)))
    return (f"{name:<22} N={g['N']:>8} mean_v={g['mean']:.4f} (z {g['zmean']:+6.2f})  chi2={g['chi2']:8.1f}/df{g['df']}"
            f" p={g['p']:.3g}  P(v=0)={g['obs'][0]/g['N']:.4f} P(v>=4)={g['obs'][4:].sum()/g['N']:.5f}"
            f"  worst bin {i}{'+' if i == g['kmax'] else ''} z={zb[i]:+.2f}")


def halving(v, kmax=20):
    rows = []
    for k in range(kmax):
        nk = int((v >= k).sum())
        nk1 = int((v >= k + 1).sum())
        if nk == 0:
            break
        z = (nk1 - 0.5 * nk) / math.sqrt(0.25 * nk)
        rows.append((k, nk, nk1, nk1 / nk, z))
    return rows


def collisions(key):
    s = np.sort(key)
    edges = np.flatnonzero(s[1:] != s[:-1]) + 1
    cnt = np.diff(np.concatenate(([0], edges, [len(s)]))).astype(np.int64)
    return int((cnt * (cnt - 1) // 2).sum())


def h2_stat(key, bits):
    """collision (Renyi-2) entropy of a bits-wide projection vs uniform. Under uniform the pair
    indicators are pairwise independent, so Var(C) = pairs q (1-q) exactly."""
    N = len(key)
    C = collisions(key)
    pairs = N * (N - 1) / 2
    q = 2.0 ** -bits
    e = pairs * q
    z = (C - e) / math.sqrt(e * (1 - q))
    deficit = math.log2(C / e) if C > 0 else float('-inf')
    return C, e, deficit, z


def hist_stat(key, bits):
    """full histogram (bits <= 20): chi2 vs uniform, Miller-Madow entropy deficit, P(0)."""
    N = len(key)
    K = 1 << bits
    cnt = np.bincount(key.astype(np.int64), minlength=K).astype(float)
    e = N / K
    chi2 = float(((cnt - e) ** 2 / e).sum())
    p = float(stats.chi2.sf(chi2, K - 1))
    pr = cnt[cnt > 0] / N
    H = float(-(pr * np.log2(pr)).sum()) + ((cnt > 0).sum() - 1) / (2 * N * math.log(2))
    return chi2, K - 1, p, bits - H, cnt[0], e


def key_of(cols, m, how='lens', masks=None):
    """concatenate a per-word m-bit projection of each column (u64 key)."""
    key = np.zeros(cols.shape[0], U64)
    for i in range(cols.shape[1]):
        w = cols[:, i]
        if how == 'lens':
            part = low_digits(w, m)
        elif how == 'lowbits':
            part = w & U32((1 << m) - 1) if m < 32 else w
        elif how == 'highbits':
            part = w >> U32(32 - m)
        else:
            raise ValueError(how)
        key = (key << U64(m)) | part.astype(U64)
    return key


def key_randlin(cols, b, masks):
    """b random parities of the whole (N, k) word block; masks shape (b, k)."""
    key = np.zeros(cols.shape[0], U64)
    for t in range(b):
        acc = np.zeros(cols.shape[0], np.uint8)
        for i in range(cols.shape[1]):
            acc ^= parity(cols[:, i] & masks[t, i])
        key = (key << U64(1)) | acc.astype(U64)
    return key


# ---------------- sections ----------------
def sec_selftest():
    out('== 0. Self-test of the lens (COMPUTED) ==')
    n, f = L.selftest(np.random.default_rng(7))
    out(f'words tested {n}, failures {f}  (reconstruction w = sum c_j (x+1)^j, valuation by exact division,'
        f' involution, rotation invariance, v(a^b) >= min, period-4 words have v >= 28)')
    for name, w in (('eta = dE3.h1', ETA), ('dY3 (E3 input a)', Y3A ^ Y3B), ('dY11 (E1 input c)', Y11A ^ Y11B)):
        out(f'  v({name} = {w:08x}) = {L.val_ref(w)}')
    if f:
        raise SystemExit('self-test failed')


def sec_identities(S):
    out('\n== 1. Ring-linear identities used below (COMPUTED on every row) ==')
    R, K1, K3 = S['R'], S['K1'], S['K3']
    U = ror(R[:, 0], 8) ^ R[:, 2]
    V = ror(R[:, 1], 8) ^ R[:, 3]
    ok1 = np.array_equal(K1[:, 2], ror(K1[:, 0], 8))
    ok2 = np.array_equal(K3[:, 3], ror(K3[:, 1] ^ U32(ETA), 8))
    ok3 = np.array_equal(U, ror(K3[:, 0], 8) ^ K3[:, 2])
    ok4 = np.array_equal(V, ror(K1[:, 1], 8) ^ K1[:, 3] ^ U32(L.ror(np.array([ETA], U32), 8)[0]))
    out(f'  K1w4 = x^-8 K1w1: {ok1};  K3w6 = x^-8 (K3w3 + eta): {ok2}')
    out(f'  U = x^-8 R1 + R4 = x^-8 K3w1 + K3w4 (E3 only): {ok3};  V = x^-8 R3 + R6 = x^-8 K1w3 + K1w6 + x^-8 eta (E1 only): {ok4}')
    out('  => v(K1w4) = v(K1w1) and v(K3w6) = v(K3w3 + eta) exactly (DERIVED: rotation is a unit).')
    S['U'] = U
    S['V'] = V


def sec_marginals(S, CTRL, tag):
    out(f'\n== 2. Valuation laws vs uniform, set {tag} (train = first half, test = second half) ==')
    N = S['R'].shape[0]
    h = N // 2
    items = []
    for i, w in enumerate(WN):
        items.append((f'R w{w}', S['R'][:, i]))
    items.append(('U=x^-8R1+R4', S['U']))
    items.append(('V=x^-8R3+R6', S['V']))
    for i, w in enumerate(WN):
        items.append((f'K1 w{w}', S['K1'][:, i]))
    for i, w in enumerate(WN):
        items.append((f'K3 w{w}', S['K3'][:, i]))
    for i, w in enumerate(WN):
        items.append((f'digA w{w}', S['dA'][:, i]))
    for i in range(4):
        items.append((f'CONTROL u{i}', CTRL[:, i]))
    for name, w in items:
        v = val(w)
        gtr = geo_test(v[:h])
        gte = geo_test(v[h:])
        out(fmt_geo(name + ' train', gtr))
        out(fmt_geo(name + ' test', gte))


def sec_halving(S, CTRL, tag):
    out(f'\n== 3. Descent toward period-2^s ideals, set {tag}: P(v>=k+1 | v>=k) (uniform 0.5) ==')
    out('   word        k:  ' + ' '.join(f'{k:>6}' for k in range(0, 18)))
    rows = [(f'R w{w}', S['R'][:, i]) for i, w in enumerate(WN)] + [('U', S['U']), ('V', S['V'])]
    rows += [(f'CONTROL u{i}', CTRL[:, i]) for i in range(2)]
    allv = []
    for name, w in rows:
        hv = halving(val(w), 18)
        out(f'   {name:<11} r: ' + ' '.join(f'{r[3]:6.3f}' for r in hv))
        out(f'   {"":<11} z: ' + ' '.join(f'{r[4]:+6.1f}' for r in hv))
        allv.append(val(w))
    # min valuation over the four R words: P(all four in I_k) vs 2^-4k
    vmin = np.minimum.reduce([val(S['R'][:, i]) for i in range(4)])
    cmin = np.minimum.reduce([val(CTRL[:, i]) for i in range(4)])
    N = len(vmin)
    out('   all four R words in I_k (R in I_k^4): count obs vs N*2^-4k, and CONTROL')
    for k in range(1, 6):
        o, c, e = int((vmin >= k).sum()), int((cmin >= k).sum()), N * 2.0 ** (-4 * k)
        out(f'     k={k}: obs {o:>8}  exp {e:10.1f}  ratio {o/e:6.3f}  z {(o-e)/math.sqrt(e):+6.2f}   CONTROL {c:>8} ratio {c/e:6.3f}')


def sec_digit_bias(S, CTRL, tag):
    out(f'\n== 4. Bias of each (x+1)-adic digit c_j (a fixed XOR mask: bits i that are supersets of j), set {tag} ==')
    N = S['R'].shape[0]
    h = N // 2
    sq = math.sqrt(h)

    def zmat(cols):
        Z = np.zeros((2, cols.shape[1], 32))
        for half, sl in enumerate((slice(0, h), slice(h, N))):
            for i in range(cols.shape[1]):
                c = digits(cols[sl, i])
                for j in range(32):
                    Z[half, i, j] = (1 - 2 * ((c >> U32(j)) & U32(1)).mean()) * sq
        return Z

    def zbits(cols):
        Z = np.zeros((2, cols.shape[1], 32))
        for half, sl in enumerate((slice(0, h), slice(h, N))):
            for i in range(cols.shape[1]):
                c = cols[sl, i]
                for j in range(32):
                    Z[half, i, j] = (1 - 2 * ((c >> U32(j)) & U32(1)).mean()) * sq
        return Z
    Rx = np.column_stack([S['R'], S['U'], S['V']])
    names = [f'R w{w}' for w in WN] + ['U', 'V']
    Zd = zmat(Rx)
    Zb = zbits(Rx)
    Zc = zmat(CTRL[:, :6])
    for lab, Z in (('lens digits c_j', Zd), ('raw bits (XOR view)', Zb), ('CONTROL digits', Zc)):
        tr, te = Z[0], Z[1]
        flat = np.argsort(-np.abs(tr).ravel())[:8]
        out(f'  {lab}: max|z| train {np.abs(tr).max():6.2f}; 6x32 tests, null max|z| ~3.4.  top-8 train -> test:')
        for f in flat:
            i, j = divmod(int(f), 32)
            nm = names[i] if lab != 'CONTROL digits' else f'u{i}'
            out(f'     {nm:<6} j={j:>2} (|mask|={32 >> bin(j).count("1") if lab != "raw bits (XOR view)" else 1:>2})'
                f'  z_train {tr[i, j]:+7.2f}  z_test {te[i, j]:+7.2f}   bias_test {te[i, j]/sq:+.4f}')
        r = np.corrcoef(tr.ravel(), te.ravel())[0, 1]
        out(f'     train/test correlation of all 192 z values: {r:+.3f}')
    # how many digits are significant in both halves (|z|>4 both, same sign)
    for lab, Z in (('lens', Zd), ('raw', Zb), ('CONTROL', Zc)):
        both = (np.abs(Z[0]) > 4) & (np.abs(Z[1]) > 4) & (np.sign(Z[0]) == np.sign(Z[1]))
        out(f'  {lab}: coordinates with |z|>4 in both halves, same sign: {int(both.sum())} of 192')
        if lab == 'lens':
            S['sig_digits'] = [(names[i], j, Z[1][i, j] / sq) for i, j in zip(*np.nonzero(both))]
    # entropy bound from single-coordinate biases (sum of 1-H(p)), per basis, test half
    for lab, Z in (('lens', Zd), ('raw', Zb), ('CONTROL', Zc)):
        e = np.clip(Z[1, :4] / sq, -0.999999, 0.999999)
        p = (1 + e) / 2
        Hd = float((1 - (-(p * np.log2(p) + (1 - p) * np.log2(1 - p)))).sum())
        out(f'  {lab}: sum over the 128 coordinates of R of (1 - H(p)) on test half = {Hd:.4f} bits'
            f' (an upper bound on what single-coordinate biases alone can save)')


def sec_projections(S, CTRL, tag):
    out(f'\n== 5. Entropy of the folds R mod (x+1)^m, all four words jointly (4m bits), set {tag} ==')
    out('   lens = low m digits (= XOR-fold to m bits when m is a power of 2); compared with the XOR-view low/high m bits,')
    out('   3 random linear projections of the 128-bit R to 4m bits, and the CONTROL (uniform words, lens projection).')
    R = S['R']
    RUV = np.column_stack([R[:, 0], R[:, 1], S['U'], S['V']])
    N = R.shape[0]
    masks = [RNG.integers(0, 2**32, size=(40, 4), dtype=np.uint64).astype(U32) for _ in range(3)]
    out('   P(R mod (x+1)^m = 0 on all four words) = P(fold of K1 = fold of K3):')
    for m in range(1, 6):
        b = 4 * m
        k = key_of(R, m)
        kc = key_of(CTRL[:, :4], m)
        e = N * 2.0 ** -b
        o, oc = int((k == 0).sum()), int((kc == 0).sum())
        out(f'     m={m} ({b:>2} bits): obs {o:>7}  exp {e:10.2f}  ratio {o/e:6.3f}  z {(o-e)/math.sqrt(e):+6.2f}'
            f'   CONTROL {oc:>7} ratio {oc/e:6.3f}')
    out('   full-histogram tests (4m <= 16):  chi2/df, p, entropy deficit (Miller-Madow) in bits')
    for m in (1, 2, 3, 4):
        b = 4 * m
        for lab, key in (('lens R', key_of(R, m)), ('lens (R1,R3,U,V)', key_of(RUV, m)),
                         ('lowbits R', key_of(R, m, 'lowbits')), ('highbits R', key_of(R, m, 'highbits')),
                         ('randlin R #0', key_randlin(R, b, masks[0][:b])), ('CONTROL lens', key_of(CTRL[:, :4], m))):
            chi2, df, p, dfc, c0, e0 = hist_stat(key, b)
            out(f'     m={m} {lab:<18} chi2/df {chi2/df:7.3f} p={p:.3g}  deficit {dfc:+.5f} bits  P(0)/2^-{b} = {c0/e0:6.3f}')
    out('   collision (Renyi-2) entropy, 4m bits: deficit = log2(collisions / expected); z vs uniform')
    out('   (the lens projection contains parity(R3)+parity(R6), which is 0 on every row, so its baseline deficit is exactly 1 bit;')
    out('    "beyond1" = collisions vs 2x expected, z under the uniform-on-the-127-dim-subspace law)')
    for m in range(5, 11):
        b = 4 * m
        C, e, d, z = h2_stat(key_of(R, m), b)
        e2 = 2 * e
        out(f'     {b} bits lens beyond the parity bit: {C}/{e2:.1f}  deficit beyond {math.log2(C / e2) if C else float("-inf"):+.3f}'
            f'  z {(C - e2) / math.sqrt(e2):+.2f}')
    for m in range(5, 11):
        b = 4 * m
        row = []
        for lab, key in (('lens R', key_of(R, m)), ('lens RUV', key_of(RUV, m)), ('lowbits', key_of(R, m, 'lowbits')),
                         ('highbits', key_of(R, m, 'highbits')),
                         ('randlin0', key_randlin(R, b, masks[0][:b])), ('randlin1', key_randlin(R, b, masks[1][:b])),
                         ('randlin2', key_randlin(R, b, masks[2][:b])), ('CONTROL', key_of(CTRL[:, :4], m))):
            C, e, d, z = h2_stat(key, b)
            row.append(f'{lab} {C}/{e:.1f} d{d:+.3f} z{z:+.1f}')
        out(f'     {b} bits: ' + ' | '.join(row))
    out('   single word, low m digits (m = 20, 24, 28) vs low m bits vs CONTROL: collisions / expected')
    for i, w in enumerate(WN):
        row = []
        for m in (20, 24, 28):
            C, e, d, z = h2_stat(low_digits(R[:, i], m).astype(U64), m)
            Cb, _, db, zb = h2_stat((R[:, i] & U32((1 << m) - 1)).astype(U64), m)
            Cc, _, dc, zc = h2_stat(low_digits(CTRL[:, i], m).astype(U64), m)
            row.append(f'm{m}: lens {C}/{e:.1f} (z{z:+.1f}) low {Cb} (z{zb:+.1f}) ctrl {Cc} (z{zc:+.1f})')
        out(f'     R w{w}: ' + ' | '.join(row))


def sec_share(S, tag):
    out(f'\n== 6. Do the E1 part (K1) and E3 part (K3) share valuation / fold?  set {tag} ==')
    out('   P(v(K1)=v(K3)) observed vs independence (product of the observed marginals) vs a row-shuffle CONTROL;')
    out('   uniform words would give 1/3.  G-test of independence on the valuation table (capped at 8).')
    K1, K3 = S['K1'], S['K3']
    N = K1.shape[0]
    h = N // 2
    perm = RNG.permutation(N)
    for i, w in enumerate(WN):
        v1, v3 = val(K1[:, i]), val(K3[:, i])
        line = []
        for half, sl in (('train', slice(0, h)), ('test', slice(h, N))):
            a, b = v1[sl], v3[sl]
            n = len(a)
            f1 = np.bincount(a, minlength=33) / n
            f3 = np.bincount(b, minlength=33) / n
            pin = float((f1 * f3).sum())
            pobs = float((a == b).mean())
            z = (pobs - pin) / math.sqrt(pin * (1 - pin) / n)
            tab = np.zeros((9, 9))
            np.add.at(tab, (np.minimum(a, 8), np.minimum(b, 8)), 1)
            tab = tab[tab.sum(1) > 0][:, tab.sum(0) > 0]
            g, p, dof, _ = stats.chi2_contingency(tab, lambda_='log-likelihood')
            line.append(f'{half}: P_eq {pobs:.4f} indep {pin:.4f} z {z:+6.2f} G p={p:.2g}')
        ps = float((v1 == v3[perm]).mean())
        out(f'   w{w}: ' + ' | '.join(line) + f' | shuffle-CONTROL P_eq {ps:.4f}')
    out('   fold sharing: P(K1 mod (x+1)^m = K3 mod (x+1)^m) per word, observed vs independence sum_x p1(x)p3(x) vs 2^-m')
    for i, w in enumerate(WN):
        row = []
        for m in (1, 2, 4, 8, 12, 16):
            a = low_digits(K1[:, i], m).astype(np.int64)
            b = low_digits(K3[:, i], m).astype(np.int64)
            f1 = np.bincount(a, minlength=1 << m) / N
            f3 = np.bincount(b, minlength=1 << m) / N
            pin = float((f1 * f3).sum())
            pobs = float((a == b).mean())
            z = (pobs - pin) / math.sqrt(pin * (1 - pin) / N)
            row.append(f'm{m}: {pobs*2**m:.3f}/{pin*2**m:.3f} z{z:+.1f}')
        out(f'   w{w} (obs*2^m / indep*2^m): ' + ' '.join(row))
    out('   entropy of each part on its own (lens low-m digits, Miller-Madow deficit in bits; m=16):')
    for i, w in enumerate(WN):
        d1 = hist_stat(low_digits(K1[:, i], 16).astype(np.int64), 16)[3]
        d3 = hist_stat(low_digits(K3[:, i], 16).astype(np.int64), 16)[3]
        dr = hist_stat(low_digits(S['R'][:, i], 16).astype(np.int64), 16)[3]
        out(f'   w{w}: K1 deficit {d1:.4f}  K3 deficit {d3:.4f}  R deficit {dr:.4f}')


def sec_crossword(S, CTRL, tag):
    out(f'\n== 7. Valuation coupling between the four R words (and a rotation scan), set {tag} ==')
    R = S['R']
    N = R.shape[0]
    h = N // 2
    V = np.column_stack([val(R[:, i]) for i in range(4)])
    VC = np.column_stack([val(CTRL[:, i]) for i in range(4)])
    for (a, b) in ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)):
        line = []
        for lab, M in (('R', V), ('CONTROL', VC)):
            tab = np.zeros((7, 7))
            np.add.at(tab, (np.minimum(M[:, a], 6), np.minimum(M[:, b], 6)), 1)
            g, p, dof, _ = stats.chi2_contingency(tab, lambda_='log-likelihood')
            line.append(f'{lab} G={g:7.1f}/df{dof} p={p:.2g}')
        out(f'   v(R w{WN[a]}) vs v(R w{WN[b]}): ' + ' | '.join(line))
    # w3/w6 beyond the parity bit: parity(R3) = parity(R6) forces v(R3)=0 <=> v(R6)=0; test the rest
    sel = (V[:, 1] >= 1) & (V[:, 3] >= 1)
    tab = np.zeros((6, 6))
    np.add.at(tab, (np.minimum(V[sel, 1] - 1, 5), np.minimum(V[sel, 3] - 1, 5)), 1)
    g, p, dof, _ = stats.chi2_contingency(tab, lambda_='log-likelihood')
    out(f'   v(R w3) vs v(R w6) on rows with both v >= 1 (the parity bit removed): G={g:.1f}/df{dof} p={p:.2g};'
        f'  P(v(R3)=0 xor v(R6)=0) = {np.mean((V[:, 1] == 0) != (V[:, 3] == 0)):.4f}')
    out('   rotation scan ("spiral" view: angle r, radius v): mean v(ROR(Ra, r) ^ Rb) over r = 0..31 for every ordered pair;')
    out('   uniform mean 1, sd of a half-sample mean = sqrt(2/(N/2)).  Low digits of ROR(a,r) depend only on r mod 2^s.')
    out('   Raw mean: every (R3,R6,r) cell sits at z ~ +512 because parity(R3) = parity(R6) on every row (section 12) and parity is')
    out('   rotation-invariant.  The scan below removes that bit: statistic = mean(v - 1 | v >= 1), uniform 1, sd sqrt(2/n1).')
    best = []
    for src, M in (('R', R), ('CONTROL', CTRL[:, :4])):
        top = []
        for a in range(4):
            for b in range(4):
                if a == b:
                    continue
                for r in range(32):
                    vv = val(ror(M[:, a], r) ^ M[:, b])
                    zz = []
                    for sl in (slice(0, h), slice(h, N)):
                        x = vv[sl]
                        x = x[x >= 1] - 1
                        zz.append((x.mean() - 1) / math.sqrt(2.0 / len(x)))
                    ztr, zte = zz
                    top.append((abs(ztr), a, b, r, ztr, zte))
        top.sort(reverse=True)
        out(f'   {src}: 384 (a,b,r) cells; top 6 by |z_train|:')
        for t in top[:6]:
            out(f'     ({"R" if src=="R" else "u"}{WN[t[1]] if src=="R" else t[1]}, {"R" if src=="R" else "u"}{WN[t[2]] if src=="R" else t[2]}, r={t[3]:>2}): z_train {t[4]:+7.2f}  z_test {t[5]:+7.2f}')
        best.append(top[0])
    return best


def sec_ctx(C):
    out('\n== 8. ctx/: does the residual fold depend on the context or the member (fixed outer words / fixed k)? ==')
    out('   groups = (context, member), 256 groups of 1,024 random j.  Homogeneity chi2 of each digit indicator across groups;')
    out('   split-half test: correlation across groups of the per-group bias in j-rows [0,512) vs [512,1024) (null r ~ N(0,1/256)).')
    R = C['R']
    N = R.shape[0]
    G = N // 1024
    grp = np.arange(N) // 1024
    inner = np.arange(N) % 1024
    ctrl = unif((N, 4))
    feats = []
    for i, w in enumerate(WN):
        d = digits(R[:, i])
        v = val(R[:, i])
        for j in range(8):
            feats.append((f'R w{w} c{j}', ((d >> U32(j)) & U32(1)).astype(float)))
        for k in (2, 3, 4):
            feats.append((f'R w{w} v>={k}', (v >= k).astype(float)))
    for i, w in enumerate(WN):
        d = digits(C['K1'][:, i])
        for j in range(4):
            feats.append((f'K1 w{w} c{j}', ((d >> U32(j)) & U32(1)).astype(float)))
        d = digits(C['K3'][:, i])
        for j in range(4):
            feats.append((f'K3 w{w} c{j}', ((d >> U32(j)) & U32(1)).astype(float)))
    for i in range(4):
        d = digits(ctrl[:, i])
        for j in range(4):
            feats.append((f'CONTROL u{i} c{j}', ((d >> U32(j)) & U32(1)).astype(float)))
    rows = []
    for name, x in feats:
        p = x.mean()
        gm = np.bincount(grp, weights=x, minlength=G) / 1024
        chi2 = float((1024 * (gm - p) ** 2).sum() / max(p * (1 - p), 1e-12))
        pv = float(stats.chi2.sf(chi2, G - 1))
        a = np.bincount(grp[inner < 512], weights=x[inner < 512], minlength=G) / 512
        b = np.bincount(grp[inner >= 512], weights=x[inner >= 512], minlength=G) / 512
        r = float(np.corrcoef(a, b)[0, 1]) if a.std() > 0 and b.std() > 0 else float('nan')
        rows.append((name, p, chi2, pv, r, r * math.sqrt(G), gm.min(), gm.max()))
    for name, p, chi2, pv, r, z, lo, hi in rows:
        out(f'   {name:<18} P(1)={p:.4f} chi2={chi2:7.1f}/df{G-1} p={pv:.2g}  split-half r={r:+.3f} (z {z:+5.1f})  group P(1) range [{lo:.3f},{hi:.3f}]')
    # best group: P(R mod (x+1)^m = 0) inside each (context, member) group, m = 1, 2 (4 and 8 bits)
    out('   per-group P(R mod (x+1)^m = 0, all four words) scaled by 2^4m; max over 256 groups vs CONTROL max; train=j-rows<512, test=rest')
    for m in (1, 2):
        k = key_of(R, m)
        kc = key_of(ctrl, m)
        sc = 2.0 ** (4 * m)
        tr = np.bincount(grp[inner < 512], weights=(k[inner < 512] == 0), minlength=G) / 512 * sc
        te = np.bincount(grp[inner >= 512], weights=(k[inner >= 512] == 0), minlength=G) / 512 * sc
        cc = np.bincount(grp, weights=(kc == 0), minlength=G) / 1024 * sc
        g = int(np.argmax(tr))
        out(f'     m={m}: best train group {g} (ctx {g//16}, member {g%16}) train {tr[g]:.2f}  test {te[g]:.2f};'
            f'  corr(train,test) over groups {np.corrcoef(tr, te)[0,1]:+.3f};  CONTROL max {cc.max():.2f}')


def sec_inputs(S, tag):
    out(f'\n== 9. Do single input bits predict the low digits of R?  set {tag} (train/test halves) ==')
    out('   inputs: k (19 bits), j (21 bits), t (32 bits), c1 (32 bits), Y4 (32 bits); targets: digits c0..c7 of each R word, and v>=2.')
    I = S['inp']
    R = S['R']
    N = R.shape[0]
    h = N // 2
    srcs = [('k', I[:, 7], 19), ('j', I[:, 8], 21), ('t', I[:, 11], 32), ('c1', I[:, 10], 32), ('Y4', I[:, 9], 32)]
    tg = []
    for i, w in enumerate(WN):
        d = digits(R[:, i])
        for j in range(8):
            tg.append((f'R w{w} c{j}', ((d >> U32(j)) & U32(1)).astype(np.int8)))
        tg.append((f'R w{w} v>=2', (val(R[:, i]) >= 2).astype(np.int8)))
    res = []
    tnames = [t[0] for t in tg]
    Zh = []
    for sl in (slice(0, h), slice(h, N)):
        Y = np.column_stack([t[1][sl] for t in tg]).astype(np.float64)
        Y = (Y - Y.mean(0)) / (Y.std(0) + 1e-300)
        blocks = []
        for sname, col, nb in srcs:
            X = ((col[sl, None] >> np.arange(nb, dtype=U32)) & U32(1)).astype(np.float64)
            X = (X - X.mean(0)) / (X.std(0) + 1e-300)
            blocks.append((X.T @ Y) / h * math.sqrt(h))
        Zh.append(np.vstack(blocks))
    labels = [f'{sname}[{bit}]' for sname, _, nb in srcs for bit in range(nb)]
    for a in range(len(labels)):
        for b in range(len(tnames)):
            res.append((abs(Zh[0][a, b]), labels[a], tnames[b], Zh[0][a, b], Zh[1][a, b]))
    res.sort(reverse=True)
    ntest = len(res)
    out(f'   {ntest} (input bit, target) pairs; Bonferroni null max|z| ~ {stats.norm.isf(0.025 / ntest):.2f}. Top 10 by |z_train|:')
    for t in res[:10]:
        out(f'     {t[1]:<8} -> {t[2]:<12} z_train {t[3]:+7.2f}  z_test {t[4]:+7.2f}')
    conf = [t for t in res if abs(t[3]) > 5 and abs(t[4]) > 5 and np.sign(t[3]) == np.sign(t[4])]
    out(f'   confirmed (|z|>5 both halves, same sign): {len(conf)}')
    for t in conf[:20]:
        out(f'     {t[1]:<8} -> {t[2]:<12} z_train {t[3]:+7.2f}  z_test {t[4]:+7.2f}')


def sec_carries(S, tag):
    out(f'\n== 10. Where the ideals break: valuation of the XOR differences through E1 and E3, set {tag} ==')
    out('   uniform: P(v=0)=0.5, P(v>=2)=0.25, P(v>=4)=0.0625, mean 1.  XOR and rotations keep v; only the 4 additions per half-G move it.')
    ein, em, eo = S['ein'], S['emid'], S['eout']
    w5 = ein[:, 4]
    dw5 = w5 ^ (w5 + U32(0xFFFFFFF8))
    items = [('dY11 (E1 c in)', np.full(len(w5), Y11A ^ Y11B, U32)), ('dw5 (E1 my)', dw5),
             ('dY3 (E3 a in)', np.full(len(w5), Y3A ^ Y3B, U32))]
    for nm, k in (('a1', 0), ('b1', 1), ('c1', 2), ('d1', 3)):
        items.append((f'E1 d{nm} (mid)', em[:, k] ^ em[:, 4 + k]))
    for nm, k in (('e1', 0), ('f1', 1), ('g1', 2), ('h1', 3)):
        items.append((f'E3 d{nm} (mid)', em[:, 8 + k] ^ em[:, 12 + k]))
    for nm, k in (('a2', 0), ('b2', 1), ('c2', 2), ('d2', 3)):
        items.append((f'E1 d{nm} (out)', eo[:, k] ^ eo[:, 4 + k]))
    for nm, k in (('e2', 0), ('f2', 1), ('g2', 2), ('h2', 3)):
        items.append((f'E3 d{nm} (out)', eo[:, 8 + k] ^ eo[:, 12 + k]))
    for nm, x in items:
        v = val(x)
        nd = len(np.unique(x[:200000]))
        out(f'   {nm:<16} distinct(first 2e5) {nd:>7}  P(v=0) {np.mean(v==0):.4f}  P(v>=2) {np.mean(v>=2):.4f}'
            f'  P(v>=4) {np.mean(v>=4):.5f}  mean {v.mean():.4f}')


def sec_d4():
    out('\n== 11. D4 partial records (1,577; one solved diagonal each): valuations of D0..D3 and of the 8-word digest XOR ==')
    A = np.fromfile(os.path.join(DATA, 'd4', 'd4_partial.u32'), '<u4').reshape(-1, 76)
    D = A[:, 4:8]
    X = A[:, 8:16]
    for lab, M in (('D0..D3', D), ('digest XOR w0..7', X), ('CONTROL', unif(D.shape))):
        v = np.concatenate([val(M[:, i]) for i in range(M.shape[1])])
        g = geo_test(v, kmax=8)
        out('   ' + fmt_geo(lab, g))
        out('     per word mean v: ' + ' '.join(f'{val(M[:, i]).mean():.3f}' for i in range(M.shape[1])))


def sec_ringform(S, tag):
    out(f'\n== 12. Ring form of R = 0 (DERIVED), each identity checked on every row of set {tag} (COMPUTED) ==')
    out('   Last half of G: d2 = x^-8(d1 + a2), b2 = x^-7(b1 + c2) (ROR r = x^-r, + = XOR).  With R1=da2+dg2, R3=dc2+de2,')
    out('   R4=dd2+df2, R6=db2+dh2 this gives, for ANY pair:')
    out('     U = x^-8 R1 + R4 = x^-8 [ (1+x) dg2 + dd1(E1) + x df1(E3) ]')
    out('     V = x^-8 R3 + R6 = x^-8 [ (1+x) dc2 + x db1(E1) + dh1(E3) ]')
    out('   (R1,R3,U,V) is an invertible linear image of R, so R = 0  <=>  da2 = dg2 =: tau,  dc2 = de2 =: eps,')
    out('     (1+x) tau = dd1 + x df1   and   (1+x) eps = x db1 + dh1.   (1+x)y always has even parity, so a pair can only')
    out('   collide if parity(dd1) = parity(df1) and parity(db1) = parity(dh1); each equation then has exactly 2 solutions (y, ~y).')
    em, eo = S['emid'], S['eout']
    d1 = em[:, 0:4] ^ em[:, 4:8]     # E1 a1 b1 c1 d1
    e1 = em[:, 8:12] ^ em[:, 12:16]  # E3 e1 f1 g1 h1
    d2 = eo[:, 0:4] ^ eo[:, 4:8]     # E1 a2 b2 c2 d2
    e2 = eo[:, 8:12] ^ eo[:, 12:16]  # E3 e2 f2 g2 h2
    mulx = lambda y: ror(y, 31)
    mul1x = lambda y: y ^ ror(y, 31)
    Up = ror(mul1x(e2[:, 2]) ^ d1[:, 3] ^ mulx(e1[:, 1]), 8)
    Vp = ror(mul1x(d2[:, 2]) ^ mulx(d1[:, 1]) ^ e1[:, 3], 8)
    out(f'   U identity holds on all rows: {np.array_equal(Up, S["U"])};  V identity holds on all rows: {np.array_equal(Vp, S["V"])}')
    R = S['R']
    p36 = parity(R[:, 1] ^ R[:, 3])
    p14 = parity(R[:, 0] ^ R[:, 2])
    out(f'   parity(R3)+parity(R6) == parity(db1)+parity(dh1) on all rows: '
        f'{np.array_equal(p36, parity(d1[:, 1] ^ e1[:, 3]))};  values taken: {np.unique(p36).tolist()}')
    out(f'   parity(R1)+parity(R4) == parity(dd1)+parity(df1) on all rows: '
        f'{np.array_equal(p14, parity(d1[:, 3] ^ e1[:, 1]))};  P(=1) = {p14.mean():.4f}')
    for nm, col in (('E1 da1', d1[:, 0]), ('E1 db1', d1[:, 1]), ('E1 dc1', d1[:, 2]), ('E1 dd1', d1[:, 3]),
                    ('E3 de1', e1[:, 0]), ('E3 dh1', e1[:, 3])):
        u = np.unique(col)
        out(f'   {nm}: {len(u)} distinct' + (f' = {int(u[0]):08x}, parity {int(parity(u)[0])}' if len(u) == 1 else ''))
    out(f'   E3 df1: {len(np.unique(e1[:, 1]))} distinct, P(parity odd) = {parity(e1[:, 1]).mean():.4f}'
        f'  -> on that half of the E3 instances the U-equation has no solution (DERIVED, E3-only abort after half a G)')
    beta = int(np.unique(d1[:, 1])[0])
    eta = int(np.unique(e1[:, 3])[0])
    w = (((beta << 1) | (beta >> 31)) & 0xFFFFFFFF) ^ eta
    q = acc = 0
    for i in range(32):
        acc ^= (w >> i) & 1
        q |= acc << i
    out(f'   front line: db1 = beta = {beta:08x}, dh1 = eta = {eta:08x}, dd1 = 0.  x beta + eta = {w:08x} (parity {bin(w).count("1") & 1})')
    out(f'   => eps in {{c*, ~c*}} = {{{q:08x}, {q ^ 0xFFFFFFFF:08x}}}; c* = 6e21be55 is the eps of every outcome in the pkgCG proof (Section 10.1),')
    out(f'      and the U-equation with dd1 = 0 reads df1 = x^-1 (1+x) tau = tau XOR ROR(tau,1), the proof\'s E3 b1 condition.')
    vv = val(d2[:, 2] ^ U32(q))
    out(f'   v(V) == 1 + v(dc2 + c*) on all rows: {np.array_equal(val(S["V"]), np.minimum(32, vv + 1))}')
    N = R.shape[0]
    h = N // 2
    vV = val(S['V'])
    for lab, sl in (('train', slice(0, h)), ('test', slice(h, N))):
        x = vV[sl]
        row = []
        for k in (6, 7, 8, 9):
            nk, nk1 = int((x >= k).sum()), int((x >= k + 1).sum())
            row.append(f'P(v>={k+1}|v>={k}) {nk1/nk:.4f} (z {(nk1-0.5*nk)/math.sqrt(0.25*nk):+.1f})')
        out(f'   V digit chain near 7/8, {lab}: ' + '  '.join(row) +
            f'  | P(v>=9)*2^8 = {(x >= 9).mean()*256:.3f}')


def dedup(S):
    _, idx = np.unique(S['inp'], axis=0, return_index=True)
    idx = np.sort(idx)
    T = {k: (v[idx] if isinstance(v, np.ndarray) and v.shape[0] == S['inp'].shape[0] else v) for k, v in S.items()}
    return T, S['inp'].shape[0] - len(idx)


def load_set(st):
    S = {}
    S['R'] = load(st, 'res.u32', 4)
    k = load(st, 'keys.u32', 8)
    S['K1'], S['K3'] = k[:, :4], k[:, 4:]
    d = load(st, 'dig.u32', 8)
    S['dA'], S['dB'] = d[:, :4], d[:, 4:]
    S['inp'] = load(st, 'inputs.u32', 12)
    S['ein'] = load(st, 'einputs.u32', 9)
    S['emid'] = load(st, 'emid.u32', 16)
    S['eout'] = load(st, 'eout.u32', 16)
    return S


def main():
    t0 = time.time()
    out(f'xplus1 analyze.py  numpy {np.__version__}')
    sec_selftest()
    S = load_set('rand')
    C = load_set('ctx')
    N = S['R'].shape[0]
    CTRL = unif((N, 6))
    out(f'rand rows {N}, ctx rows {C["R"].shape[0]}; CONTROL = {N} rows of uniform u32 (seeded)')
    sec_identities(S)
    sec_identities(C)
    Cd, ndup = dedup(C)
    nC = Cd['R'].shape[0]
    out(f'ctx: {ndup} repeated input rows removed for sections 3, 5, 6 and 12 ({nC} rows left); section 8 keeps the group layout')
    sec_marginals(S, CTRL, 'rand')
    sec_halving(S, CTRL, 'rand')
    sec_halving(Cd, CTRL[:nC], 'ctx')
    sec_digit_bias(S, CTRL, 'rand')
    sec_projections(S, CTRL, 'rand')
    sec_projections(Cd, CTRL[:nC], 'ctx')
    sec_share(S, 'rand')
    sec_share(Cd, 'ctx')
    sec_crossword(S, CTRL, 'rand')
    sec_ctx(C)
    sec_inputs(S, 'rand')
    sec_carries(S, 'rand')
    sec_d4()
    sec_ringform(S, 'rand')
    sec_ringform(Cd, 'ctx')
    out(f'\nelapsed {time.time() - t0:.1f} s')
    with open(os.path.join(HERE, 'analyze_out.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(LOG) + '\n')


if __name__ == '__main__':
    main()
