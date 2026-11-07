"""Ledger parts of the chosen r39 configuration under Lemma 2 v2 (sched_first 39, 1,024 registers, entry 26 B, kappa 13, 20,000 panels)."""
import sys, os, json
from math import log2
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import v2price
import rolled
v = v2price.v
v2price.PANELS = 20000
v._zq = v2price._zq_panels
rolled.set_rounds(39)
b = rolled.b
st = b.step256()
d = rolled.design(39)
oc = b.other_code(st)
body = d["kernel"] + d["filt"] + b.LOOP_OPS
code = (d["instr"] + d["filt"] + b.LOOP_OPS + oc) * 36
regs, entry, kappa = 1024, 26, 13
tmax = (v.MEM_LIMIT - code - regs * 32 - v.COUNTERS - d["mem_arrays"]) // entry
v.machine_constants = lambda st_=None, R=None: (0, 0, body, code, tmax)
p = v.plan(256, kappa, None, regs)
rec = b.packed_ops(st.qwords) + b.RECOVER_EXTRA
gen = b.GEN_FACTOR * (2 * st.gen_calls + st.ops)
parts = [("main loop: B * %d" % body, body * p["B"]),
         ("slice checks: ceil(B / 2^48) * %d" % v.SLICE_OPS, -(-p["B"] // p["Sb"]) * v.SLICE_OPS),
         ("stage-1 hits: e2max * %d" % v.HIT_OPS, p["e2max"] * v.HIT_OPS),
         ("finished trails: tmax * (%d + 3 tmax)" % v.EVENT_OPS, p["tmax"] * (v.EVENT_OPS + 3 * p["tmax"])),
         ("cut trails: %d * %d" % (p["cmax"], v.CUT_OPS), p["cmax"] * v.CUT_OPS),
         ("recovery: capr * %d + 600" % rec, p["capr"] * rec + 600),
         ("setup + generator", v.SETUP_FIXED + gen)]
N = sum(x for _, x in parts)
for k, x in parts:
    print("%-45s %d" % (k, x))
C = 2812
# exact integer certificate 2^E * C^100000 <= N^100000 < 2^(E+1) * C^100000 by bisection on E
lo, hi = 12000000, 12600000
NP, CP = N ** 100000, C ** 100000
while hi - lo > 1:
    m = (lo + hi) // 2
    if (CP << m) <= NP:
        lo = m
    else:
        hi = m
ls = v.loss(p)
print(json.dumps(dict(N=str(N), log2_N_over_C=log2(N / C), certificate="2^%d * 2812^100000 <= N^100000 < 2^%d * 2812^100000" % (lo, lo + 1),
                      time_log2_claim=round((lo + 1) / 100000, 5), Tp=p["Tp"], kappa=kappa, tmax=tmax, B=str(p["B"]), P_lower=ls["P_lower"],
                      theta=ls["theta"], memory=code + regs * 32 + v.COUNTERS + d["mem_arrays"] + entry * tmax, code=code, body=body)))
