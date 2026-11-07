"""Summaries of q3gpu runs (PREREG_v3-style): mean of Z, relative sd, one-sided 99% Student bound; stage means;
per-A0 spread of the tail factor; variant-sampler checks; pricing with levers_r38.py's ledger arithmetic.
usage: python stats.py log1 [log2 ...] [--a0 file.a0 ...] [--price]"""

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

import sys, math, re, io, contextlib, runpy

def tq99(df):   # one-sided 99% Student quantile, Cornish-Fisher (exact to ~1e-4 for df >= 30)
    z = 2.3263478740
    return z + (z**3 + z) / (4 * df) + (5 * z**5 + 16 * z**3 + 3 * z) / (96 * df**2) + (3 * z**7 + 19 * z**5 + 17 * z**3 - 15 * z) / (384 * df**3)

RUN = re.compile(r'^run (\d+) key ([0-9a-f]+) log2Z (\S+) stages (.*) ns (.*) f7 (\d+) hits (\d+) bad (\d+)')
def read_logs(fns):
    runs = {}
    for fn in fns:
        for line in open(fn):
            m = RUN.match(line)
            if m:
                key = m.group(2)
                runs[key] = dict(r=int(m.group(1)), lz=float(m.group(3)), st=[float(x) for x in m.group(4).split()],
                                 ns=[int(x) for x in m.group(5).split()], f7=int(m.group(6)), hits=int(m.group(7)), bad=int(m.group(8)))
    return list(runs.values())

def summary(runs, label):
    n = len(runs)
    Z = [2.0 ** (r['lz'] + 101) if r['lz'] > -1e8 else 0.0 for r in runs]
    mz = sum(Z) / n; sd = math.sqrt(sum((z - mz) ** 2 for z in Z) / (n - 1)); t = tq99(n - 1)
    lb = mz - t * sd / math.sqrt(n)
    out = dict(n=n, mean_log2=math.log2(mz) - 101, rel_sd=sd / mz, t=t, bound_log2=math.log2(lb) - 101 if lb > 0 else float('nan'),
               min_log2=math.log2(min(z for z in Z if z > 0)) - 101, max_log2=math.log2(max(Z)) - 101,
               hits=sum(r['hits'] for r in runs), bad=sum(r['bad'] for r in runs), extinct=sum(1 for z in Z if z == 0))
    st = list(zip(*[r['st'] for r in runs if r['lz'] > -1e8]))
    out['stage_means'] = [sum(s) / len(s) for s in st]
    out['stage_sds'] = [math.sqrt(sum((x - mu) ** 2 for x in s) / (len(s) - 1)) for s, mu in zip(st, out['stage_means'])]
    print('%s: %d runs, mean 2^%.4f, relative sd %.4f, min 2^%.4f, max 2^%.4f, one-sided 99%% bound 2^%.4f (%d df, t = %.4f)'
          % (label, n, out['mean_log2'], out['rel_sd'], out['min_log2'], out['max_log2'], out['bound_log2'], n - 1, t))
    print('  stage means (log2, rows 17..22, tail): ' + ' '.join('%.4f' % x for x in out['stage_means']) + '  (+ row 16: -27 exact)')
    print('  stage sds: ' + ' '.join('%.4f' % x for x in out['stage_sds']))
    print('  tail successes %d, failed re-verifications %d, extinct runs %d' % (out['hits'], out['bad'], out['extinct']))
    return out

