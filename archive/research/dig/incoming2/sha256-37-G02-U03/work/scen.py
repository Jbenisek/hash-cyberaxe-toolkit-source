import math, json, copy
from fractions import Fraction as Fr
import lowm_copy as L
base = dict(PROBE=L.PROBE, GROUP_BODY=L.GROUP_BODY, SURV_FIX=L.SURV_FIX, SURV_LANE=L.SURV_LANE, EX_OPS=L.EX_OPS, PNZ=L.PNZ, MU=L.MU)
def run(name, mem, **kw):
    for k, v in base.items(): setattr(L, k, v)
    for k, v in kw.items(): setattr(L, k, v)
    o = L.ledger(show=False)
    e = L.expected()
    S = o['time_log2'] + max(0, math.log2(mem) - 20)
    r = dict(name=name, mem=mem, time_log2=o['time_log2'], nfb=o['nfb'], vbar=o['vbar'], per_fb=o['per_fb_units'], S=S)
    print(json.dumps(r)); return r
tab, tot = L.memory_bytes(); M0 = tot
out = {}
out['ship'] = run('shipped LO+MID', M0)
# direct: no chunk tables; per group 32 l x 6 ops + 8 = 200 ops (our bound), same survivors
out['direct'] = run('no tables, direct filt', M0 - 262144, PROBE=(50,50,50,50))
# no filter at all: every l exact-tested for every lane
out['nofilt'] = run('no filter, exact test all 32 l', M0 - 262144, PROBE=(0,0,0,0), SURV_FIX=0, PNZ=Fr(1), MU=Fr(32))
# ideal oracle: free membership, only rare path
out['oracle'] = run('oracle free membership (lower bound on time)', M0 - 262144 + 8388608 + 33*4, PROBE=(0,0,0,0), SURV_FIX=0, SURV_LANE=0, EX_OPS=0)
out['oracle_nomem'] = run('oracle ignoring memory', M0, PROBE=(0,0,0,0), SURV_FIX=0, SURV_LANE=0, EX_OPS=0)
# HI table (9th condition bit 30): extra probe ops e per group; PNZ, MU halved approx (exact value unknown: 9 cond -> MU=32/512)
for e in (0, 4, 6, 8, 12):
    out['hi%d'%e] = run('HI table +%d ops/group'%e, M0 + 256*32, PROBE=(11,12,12,12+e), PNZ=Fr(1521152,1<<24)*Fr(1,2)*Fr(1), MU=Fr(32,512))
# pair list materialised: store+load per group
out['mat'] = run('pairs materialised (store+load per group)', M0 + 1, GROUP_BODY=L.GROUP_BODY + 2)
json.dump(out, open('scen_out.json','w'), indent=1)
