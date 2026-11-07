"""check2-3: independent statistics of q3gpu logs (not the scout's stats.py).
Per run, Z is recomputed from the logged INTEGER counts (survivors ns, tail hits) with the imposed-bit counts f taken
directly from vt38.py's CELL/PLUS tables and |F7| = 287,309,824; compared with the logged log2Z; run keys recomputed
from runkey(master, r); exact Student quantile (scipy); batch-means bound as a dependence/normality check.
usage: python indep_stats.py [--a0 file.a0] log [log ...]"""

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

import sys, re, math, importlib.util
sys.dont_write_bytecode = True
import numpy as np
from scipy import stats

BASE = _hca_public_path_text('__HCA_WORKSPACE__/research/tools/build_pkg/scratch/pkgR38a/base')
spec = importlib.util.spec_from_file_location('vt38', BASE + r'\experiments\vt38.py')
vt = importlib.util.module_from_spec(spec); spec.loader.exec_module(vt)
pc = lambda x: bin(x & 0xffffffff).count('1')
F = {I: pc(vt.CELL['E'][I][0]) + pc(vt.PLUS[I]) for I in range(17, 23)}
OV = {I: pc(vt.CELL['E'][I][0] & vt.PLUS[I]) for I in range(17, 23)}
F23 = pc(vt.CELL['W'][23][0]); F7N = 287309824
M64 = (1 << 64) - 1
def smx64(x):
    x = (x + 0x9e3779b97f4a7c15) & M64; x = ((x ^ (x >> 30)) * 0xbf58476d1ce4e5b9) & M64
    x = ((x ^ (x >> 27)) * 0x94d049bb133111eb) & M64; return x ^ (x >> 31)
def runkey(master, r): return smx64(smx64(master) ^ ((0x9e3779b97f4a7c15 * (r + 1)) & M64))

HDR = re.compile(r'^# q3gpu (?:cpubatch )?master (\d+) .*NP (\d+) MS (\d+) (\d+) (\d+) (\d+) (\d+) (\d+) MT (\d+) V (\d+)')
def load(fn, master=None, cfg=None):
    rows = []; bad_key = 0; maxdiff = 0.0
    for line in open(fn):
        m = HDR.match(line)
        if m:
            g = [int(x) for x in m.groups()]; master = g[0]; cfg = dict(NP=g[1], MS=dict(zip(range(17, 23), g[2:8])), MT=g[8], V=g[9]); continue
        if not line.startswith('run '): continue
        t = line.split()
        r = int(t[1]); key = int(t[3], 16); lz = float(t[5]); i_ns = t.index('ns')
        ns = [int(x) for x in t[i_ns + 1:i_ns + 7]]; hits = int(t[t.index('hits') + 1]); bad = int(t[t.index('bad') + 1])
        if master is not None and runkey(master, r) != key: bad_key += 1
        NP, MS, MT = cfg['NP'], cfg['MS'], cfg['MT']
        lzc = -27.0 + sum(math.log2(ns[i] / (NP * MS[17 + i])) - F[17 + i] for i in range(6)) \
              + math.log2(hits / (NP * MT)) + 32 - F23 - math.log2(F7N)
        maxdiff = max(maxdiff, abs(lzc - lz))
        rows.append((r, lzc, hits, bad))
    return rows, bad_key, maxdiff, master, cfg

