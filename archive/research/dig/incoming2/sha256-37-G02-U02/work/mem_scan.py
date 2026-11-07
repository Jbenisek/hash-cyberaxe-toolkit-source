import math, sys, io, contextlib
sys.argv=['x']
import lowm as L
from fractions import Fraction as Fr
def run():
    with contextlib.redirect_stdout(io.StringIO()):
        o=L.ledger(show=False)
    return o
base=run(); T0=base['time_log2']
tab,tot=L.memory_bytes()
print('baseline time_log2',T0,'log2_T',base['log2_T'],'mem',tot,math.log2(tot),'S',T0+max(0,math.log2(tot)-20))
print('per_fb units',base['per_fb_units'],'FIXED',L.FIXED,'CT_DET',L.CT_DET,'F7_OPS',L.F7_OPS,'vbar',base['vbar'],'C',L.C_REF)
F0=L.FIXED; W0=dict(L.W6_OPS); S0_=dict(L.SUBF_OPS)
# F7 free test
L.FIXED=F0-L.F7_OPS; o=run(); print('F7 test free: time',o['time_log2'],'d',o['time_log2']-T0,'log2_T d',o['log2_T']-base['log2_T'])
# F7 whole class test via bitmap lookup, optimistic 6 prims/class
for per in (6,8):
    L.FIXED=F0-L.CT_DET+per*L.NCLS+0; o=run(); print('F7 bitmap lookup %d/class'%per,'time',o['time_log2'],'d',o['time_log2']-T0)
L.FIXED=F0
# F6 free
for k in L.W6_OPS: L.W6_OPS[k]-=27
for k in L.SUBF_OPS: L.SUBF_OPS[k]-=27
o=run(); print('F6 test free: time',o['time_log2'],'d',o['time_log2']-T0)
L.W6_OPS.update(W0); L.SUBF_OPS.update(S0_)
o=run(); assert o['time_log2']==T0
# G: reps per fb, list rebuild lower bound
reps=sum(cnt*(n>>k) for n,k,cnt in L.CLASS_TYPES)
reps_pf=float(L.P7)*reps
print('total reps (222 classes)',reps,'expected reps in passing classes per fb',reps_pf,'passing classes',222*float(L.P7))
perfb=float(2644+L.FIXED+base['vbar'])
for ppr in (30,40,60):
    add=reps_pf*ppr
    print('list rebuild per fb at %d prim/rep: +%.0f prims of %.0f -> +%.4f bits time'%(ppr,add,perfb,math.log2((perfb+add)/perfb)))
# whole-G scale
Nvar=782800; G=12103680
s=G/Nvar
scal=float(L.CT_DET)+base['vbar']; N0=2644+L.FIXED-L.CT_DET
cur=(N0+scal)/830.988
new=(N0+s*scal)/(s*830.988)
print('wide G (all 12.1M variants, ideal same cost per variant): s=%.3f gain bits time %.4f'%(s,math.log2(cur/new)))
# lists memory
lists=tab['s_planes']+tab['s_entries']
print('list tables bytes',lists,'descr',tab['class_descriptors'],'headroom',(1<<20)-tot)
for scale in (s,):
    m=tot-lists-tab['class_descriptors']+scale*(lists+tab['class_descriptors'])
    print('wide G memory %.0f = 2^%.3f  penalty %.3f bits'%(m,math.log2(m),math.log2(m)-20))
# headroom: how many extra 222-class-equivalents fit under 2^20
extra=((1<<20)-tot)/(lists+tab['class_descriptors']); print('extra class-sets fit under 2^20 at same density: %.2f (x222 classes=%.0f)'%(extra,extra*222))
# gain from adding fraction f of 782800 as extra variants within headroom
s2=1+extra
new2=(N0+s2*scal)/(s2*830.988); print('gain if 1+%.2f scale of classes held: %.4f bits (upper bound, new classes assumed as good as top 222)'%(extra,math.log2(cur/new2)))
print('bitmap 2^32 bits = %d B = 2^%.4f; total %.4f; penalty %.4f'%(1<<29,29,math.log2((1<<29)+tot),math.log2((1<<29)+tot)-20))
print('G descr bytes 222*128=',222*128,'G as 32-bit list',G*4, math.log2(G*4),'classes 22976 x 128 B',22976*128,math.log2(22976*128))
