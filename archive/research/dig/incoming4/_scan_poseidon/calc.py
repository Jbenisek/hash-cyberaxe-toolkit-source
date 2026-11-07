import random, math, json
import numpy as np
from math import log2, exp
C=237
# fix ledger
init=143597; line,rnd,build,power=3910,3,43338189,45559521537
d_budget,d_gap,scan=8800000000,214000000,400000
e_budget,e_gap,fg=10000000,2500000,200000
def tot(pc=None, **kw):
    d=dict(init=init,line=line,rnd=rnd,build=build,power=power,d_budget=d_budget,d_gap=d_gap,scan=scan,e_budget=e_budget,e_gap=e_gap,fg=fg,nc=2)
    d.update(kw)
    pc=d['line']+d['rnd']+d['build']+d['power']+d['d_budget']+d['d_gap']+d['scan']
    return d['init']+d['nc']*pc+d['e_budget']+d['e_gap']+d['fg'], pc
N,pc=tot()
out={}
out['N_fix']=N; out['units']=N/C; out['t_fix']=log2(N/C); out['pc']=pc
out['t_one']=log2((init+pc+e_budget+e_gap+fg)/C)
# stage shares per centre
for k,v in dict(line=line,build=build,power=power,d_budget=d_budget,d_gap=d_gap).items(): out['share_'+k]=v/pc
# bits saved if stage cost -> 0 (2 centres)
for k in ['init','build','power','d_budget']:
    N2,_=tot(**{k:0}); out['drop_'+k]=log2(N/C)-log2(N2/C)
# newton
newton=302883363
N2,_=tot(power=power-newton); out['drop_newton_bits']=log2(N/C)-log2(N2/C); out['newton_share_pc']=newton/pc
out['newton_quadratic_mults']=39061*39062//2
# E / split
for eb in (0,761102,1541920,10000000):
    N2,_=tot(e_budget=eb); out['E_budget_%d'%eb]=log2(N2/C)
out['splitE_bits']=log2(N/C)-log2(tot(e_budget=0,e_gap=0)[0]/C)
# fg
out['fg_bits']=log2(N/C)-log2(tot(fg=0)[0]/C)
# types (fix run, 2 centres)
T=dict(add=2715539688,sub=2534837889,mul=2470953120,sqr=66646268,ld=2997348202,st=1663304782,ctl=90411597007,unit=46596096)
arith=T['add']+T['sub']+T['mul']+T['sqr']; tp=sum(T.values())
out['types_total']=tp; out['arith_share']=arith/tp
for k in ['ld','st','ctl']:
    out['share_'+k]=T[k]/tp
    out['bits_if_free_'+k]=log2(tp/(tp-T[k]))
# ctl floor: arith+ld+st+addr(ld+st)+unit
floor=arith+T['ld']+T['st']+T['ld']+T['st']+T['unit']
out['floor_total']=floor; out['floor_bits']=log2(tp/floor); out['ctl_addr_part']=T['ld']+T['st']; out['ctl_other_part']=T['ctl']-T['ld']-T['st']
for f in (2,4,8):
    out['bits_ctl_div_%d'%f]=log2(tp/(tp-T['ctl']+T['ctl']/f))
out['bits_ctl_addr_only_free']=log2(tp/(tp-T['ld']-T['st']))
out['mul_sqr_share']=(T['mul']+T['sqr'])/tp
for f in (0.5,):
    out['bits_mul_half']=log2(tp/(tp-(T['mul']+T['sqr'])*0.5))
# old ledger (lean_r1 note, free addressing)
Nold=14202616031; out['t_old']=log2(Nold/C)
# memory
mem=8638495; out['mem_bits']=log2(mem)-20
for nm,sav in dict(twid=524288, tmp=1048576, Y=3145728, MU=1249952).items():
    out['memsave_'+nm]=log2(mem)-log2(mem-sav)
out['mem_floor_1MiB']=log2(mem)-20
out['p331']=None
# centres
q1=1-exp(-.5)
for c in (1,2,3):
    pcc=init+c*pc+e_budget+e_gap+fg
    p=1-(1-q1)**c
    out['c%d'%c]=dict(t=log2(pcc/C),P=p,t_over_P=log2(pcc/C/p))
# measured
q=28/65
for c in (1,2,3): out['meas_c%d'%c]=1-(1-q)**c
out['wilson_lo_two']=1-(1-0.318)**2
# Poisson histogram
pois=[exp(-.5)*.5**k/math.factorial(k) for k in range(6)]
out['pois']=pois; out['P_gt8']=1-sum(exp(-.5)*.5**k/math.factorial(k) for k in range(9))
# fresh run
out['fresh_total']=51453520952; out['fresh_units']=51453520952/C
# toy
rng=np.random.default_rng(12345)
p=10007; deg=120
sq=np.unique((np.arange(1,p)**2)%p).astype(np.int64)
N0=0;hist={};sqfree=0;trials=3000
for t in range(trials):
    co=rng.integers(0,p,size=deg).astype(np.int64)  # monic: x^deg + ...
    v=np.ones_like(sq)
    acc=np.zeros_like(sq)
    acc=(sq.copy())  # Horner start: monic coefficient 1 -> x
    # compute g(S)=S^deg + sum co[i] S^i via Horner
    acc=np.ones_like(sq)
    for i in range(deg-1,-1,-1):
        acc=(acc*sq+co[i])%p
    k=int((acc==0).sum())
    hist[k]=hist.get(k,0)+1
out['toy_hist']=dict(sorted(hist.items())); out['toy_trials']=trials; out['toy_nsq']=len(sq)
out['toy_succ']=1-hist.get(0,0)/trials
out['toy_p1']=hist.get(1,0)/trials
json.dump(out,open('calc.json','w'),indent=1)
print(json.dumps(out,indent=0))
