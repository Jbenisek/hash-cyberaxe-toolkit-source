import math, json
from fractions import Fraction
from g02u02 import *
B0 = bytes_base(); T0, I0 = T(); lg = math.log2
def S(t, b): return t + max(0, lg(b) - 20)
out = {}
out['base'] = dict(T=T0, B=B0, S=S(T0, B0), perFB=2728+35+float(I0['vbar']))
w7mean = float(sum(c*p for (c, ok), p in cal['w7'].items()))
out['w7mean'] = w7mean
# ---- F7T
Tun, _ = T(W7X=0); Bun = B0 - 57*32 + 90*52*32
Tfree, _ = T(W7X=0, W7MEAN=0)
bm_ops = 13  # bitmap test per class incl loop+counter (my count, see notes)
Tbm, _ = T(W7X=0, W7MEAN=bm_ops); Bbm = 2**29 + B0 - 57*32 + 12*32
def be_bytes(dT):  # bytes above 2^20 at which a time gain dT (bits) is paid for
    return 2**20 * (2**dT - 1)
out['F7T'] = dict(
  unrolled=dict(T=Tun, dT=T0-Tun, B=Bun, S=S(Tun, Bun), dB=Bun-B0),
  freetest_bound=dict(T=Tfree, dT=T0-Tfree),
  bitmap=dict(T=Tbm, dT=T0-Tbm, B=Bbm, S=S(Tbm, Bbm)),
  breakeven_total_B_unrolled=2**20 * 2**(T0-Tun), breakeven_B_freetest=2**20*2**(T0-Tfree),
  headroom=2**20-B0, penalty_per_byte_at_2e20=1/(2**20*math.log(2)))
# ---- PL90 / SHC data
worst = None
import re
terms = A.pre_terms(); worst = int(re.search(r'x (\d+) operations', terms[0][0]).group(1))
v = [bin(c[2]).count('1') for c in A.CLASSES]
shp = [bin(A.shape_of(h)[0]).count('1') for h in A.GRP]
planes_b = [15*vi*32 for vi in v]; sh_b = [s*32 for s in shp]
assert sum(planes_b) == 675840 and sum(sh_b) == 11520, (sum(planes_b), sum(sh_b))
out['worst_member_test'] = worst
cost_cls = [2**vi*worst + 4*3840*vi for vi in v]
PREX = -sum(cost_cls)
Tst, Ist = T(CLSX=lambda i: cost_cls[i], PREX=PREX)
Bst = B0 - 675840 + max(planes_b)
exp_cls = float(sum(Fraction(287309824, 2**32)*c for c in cost_cls))
out['PL90'] = dict(v_min=min(v), v_max=max(v), cost_cls_mean=sum(cost_cls)/90, expected_recompute_ops_per_FB=exp_cls,
   M2=dict(T=Tst, dT=Tst-T0, B=Bst, S=S(Tst, Bst), dS=S(Tst,Bst)-S(T0,B0), scratch=max(planes_b)),
   M2_sub=dict(per_class_ops_mean=sum(cost_cls)/90, member_tests_mean=sum(2**vi*worst for vi in v)/90))
# drop-one
gains = []
for i in range(90):
    idx = [j for j in ALL if j != i]; t, _ = T(idx)
    by = planes_b[i] + sh_b[i] + 96
    gains.append((T0 - (T0 - (t - T0)) , 0))  # placeholder
rows = []
for i in range(90):
    idx = [j for j in ALL if j != i]; t, _ = T(idx)
    by = planes_b[i] + sh_b[i] + 96
    rows.append(dict(i=i, gain=t-T0, bytes=by, pen=lg((B0+by)/2**20) if B0+by > 2**20 else 0))
avg_gain = sum(r['gain'] for r in rows)/90; avg_by = sum(r['bytes'] for r in rows)/90
best = max(rows, key=lambda r: r['gain']/r['bytes'])
out['PL90']['M4'] = dict(avg_gain=avg_gain, avg_bytes=avg_by, avg_pen_cross=lg((B0+avg_by)/2**20),
   best=best, best_net=best['gain']-lg((B0+best['bytes'])/2**20), max_gain=max(r['gain'] for r in rows), min_bytes=min(r['bytes'] for r in rows),
   gain_per_KB_avg=avg_gain/avg_by*1024, pen_per_KB=1024/(2**20*math.log(2)))
# ---- SHC
ops_word = 4
Tsh, _ = T(CLSX=lambda i: shp[i]*ops_word)
scr = max(sh_b); Bsh = B0 - 11520 + scr; dT = Tsh - T0
D = 11520 - scr
out['SHC'] = dict(M2=dict(T=Tsh, dT=dT, B=Bsh, S=S(Tsh, Bsh), exp_ops_per_FB=float(sum(Fraction(287309824,2**32)*shp[i]*ops_word for i in range(90))), scratch=scr),
   hold_S=S(T0,B0), headroom_after=2**20-Bsh,
   over_bytes_breakeven=2**20*(2**dT-1), full_cross_penalty=lg(2**20/(2**20-D)),
   S_hold_minus_rec_at=lambda: None)
# S compare above 2^20: hold = T0+log2(B/2^20) ; rec = Tsh + log2((B-D)/2^20)
def cmp_above(Bx):
    return (T0+max(0,lg(Bx)-20)) - (Tsh+max(0,lg(Bx-D)-20))
out['SHC']['S_hold_minus_rec_at_2e20+5000'] = cmp_above(2**20+5000)
out['SHC']['S_hold_minus_rec_at_2e20+20000'] = cmp_above(2**20+20000)
out['SHC']['S_hold_minus_rec_at_B0'] = cmp_above(B0)
del out['SHC']['S_hold_minus_rec_at']
# PL90 hold vs stream above: penalty of holding planes at 2^20+x
out['PL90']['hold_pen_at_2e20'] = lg(2**20/(2**20-(675840-max(planes_b))))
json.dump(out, open('results.json','w'), indent=1, default=str)
print(json.dumps(out, indent=1, default=str))
