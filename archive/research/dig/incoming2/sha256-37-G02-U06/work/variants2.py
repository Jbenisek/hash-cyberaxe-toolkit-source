import sys, math, json
import lowm_w as L
from variants import run, ORIG, BASE_B
def S(t,B): return t+max(0,math.log2(B)-20)
M32=L.M32
env=L.Env()
# ---- known-answer: recompute per-l constants from x15 and the l-independent rows 12..14 ----
tx0=env.Lt[0]['tx']; x15_0=L.LW15[0]
a12,a13,a14=(tx0[0][i] for i in (12,13,14)); e12,e13,e14=(tx0[1][i] for i in (12,13,14))
A15b=(tx0[0][15]-x15_0)&M32; E15b=(tx0[1][15]-x15_0)&M32
Yor=a14|a13; Yand=a14&a13; cdiff=e13^e12   # CH(x,y,z)=z^(x&(y^z)), y=e14? see below
# constants folded into immediates: Cfix etc. derived from the trace of row 12..14 and the message words
base0=env.Lt[0]['base']
Cfix=(a12+e12+L.K[16]+L.s1(L.W14X)+L.MX[9])&M32
bad=0
for l in range(32):
    x15=L.LW15[l]
    a15=(A15b+x15)&M32; e15=(E15b+x15)&M32                      # 2 ops
    maj=(a15&Yor)|Yand                                          # 2
    cxA=(L.S0(a15)+maj+(-a12))&M32                              # 8+2 (+maj) : S0 8, add, add
    chv=e13^(e15&(e14^e13))                                      # CH(e15,e14,e13)  2
    C=(Cfix+L.S1(e15)+chv)&M32                                   # S1 8 + 2 adds
    VA=0x20000000|(((a15^0x8000))&0x02808000)                   # 3 ops
    c=env.LC[l]
    ok = (C==c['C'] and cxA==c['cxA'] and e15==c['Ex15'] and a15==c['Ax15'] and VA==env.VA[l])
    bad+= (not ok)
print('per-l constants recomputed from x15: l checked 32, mismatches',bad)
assert bad==0
# VA check detail: ~a15&0x8000 | a15&0x00800000 | a15&0x02000000 vs (a15^0x8000)&0x02808000: bit 15 = ~a15 ok
# ---- table-free ctz check ----
import random
def popc(x,bits):
    # SWAR sequence priced in variants.pop
    x = x-((x>>1)&0x5555555555555555); x=(x&0x3333333333333333)+((x>>2)&0x3333333333333333); x=(x+(x>>4))&0x0F0F0F0F0F0F0F0F
    x=(x+(x>>8)); x=(x+(x>>16)); x=(x+(x>>32)); return x&0x7f
bad=0
for c in range(1,1<<16):
    nc=c&(c-1); b=c^nc; bm=b-1
    bad+= popc(bm,16)!=(c&-c).bit_length()-1
rr=random.Random(5)
for _ in range(200000):
    c=rr.getrandbits(64)|1<<rr.randrange(64); c&= (1<<64)-1
    if c==0: continue
    nc=c&(c-1); b=c^nc; bm=b-1; bad+= popc(bm,64)!=(c&-c).bit_length()-1
print('table-free ctz (c&(c-1), c^nc, b-1, SWAR popcount) mismatches over all 16-bit and 2e5 random 64-bit:',bad)
# ---- ledger variants ----
b=run(); T0=b['log2_T']; out={}
def rec(name,B,o,extra=None):
    d=dict(name=name,B=B,time_log2=o['time_log2'],dT=o['log2_T']-T0,S=S(o['time_log2'],B)); 
    if extra: d.update(extra)
    out[name]=d; print(json.dumps(d))
# PERL per-l constants
ops_new=34-8+2+29
rec('perl_consts_recompute',BASE_B-4096,run(EX_OPS=ops_new),dict(EX_OPS=ops_new))
# S/L* recompute
row=33; common=(15+9)*row; perl_extra=2*row+1
rec('perl_SLstar_recompute',BASE_B-40960+ (40+32)*32,run(RECOMP=ORIG['RECOMP']+common,EXTRA_L=perl_extra),dict(common=common,per_l=perl_extra))
rec('perl_both',BASE_B-4096-40960+(40+32)*32,run(EX_OPS=ops_new,RECOMP=ORIG['RECOMP']+common,EXTRA_L=perl_extra))
# SCAL scalar planes
bg=L.bgen
FBd=ORIG['FB_DET']-bg(L.MB)-(2*len(L.MB)-1)
sw_all=3+bg(L.MB)+bg(L.KZB)+bg(range(32))+bg(L.NBA)
sw_cls=3+2*len(L.MB)+bg(L.KZB)+bg(range(32))+bg(L.NBA)
print('FB_DET',ORIG['FB_DET'],'->',FBd,'SWEEP_OVH',ORIG['SWEEP_OVH'],'-> all',sw_all,'class-only',sw_cls,'cprep',ORIG['cprep_ops'](),'->17')
Z=96*32
def run_cp(**ov):
    L.cprep_ops=lambda: 17
    try: return run(**ov)
    finally: L.cprep_ops=ORIG['cprep_ops']
# note run() restores cprep_ops from ORIG at start, so set after: implement manually
def run_scal(**ov):
    for k,v in ORIG.items(): setattr(L,k,v)
    for k,v in ov.items(): setattr(L,k,v)
    L.cprep_ops=lambda: 17
    L.CT_DET = 2 + L.bgen(range(32)) + 63 + L.F7_OPS + 1 + L.SCAN_FIX
    L.FIXED = 30 + L.CTRL_FB + L.FB_DET + L.CT_DET
    o=L.ledger(show=False)
    for k,v in ORIG.items(): setattr(L,k,v)
    return o
rec('scal_planes_direct_all',BASE_B-Z,run_scal(FB_DET=FBd,SWEEP_OVH=sw_all))
rec('scal_planes_direct_classonly',BASE_B-Z+17*32,run_scal(SWEEP_OVH=sw_cls))
# cv_pre recomputed per group (instead of held)
rec('scal_cvpre_per_group',BASE_B-2048,run(GROUP_BODY=ORIG['GROUP_BODY']+81))
json.dump(out,open('perscal_results.json','w'),indent=1)
