# Ledger sensitivities for LOOP / DPF / CTRL / EVALS / RECOV / SETUP / JRECOV (exact ledger of rho.py, fractions), plus the filter truth-table control
import random
from fractions import Fraction
from math import log2, log
from common import rho as R
lg0=R.ledger(256); tot=lg0['total']; T0=log2(tot/638); P=lg0['parts']
print('base time_log2 %.5f ; total ops %.6e'%(T0,float(tot)))
for k,v in P.items(): print('  part %-9s %.4e = %.5f%% of total ; bits if the part were free: %.6f'%(k,float(v),100*float(v/tot),-log2(1-float(v/tot))))
def T(**kw):
    saved={k:getattr(R,k) for k in kw}
    for k,v in kw.items(): setattr(R,k,v)
    try: return log2(R.ledger(256)['total']/638)
    finally:
        for k,v in saved.items(): setattr(R,k,v)
print('--- LOOP R4: batch ops')
for d in (-59,-30,-10,-1,1,10): print('  PH %d: time %+.5f bit'%(595+d,T(PH=595+d)-T0))
print('  per op per batch: %.5f bit'%((T(PH=596)-T(PH=594))/2))
print('--- DPF: filter ops per batch 4 (and/add, and, compare, branch counted as 4; code uses ((z0&mask)+K)&bit32 vs bit32 with s1=32: add, and, cmp, br)')
# stage1 is hard-coded inside ledger(); emulate by changing the per-body arithmetic
def Tbody(stage1=4,U=16,ctrl=3,PH=595):
    per=U*(PH+stage1)+ctrl
    main=Fraction(per,U)*lg0['plan']['B']
    total=tot-P['main']+main
    return log2(total/638)
print('  base via helper %.5f'%Tbody())
for s in (0,1,2,3,5,6,8): print('  filter %d ops: %+.5f bit'%(s,Tbody(stage1=s)-T0))
print('--- CTRL R4: unroll U and loop-control ops')
for U in (1,2,4,8,16,32,64): print('  U=%2d (control 3 per body): %+.5f bit ; code instructions %d'%(U,Tbody(U=U)-T0,U*599+3))
for c in (0,3,6,10): print('  control %d ops per 16 batches: %+.6f bit'%(c,Tbody(ctrl=c)-T0))
print('--- DPF control: truth table of the filter expression ((w0 & s1mask) + REP*0xFFFFFFFF) & bit32 != bit32  <=>  some lane has word0 == 0')
REP=R.REP; bit32=REP<<32; ff=REP*0xFFFFFFFF; s1mask=REP*0xFFFFFFFF
random.seed(3); bad=0; tp=fp=fn=0
for t in range(300000):
    lanes=[random.getrandbits(32) for _ in range(7)]
    k=random.random()
    if k<0.4: lanes[random.randrange(7)]=0
    elif k<0.5: lanes=[random.choice((0,1,0xFFFFFFFF,0x80000000)) for _ in range(7)]
    # garbage in the guard bits of a "clean" word cannot occur (digest words are masked); test clean words
    w=R.pack(lanes)
    flag=((w & s1mask)+ff) & bit32 != bit32
    truth=any(x==0 for x in lanes)
    if flag!=truth: bad+=1
print('  300000 random/edge words: mismatches',bad,'(flag iff some lane word0 == 0)')
# negative control: if the AND with s1mask is dropped and guard bits are dirty, a dirty word fires wrongly
dirty=R.pack([random.getrandbits(36) for _ in range(7)])
print('  negative control (dirty guard bits, no mask) wrongly flags sometimes: ', sum(1 for _ in range(1000) if (((R.pack([random.getrandbits(36) for _ in range(7)]))+ff)&bit32)!=bit32 and True) )
print('--- EVALS R4: sensitivity of time to Q')
for pct in (-1,-0.1,0.1,1): print('  Q %+.1f%%: %+.5f bit'%(pct,log2(1+pct/100)))
print('--- RECOV R4 / JRECOV R2,R4: recovery charge per batch (capr = %d batches)'%lg0['plan']['capr'])
def Trec(per, extra_ops=600, cap=None):
    cap=cap or lg0['plan']['capr']
    rec=cap*per+extra_ops
    return log2((tot-P['recovery']+rec)/638)
for nm,per in (('595 only (no test)',595),('620 = 595+24+1 (claim 125.1081)',620),('624 = 595+26+3 (exact need, proof 3.3)',624),('659 = 595+64 (filed)',659),('700',700),('2*595+64 (both lanes as separate scalar walks)',2*595+64),('1190+... 2 full passes',2*659)):
    print('  %-52s time %.5f  (%+.5f vs filed)'%(nm,Trec(per),Trec(per)-T0))
print('  phase split exact: (a-b)*598 + (b+1)*624 <= capr*624 ; filed charge 659 is %.2f%% above 624'%(100*(659/624-1)))
for nm,mult in (('recovery cap 12L -> expected 3L (not a bound)',Fraction(3,12)),('cap 12L -> 6L',Fraction(6,12))):
    cap=int(lg0['plan']['capr']*mult)
    print('  %-52s time %.5f  (%+.5f)'%(nm,Trec(659,cap=cap),Trec(659,cap=cap)-T0))
print('--- SETUP R4: sizes')
for nm,key in (('init 2000',None),):
    pass
for fac in (1,10**3,10**6,10**12,10**20):
    print('  init x %d: %+.3e bit'%(fac,log2((tot+2000*(fac-1))/tot)))
print('  setup bound used 2000 ; recount proof 3.3: 1 + 287 + 25 + 336 = %d (< 800 stated) ; charged 2000'%(1+287+25+336))
