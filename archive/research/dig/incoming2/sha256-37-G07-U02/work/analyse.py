import math, json, copy
from fractions import Fraction as Fr
from decimal import Decimal, getcontext
import lowm
base = lowm.ledger(show=False)
T0 = base['time_log2']; print('base', T0, base['nfb'], base['mu_req'])
res = {}
# ---- H4 R2: exact recount of the A_C comparison ----
cpu = 593858; price = 2**21.427
rerun_units = cpu*price
print('re-run charge units log2', math.log2(rerun_units), ' ratio 2^60/rerun', 2**60/rerun_units, ' A_C cpu-s log2', 60-21.427, ' 2^60/593858 =', 2**60/593858/price)
# ratio 2^60 / 593858 CPU-s -> in CPU-s: 2^38.573 / 593858
cpus = 2**(60-21.427); print('A_C in cpu-s', cpus, 'ratio', cpus/cpu)
print('A_S/paper', 2**(50-41.3), 'log2', 50-41.3)
# share of T
for name, v in (('A_C',2**60),('A_S',2**50),('DEV',2**40)):
    print(name, 'share of T', v/ (2**base['log2_T']))
print('PRE_OPS', lowm.PRE_OPS, 'log2 per C', math.log2(lowm.PRE_OPS/lowm.C_REF))
for ac in (52,56,58,59,60,61):
    o = lowm.ledger(ac_log2=ac, show=False); print('ac',ac,o['time_log2'], round(o['time_log2']-T0,5))
# per 1 bit of A_C: dT/d(ac)
o59 = lowm.ledger(ac_log2=59, show=False); print('bits of time per bit of A_C near 60', T0-o59['time_log2'])
# A_S, DEV sensitivity (hand: T = AC+AS+DEV+..)
T = base['log2_T']; Tn = 2**T
print('A_S 2^50->2^41.3 saves', math.log2(Tn)-math.log2(Tn-2**50+2**41.3))
print('A_S -> 0 saves', math.log2(Tn)-math.log2(Tn-2**50), ' DEV->0', math.log2(Tn)-math.log2(Tn-2**40))
print('A_C total -> 0', math.log2(Tn)-math.log2(Tn-2**60))
# ---- H5 R4: bits per primitive ----
def with_(**kw):
    saved = {k: copy.copy(getattr(lowm,k)) for k in kw}
    for k,v in kw.items(): setattr(lowm,k,v)
    try: return lowm.ledger(show=False)
    finally:
        for k,v in saved.items(): setattr(lowm,k,v)
def exact_dT(o): return math.log2(Fr(o['T_num'],o['T_den']).numerator) - math.log2(Fr(o['T_num'],o['T_den']).denominator)
def lg(o): return math.log2(o['T_num']) - math.log2(o['T_den']) if False else o['log2_T']
def d(o): return base['log2_T'] - o['log2_T']
out = {}
print('log2_T base', base['log2_T'])
o = with_(F7_OPS=lowm.F7_OPS-1); out['F7_OPS -1 (166->165)'] = d(o)
o = with_(F7_OPS=0); out['F7_OPS ->0 (free)'] = d(o)
W = dict(lowm.W6_OPS); W2 = {k:v-1 for k,v in W.items()}; out['W6_OPS all -1'] = d(with_(W6_OPS=W2))
W3 = {k:0 for k,v in W.items()}; out['W6_OPS all ->0'] = d(with_(W6_OPS=W3))
S = dict(lowm.SUBF_OPS); out['SUBF_OPS all -1'] = d(with_(SUBF_OPS={k:v-1 for k,v in S.items()}))
out['SUBF_OPS all ->0'] = d(with_(SUBF_OPS={k:0 for k in S}))
out['GROUP_BODY 31->30'] = d(with_(GROUP_BODY=lowm.GROUP_BODY-1))
pr = lowm.PROBE
out['PROBE each -1'] = d(with_(PROBE=tuple(x-1 for x in pr)))
out['FIXED -1'] = d(with_(FIXED=lowm.FIXED-1))
out['FIXED 615->0 (all scalar/control)'] = d(with_(FIXED=0))
out['PRE_OPS (2^38) ->0'] = d(lowm.ledger(show=False, pre_ops=0))
for k,v in out.items(): print('%-40s %.7f bits' % (k, v))
print('GROUP_BODY', lowm.GROUP_BODY, 'PROBE', lowm.PROBE, 'FIXED', lowm.FIXED)
print('names', [n for n in dir(lowm) if n.isupper()][:80])
res['out']=out
# q3: the ledger bits per bit of q3 (context)
o = lowm.ledger(q3_log2=lowm.Q3_LOG2+0.1, show=False); print('q3 +0.1 bit -> T', o['log2_T']-base['log2_T'], 'Q3', lowm.Q3_LOG2)
# ---- H7 R3: control on mu0 / Pcap ----
getcontext().prec = 60
D = Decimal(1) - (Decimal(-10.4)*Decimal(2).ln()).exp()
def mu_req(pcap):
    x = Decimal('0.61') - pcap - Decimal(2)**-60
    return int((-x.ln()/D*10**8).to_integral_value(rounding='ROUND_FLOOR'))+1
def succ(mu, pcap): return 1 - (-(D*mu)).exp() - pcap - Decimal(2)**-60
pc = Decimal(28103)/Decimal(50000000)
m = Decimal(mu_req(pc))/Decimal(10**8); print('mu0 from Pcap 0.00056206:', m, 'succ', succ(m,pc))
m_lo = m - Decimal(1)/Decimal(10**8); print('NEG control mu0-1e-8: succ', succ(m_lo,pc), '>0.39?', succ(m_lo,pc) > Decimal('0.39'))
pc_old = Decimal('0.00035769'); m_old = Decimal(mu_req(pc_old))/Decimal(10**8); print('known answer R37X (fcbc9c83/ffbe30bb-lineage) Pcap 0.00035769 -> mu0', m_old, 'succ', succ(m_old,pc_old))
# wrong-formula negative control: drop Pcap
print('wrong (no Pcap) mu', Decimal(mu_req(Decimal(0)))/Decimal(10**8))
# wrong: no 1-2^-10.4 divisor
x = Decimal('0.61')-pc-Decimal(2)**-60; print('wrong (no H3 divisor) mu', -x.ln())
# Pcap recompute from ledger parts
print('Pcap recomputed', float(Fr(lowm.vmax_fb_value())/(lowm.SLACK**2*base['nfb']*lowm.expected()['vbar'])), 'assumed', float(base['pcap_assumed']), 'slack', lowm.SLACK)
# sensitivity: bits of time per 1e-8 of mu0 and per +1e-5 of Pcap
for dp in (1e-5, 1e-4):
    pcx = pc + Decimal(dp); mx = Decimal(mu_req(pcx))/Decimal(10**8)
    print('Pcap +%g -> mu0 %s, log2 nfb change %.7f' % (dp, mx, math.log2(float(mx)/float(m))))
print('Pcap cap = 0 would give log2(nfb) change', math.log2(float(Decimal(mu_req(Decimal(0)))/Decimal(10**8))/float(m)))