def summary(label, rows):
    rs = [x[0] for x in rows]
    z = np.array([2.0 ** (x[1] + 101) for x in rows]); n = len(z)
    mz = z.mean(); sd = z.std(ddof=1); t = stats.t.ppf(0.99, n - 1); lb = mz - t * sd / math.sqrt(n)
    out = '%s: n %d (distinct r %d), mean 2^%.5f, rel sd %.4f, t %.4f, one-sided 99%% bound 2^%.5f; min 2^%.4f max 2^%.4f; skew %.3f exkurt %.3f; hits %d bad %d' % (
        label, n, len(set(rs)), math.log2(mz) - 101, sd / mz, t, math.log2(lb) - 101, math.log2(z.min()) - 101, math.log2(z.max()) - 101,
        stats.skew(z), stats.kurtosis(z), sum(x[2] for x in rows), sum(x[3] for x in rows))
    # batch means (consecutive runs by index): 128 batches
    order = np.argsort(rs); zb = z[order]; B = 128 if n >= 4096 else 16
    k = n // B; bm = zb[:k * B].reshape(B, k).mean(axis=1); tb = stats.t.ppf(0.99, B - 1)
    lbb = bm.mean() - tb * bm.std(ddof=1) / math.sqrt(B)
    out += '\n   batch means (%d batches of %d): bound 2^%.5f; batch-mean sd / (run sd/sqrt(k)) = %.3f' % (B, k, math.log2(lbb) - 101, bm.std(ddof=1) / (sd / math.sqrt(k)))
    return out, z

def a0chk(fn, SR=191773672732):
    J = []
    for line in open(fn):
        if line.startswith('#'): continue
        j, a0, rj, acc, pr, hi = line.split(); J.append((int(rj), int(acc), int(pr), int(hi), a0))
    rj = np.array([x[0] for x in J], float); acc = np.array([x[1] for x in J], float)
    pr = np.array([x[2] for x in J], float); hi = np.array([x[3] for x in J], float)
    A = acc.sum(); e = A * rj / SR; chi_acc = ((acc - e) ** 2 / e).sum()
    T = hi.sum() / pr.sum(); eh = pr * T; chi_h = ((hi - eh) ** 2 / eh).sum()
    rel = np.log2(hi / pr / T)
    return ('%s: SR(sum |R_j|) %d; accepted %d, chi2 vs |R_j|/SR %.1f (255 df, p %.3f); tail-rate heterogeneity chi2 %.1f (255 df, p %.3f); '
            'per-A0 log2 rate rel. to mean: min %+.4f max %+.4f sd %.4f' % (fn.split('\\')[-1], int(rj.sum()), int(A), chi_acc, stats.chi2.sf(chi_acc, 255),
            chi_h, stats.chi2.sf(chi_h, 255), rel.min(), rel.max(), rel.std(ddof=1)))

if __name__ == '__main__':
    print('imposed bits f from vt38 CELL/PLUS (rows 17..22):', [F[I] for I in range(17, 23)], ' mask/plus overlaps:', [OV[I] for I in range(17, 23)], ' f23 =', F23,
          ' tail weight log2 = %.6f' % (32 - F23 - math.log2(F7N)))
    args = sys.argv[1:]; groups = []; cur = []; a0s = []
    i = 0; dm = None; dv = None
    while i < len(args):
        if args[i] == '--a0': a0s.append(args[i + 1]); i += 2; continue
        if args[i] == '--mv': dm, dv = int(args[i + 1]), int(args[i + 2]); i += 3; continue   # master/V for headerless cpusmc logs
        if args[i] == '+': groups.append(cur); cur = []; i += 1; continue
        cur.append((args[i], dm, dv)); dm = dv = None; i += 1
    if cur: groups.append(cur)
    for g in groups:
        rows = []
        for fn, dm, dv in g:
            cfg0 = dict(NP=4000, MS=dict(zip(range(17, 23), (2048, 64, 64, 8, 8, 4))), MT=8192, V=dv) if dm is not None else None
            rr, bk, md, master, cfg = load(fn, dm, cfg0)
            print('%s: %d run lines, keys != runkey(master %s, r): %d, max |log2Z recomputed from counts - logged| = %.2e' % (fn.split('\\')[-1], len(rr), master, bk, md))
            rows += rr
        s, _ = summary(' + '.join(x[0].split('\\')[-1] for x in g), rows); print(s)
    for fn in a0s: print(a0chk(fn))
