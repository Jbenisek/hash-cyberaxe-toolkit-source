import math, json
from fractions import Fraction as Fr
import g02_mem as g
S=g.Sscore
res={}
# groups per FB (table line) and probe delta for chunk tables (lowm constants)
r1=g.ledger_param(1)
groups=r1['groups_per_fb']
dgrp=Fr(sum(g.l.PROBE)-sum(g.x.PROBE_OPS)) + 4*(g.l.PNZ*g.l.SURV_FIX + g.l.MU*(g.l.SURV_LANE+g.l.EX_OPS))
print('groups/FB',groups,'delta ops per group (chunk probe + survivors)',float(dgrp),'-> +%.0f ops/FB'%(groups*float(dgrp)))
CH=2*4096*32   # two 4096-word chunk tables
lane_w=2; LS=165*(1<<24)*lane_w; VAR=782800*8; CODE=1<<16; CLS=222*4*32
ANC_tab=LS+VAR+CODE+CLS
print('ANC lane-scan bytes w=2,4,8:',[165*(1<<24)*w for w in (2,4,8)],'log2',[math.log2(165*(1<<24)*w) for w in (2,4,8)],'variants',VAR)
def grid(label, mode, r16=g.R16T_B, anc=g.ANC_B, scan_lane=None, pgd=Fr(0), ks=range(0,46)):
    best=None; rows=[]
    for k in ks:
        r=g.ledger_param(1<<k,mode,scan_lane=scan_lane,probe_delta_group=pgd)
        m=g.mem_bound(1<<k,r16,anc); s=S(r['tl'],m); rows.append((k,r['tl'],m,s))
        if best is None or s<best[3]: best=rows[-1]
    return rows,best
variants={
 'D126 held R16T, ANC<2^33':('d126',g.R16T_B,g.ANC_B,None,Fr(0)),
 'reject-early held R16T, ANC<2^33':('rej',g.R16T_B,g.ANC_B,None,Fr(0)),
 'reject-early R16T->chunk tables':('rej',CH,g.ANC_B,None,dgrp),
 'reject-early R16T->chunk, ANC lane-scan->debruijn':('rej',CH,VAR+CODE+CLS,9,dgrp),
 'reject-early held R16T, ANC lane-scan->debruijn':('rej',g.R16T_B,VAR+CODE+CLS,9,Fr(0)),
}
allrows={}
for name,(mode,r16,anc,sl,pg) in variants.items():
    rows,best=grid(name,mode,r16,anc,sl,pg); allrows[name]=rows
    print('%-52s best k=%d T=%.5f mem=%d (2^%.3f) S=%.5f | k0 S=%.5f'%(name,best[0],best[1],best[2],math.log2(best[2]),best[3],rows[0][3]))
json.dump({n:[(k,t,m,s) for k,t,m,s in rows] for n,rows in allrows.items()},open('grid.json','w'))
# detail rows for key variant
for name in ['reject-early held R16T, ANC<2^33','reject-early R16T->chunk tables','reject-early R16T->chunk, ANC lane-scan->debruijn']:
    print(name)
    for k,t,m,s in allrows[name]:
        if k in (0,3,4,5,6,8,10,11,12,13,15,20,25,30,31,35,40,45): print('  k=%2d T=%.5f mem2^%.3f S=%.5f'%(k,t,math.log2(m),s))
# debruijn-only time effect at k=0
a=g.ledger_param(1); b=g.ledger_param(1,scan_lane=9); print('debruijn k=0: T %.6f -> %.6f  (+%.6f bits); vbar %.2f -> %.2f'%(a['tl'],b['tl'],b['tl']-a['tl'],a['vbar'],b['vbar']))
c=g.ledger_param(1,probe_delta_group=dgrp); print('chunk R16T k=0: T %.6f -> %.6f (+%.6f bits); vbar %.2f -> %.2f'%(a['tl'],c['tl'],c['tl']-a['tl'],a['vbar'],c['vbar']))
# table-free lowm like-for-like
lo=g.l.ledger(show=False); lo2=g.l.ledger(q3_log2=g.x.Q3_LOG2,show=False)
print('lowm own q3 -71.47: T %.5f mem 607744 S %.5f ; lowm at table-line q3 -74.03: T %.5f vbar %.1f nfb %d'%(lo['time_log2'],lo['time_log2'],lo2['time_log2'],lo2['vbar'] if 'vbar' in lo2 else 0,lo2['nfb']))
