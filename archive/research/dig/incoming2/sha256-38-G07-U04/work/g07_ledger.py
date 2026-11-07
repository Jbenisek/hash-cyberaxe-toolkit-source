# g07_ledger.py - G07-U04 LEDGER.LM3: fresh recount of the shipped a0lean38.py ledger, sensitivities, lane-cost mean vs charged max.

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

import sys, json, math, time, os
EXP = _hca_public_path_text('__HCA_WORKSPACE__/research/tools/build_pkg/scratch/pkgR38M3/pkg/sha256-r38/experiments')
sys.path.insert(0, EXP)
import a0lean38 as L
from fractions import Fraction
t0 = time.time()
cal = L.calibrate()
print('calibrate s', round(time.time() - t0, 1), flush=True)
rows, info = L.ledger(cal=cal, show=True)
N = sum(int(v) for _, v in rows); a, cl = L.certificate(N, 2728)
print('N', N, 'claim', cl, 'log2(N/C)', math.log2(N) - math.log2(2728))
def T(**kw):
    c = dict(cal); c.update(kw.pop('cal', {}))
    r, i = L.ledger(cal=c, show=False, **kw); n = sum(int(v) for _, v in r)
    return math.log2(n) - math.log2(2728), i
base, bi = T()
out = dict(N_FB=info['N_FB'], vbar=float(info['vbar']), vbar_frac=str(info['vbar']), VMAX=info['VMAX'], N=N, claim=str(cl), time_log2=base, cal={k: (v if not isinstance(v, dict) else {str(x): str(y) for x, y in v.items()}) for k, v in cal.items()})
# sensitivities: +1 unit of each ledger input
S = {}
S['fixed_ops_per_fb +1'] = T(cal=dict(fixed=cal['fixed'] + 1))[0] - base
S['step3b_ops +100'] = T(cal=dict(step3b=cal['step3b'] + 100))[0] - base
S['fb_scalars +10'] = T(cal=dict(fb_scalars=cal['fb_scalars'] + 10))[0] - base
S['planes +10'] = T(cal=dict(planes=cal['planes'] + 10))[0] - base
pr = dict(cal['prog']); pr2 = {k: v + 1 for k, v in pr.items()}
S['every plane program +1 instruction'] = T(cal=dict(prog=pr2))[0] - base
S['lane_max +10 (all 3 masks)'] = T(cal=dict(lane_max={k: v + 10 for k, v in cal['lane_max'].items()}))[0] - base
w7 = {k: p for k, p in cal['w7'].items()}
w7b = {(c + 1, ok): p for (c, ok), p in w7.items()}
S['w7 test +1 op'] = T(cal=dict(w7=w7b))[0] - base
S['A_C 2^84 (+6 bits)'] = T(A_C=2**84)[0] - base
S['A_C 2^78 -> 2^74'] = T(A_C=2**74)[0] - base
S['q3 -1 bit'] = T(q3_log2='-98.7838')[0] - base
S['success 0.39->0.40'] = T(succ='0.40')[0] - base
S['cap margin eps 2^-16 -> 2^-14'] = T(eps_log2=14)[0] - base
out['sens_bits'] = S
for k, v in S.items(): print('%-40s %+.6f bit' % (k, v), flush=True)
# lane cost: charged max vs mean over the 256 lane positions, per mask
lm = {}
t1 = time.time()
for mk in sorted({c[2] for c in L.CLASSES}):
    ci = next(i for i, c in enumerate(L.CLASSES) if c[2] == mk)
    cs = [L.lane_cost(ci, ell) for ell in range(256)]
    lm[mk] = dict(max=max(cs), min=min(cs), mean=float(sum(cs)) / 256.0, mean_frac=Fraction(sum(cs), 256))
    print('mask', mk, lm[mk], flush=True)
print('lane scan s', round(time.time() - t1, 1))
meanc = {str(mk): Fraction(lm[mk]['mean']).limit_denominator(1000) for mk in lm}
mean_lane_cal = {mk: -(-lm[mk]['mean_frac'].numerator // lm[mk]['mean_frac'].denominator) for mk in lm}  # mean rounded UP to an integer (ledger needs ints)
tm, im = T(cal=dict(lane_max=mean_lane_cal))
out['lane_cost'] = {str(k): {a: str(b) for a, b in v.items()} for k, v in lm.items()}
out['lanes_term_charged'] = 1714.3396
out['lanes_term_mean'] = float(sum(Fraction(287309824, 2**32) * 3840 * Fraction(1, 4096) * mean_lane_cal[c[2]] for c in L.CLASSES))
out['time_log2_with_mean_lane'] = tm
out['gain_mean_lane_bits'] = base - tm
print('lanes term charged 1714.3396, with mean lane cost', out['lanes_term_mean'], 'time', tm, 'gain bits', base - tm)
json.dump(out, open('g07_ledger.json', 'w'), indent=1, default=str)
