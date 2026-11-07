"""Print the select-gate program numbers of one row.  usage: python -B nums.py <row dir>"""
import sys, os, json, time
from math import log2, ceil
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(sys.argv[1], "pkg", "blake3", "experiments"))
import bsrho as b
t0 = time.time()
st = b.step256()
ph, filt, body, code, tmax = b.machine_constants(st)
p = b.plan(256); lg = b.ledger(p); ls = b.loss(p)
nodes = len(b.trace(256)[0].nodes)
N = lg["total"]; TL = log2(N / b.UNIT)
print(json.dumps(dict(rounds=b.ROUNDS, unit=b.UNIT, ops=st.ops, by=st.by, gen_calls=st.gen_calls, ph=ph, filt=filt, body=body, code=code, tmax=tmax, nodes=nodes,
                      Tp=p.get("Tp"), P_lower=ls["P_lower"], N=N, TL=TL, TLceil=ceil(TL * 1e5) / 1e5, gen=lg.get("gen"), secs=round(time.time() - t0, 1)), default=str))