def a0stats(fns, SR=191773672732):
    acc = [0] * 256; props = [0] * 256; hits = [0] * 256; rj = [0] * 256; a0 = [''] * 256
    for fn in fns:
        for line in open(fn):
            if line.startswith('#'): continue
            j, a, r, ac, pr, hi = line.split(); j = int(j)
            a0[j] = a; rj[j] = int(r); acc[j] += int(ac); props[j] += int(pr); hits[j] += int(hi)
    A = sum(acc); chi = sum((acc[j] - A * rj[j] / SR) ** 2 / (A * rj[j] / SR) for j in range(256))
    print('variant sampler: %d accepted; per-A0 counts vs |R_j|/SR: chi2 = %.1f on 255 df (z = %.2f)' % (A, chi, wh(chi, 255)))
    T = sum(hits) / sum(props)
    lr = [math.log2(hits[j] / props[j] / T) for j in range(256) if hits[j]]
    chi2 = sum((hits[j] - props[j] * T) ** 2 / (props[j] * T) for j in range(256))
    exp_sd = math.sqrt(sum(1 / hits[j] for j in range(256)) / 256) / math.log(2)
    m = sum(lr) / len(lr); sd = math.sqrt(sum((x - m) ** 2 for x in lr) / (len(lr) - 1))
    jmin = min(range(256), key=lambda j: hits[j] / props[j]); jmax = max(range(256), key=lambda j: hits[j] / props[j])
    print('per-A0 tail factor (q3 of an A0 relative to the average, log2): sd %.4f (binomial noise alone %.4f), min %+.4f (A0 %s), max %+.4f (A0 %s);'
          ' heterogeneity chi2 = %.1f on 255 df (z = %.2f); hits per A0 %d..%d'
          % (sd, exp_sd, math.log2(hits[jmin] / props[jmin] / T), a0[jmin], math.log2(hits[jmax] / props[jmax] / T), a0[jmax], chi2, wh(chi2, 255), min(hits), max(hits)))
    var_true = max(0.0, sd ** 2 - exp_sd ** 2)
    print('  implied A0-to-A0 spread of q3 beyond noise: sd %.4f bit' % math.sqrt(var_true))
    return dict(chi_acc=chi, chi_tail=chi2, sd=sd, exp_sd=exp_sd)

def wh(x, k):   # Wilson-Hilferty normal score of a chi-square value
    return ((x / k) ** (1 / 3) - (1 - 2 / (9 * k))) / math.sqrt(2 / (9 * k))

def price(bounds):
    LV = _hca_public_path_text('__HCA_WORKSPACE__/research/sha256grid/map-r38/levers_r38.py')
    with contextlib.redirect_stdout(io.StringIO()):
        g = runpy.run_path(LV)
    from fractions import Fraction
    from decimal import Decimal
    total, log2, C, A70, A64, base = g['total'], g['log2'], g['C'], g['A70'], g['A64'], g['base']
    d_struct = g['d_struct']
    def T(ng): return float(log2(Fraction(total(A70, A70, A64, ng_scale=ng))) - log2(C))
    print('pricing (levers_r38.py ledger; N_G scaled at fixed success bound; units = %d ops):' % C)
    print('  leader ledger rebuilt: %.5f (claimed 72.64; derivative row 72.61489)' % float(base))
    for lab, b in bounds:
        f = Fraction(str(Decimal(2) ** Decimal(str(-102 - b))))
        t1 = T(f); t2 = T(f / (2 - d_struct)); t3 = float(log2(Fraction(total(A70, 1 << 50, A64, ng_scale=f / (2 - d_struct) * Fraction(50, 51)))) - log2(C))
        print('  q3_model 2^-102 -> 2^%.4f (%s): %.5f (%+.4f vs 72.64); with pair budget structural %.6f: %.5f; + A_S 2^50 + no pad: %.5f'
              % (b, lab, t1, t1 - 72.64, float(d_struct), t2, t3))

if __name__ == '__main__':
    args = sys.argv[1:]; a0f = []; logs = []; pr = False; i = 0
    while i < len(args):
        if args[i] == '--a0': a0f.append(args[i + 1]); i += 2
        elif args[i] == '--price': pr = True; i += 1
        else: logs.append(args[i]); i += 1
    res = None
    if logs: res = summary(read_logs(logs), ' + '.join(l.split('\\')[-1].split('/')[-1] for l in logs))
    if a0f: a0stats(a0f)
    if pr:
        b = [('leader fixed-sample 99% bound', -101.0101), ('leader population 99% bound', -101.0051)]
        if res and res['bound_log2'] == res['bound_log2']: b.append(('this study 99% bound', res['bound_log2']))
        price(b)
