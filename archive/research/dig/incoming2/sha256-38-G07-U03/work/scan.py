import sys, os, json, math, io, contextlib, random
from fractions import Fraction as Fr
W = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(W, 'src')); sys.dont_write_bytecode = True
import ledger38 as L
L.RUNS = os.path.join(W, 'runs_fresh')   # freshly metered pre1/pre2 (identical to shipped)
shutil = __import__('shutil'); shutil.copy(os.path.join(W, 'runs', 'costs.json'), L.RUNS)
def led(**k):
    with contextlib.redirect_stdout(io.StringIO()):
        return L.ledger(show=False, **k)
res = {}
b = led(); res['filed'] = {k: b[k] for k in ('time_log2', 'NG', 'NG_log2', 'pre_ops', 'pre_units_log2', 'online_ops_log2', 'cap_overflow_total', 'success_lower_bound', 'NE_MAX', 'NW_MAX', 'N1_MAX', 'N2_MAX', 'E_NE', 'E_NW', 'E_N1', 'E_N2', 'pre_terms', 'allow_log2')}
# R3 control: base (37742a53) reproduces 71.695220; delta=0 / 1 / 1.5
base = led(base=True, delta=Fr(1)); res['base_delta1_time'] = base['time_log2']
res['base_flag'] = led(base=True, delta=Fr(141,250))['time_log2']
for d in (Fr(0), Fr(1,2), Fr(1), Fr(3,2)):
    r = led(delta=d); res['delta_%s' % d] = (r['time_log2'], r['NG_log2'])
# D7 line: delta1 near 0.080 x 0.296687 + far 0.484
d7 = Fr(80, 1000) * Fr(296687, 10**6) + Fr(484, 1000)
r = led(delta=d7); res['D7_delta'] = float(d7); res['D7_time'] = (r['time_log2'], r['NG_log2'], r['NG'])
r2 = led(delta=Fr(80,1000) * Fr(293, 1000) + Fr(484,1000)); res['D7_point293'] = r2['time_log2']
# sensitivity of delta (bits per 0.1 delta), numerical derivative
a = led(delta=Fr(55,100)); c = led(delta=Fr(57,100)); res['d_time_per_delta'] = (c['time_log2'] - a['time_log2']) / 0.02
res['d_NGlog2_per_delta'] = (c['NG_log2'] - a['NG_log2']) / 0.02
# PREP R4: +1 op per item in each executed body (p2 / p1) and exact pre share
p1 = json.load(open(os.path.join(L.RUNS, 'pre1.json'))); p2 = json.load(open(os.path.join(L.RUNS, 'pre2.json')))
t0 = b['time_log2']; sens = {}
for k in list(p2):
    q = dict(p2); q[k] += 1; sens['p2.' + k] = led(p2=q)['time_log2'] - t0
for k in ('G_hit_ops', 'F7_in_ops', 'A2_hit_ops', 'LIVE_ops'):
    q = dict(p1); q[k] += 1; sens['p1.' + k] = led(p1=q)['time_log2'] - t0
res['sens_plus1_op_bits'] = sens
# exact (unrounded) log2 T and the 1e-5 round-up slack
res['log2_T_exact'] = b['log2_T']; res['roundup_slack_bits'] = b['time_log2'] - b['log2_T']
# pre share of T
res['pre_share_of_T'] = b['pre_ops'] / 2728 / 2 ** b['log2_T']
res['pre_share_log2_terms_top'] = sorted(b['pre_terms'].items(), key=lambda x: -x[1])[:4]
# what-if: zero preprocessing (upper limit of any prep shave)
zero = dict(p2);
res['no_pre_whatif'] = None
import types
orig = L.pre_ops
L.pre_ops = lambda *a, **k: {'z': 0}
res['no_pre_whatif'] = led()['time_log2'] - t0
L.pre_ops = orig
# CAP: R1 charged margins and cost; sensitivity
res['cap_total_overflow'] = b['cap_overflow_total']; res['cap_budget'] = 'success bound 0.39 required'
for name, e in (('eps_2^-8', Fr(1, 2**8)), ('eps_2^-4', Fr(1, 16)), ('eps_2^-3', Fr(1, 8))):
    res['cap_' + name] = led(eps=e)['time_log2'] - t0
# cap inflation of online ops: online with MAX (1+eps) vs expected-only
NG = b['NG']; E = {k: b[k] for k in ('E_NE', 'E_NW', 'E_N1', 'E_N2')}
res['cap_inflation_bits_of_online'] = None
cs = json.load(open(os.path.join(L.RUNS, 'costs.json')))
# online with N_MAX replaced by NG*E (no eps) -> time difference via eps -> tiny eps not allowed, so compute directly
infl = (cs['ITER'] // 2) * ((b['NE_MAX'] - NG * E['E_NE'])) + 43 * (b['NW_MAX'] - NG * E['E_NW']) + b['c1'] * (b['N1_MAX'] - NG * E['E_N1']) + b['c2'] * (b['N2_MAX'] - NG * E['E_N2'])
res['cap_eps_inflation_ops'] = infl; res['cap_eps_inflation_bits_of_T'] = math.log2(1 + infl / 2728 / 2 ** b['log2_T'])
# the bucket-bound (B_k) terms are the real cap cost: (B_NE etc.) /C
ngw = 22; MAXB = 14 * ngw * 768; B_ent = 256 * MAXB
Bops = (cs['ITER'] // 2) * (2 * (B_ent + 256) ) + 43 * B_ent + b['c1'] * B_ent + b['c2'] * B_ent
res['cap_B_terms_ops'] = Bops; res['cap_B_terms_bits_of_T'] = math.log2(1 + Bops / 2728 / 2 ** b['log2_T'])
# CAP R3 negative control: tiny eps must break the success guard
try:
    led(eps=Fr(1, 2**40)); res['cap_negctl_tiny_eps'] = 'NO FAILURE (bad)'
except Exception as ex:
    res['cap_negctl_tiny_eps'] = 'raised %s' % type(ex).__name__
# CAP R3 known-answer: Chebyshev toy. X in {0,B} per group (max variance for bound B), mean E
rng = random.Random(38070301); import numpy as np
g = np.random.default_rng(380703)
NGt, Et, Bt, epst = 10000, 1.0, 10, 0.5
bound = Bt / (epst ** 2 * NGt * Et)
reps = 200000
tot = Bt * g.binomial(NGt, Et / Bt, size=reps)
emp = float(np.mean(tot > (1 + epst) * NGt * Et))
# tighter toy where empirical is not 0: eps small
NGt2, epst2 = 400, 0.25
b2 = Bt / (epst2 ** 2 * NGt2 * Et)
tot2 = Bt * g.binomial(NGt2, Et / Bt, size=reps)
emp2 = float(np.mean(tot2 > (1 + epst2) * NGt2 * Et))
res['cap_toy'] = dict(bound1=bound, emp1=emp, bound2=b2, emp2=emp2, ok=(emp <= bound and emp2 <= b2))
# NG R3: Clopper-Pearson recompute of delta7 from the t4 raw counts + control law
from math import comb
def cp_upper(k, n, alpha):
    lo, hi = k / n, 1.0
    # binary search P(X<=k | p) = alpha, via log-sum using normal-free exact: use betainc through scipy if available
    try:
        from scipy.stats import beta
        return float(beta.ppf(1 - alpha, k + 1, n - k))
    except Exception:
        return None
res['delta7_cp99_oneside'] = cp_upper(2491, 8499, 0.01)
res['delta7_cp99_twoside_upper'] = cp_upper(2491, 8499, 0.005)
res['delta7_point'] = 2491 / 8499
res['control_rate'] = 12113 / 1591808; res['control_log2'] = math.log2(12113 / 1591808)
# recount from raw files
def tally(fn):
    n = 0; keys = None
    for line in open(fn, encoding='utf-8'):
        n += 1
        if keys is None: keys = list(json.loads(line).keys())
    return n, keys
T4 = os.path.join(W, '..', '..', '..', '..', 'retest', 't4')
res['t4_raw'] = {f: tally(os.path.join(T4, f)) for f in ('raw_A.jsonl', 'raw_B.jsonl')}
json.dump(res, open(os.path.join(W, 'scan_out.json'), 'w'), indent=1, default=str)
print(json.dumps(res, indent=1, default=str))

