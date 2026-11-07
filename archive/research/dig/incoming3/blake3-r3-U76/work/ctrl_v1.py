# Ledger control: meter the shipped program (rho.search / rho.recover, unchanged) at n=22 and n=32 on the real 3-round target
# and compare every metered quantity with the corresponding ledger bound of plan(n)/ledger(n).
# usage: ctrl.py N ATTEMPTS SEED
import sys, time, os, hashlib
from fractions import Fraction
from math import log2, exp
from common import rho as R
n=int(sys.argv[1]); A=int(sys.argv[2]); seed=sys.argv[3]
p=R.plan(n); lg=R.ledger(n); P=lg['parts']
stage1=4+(1 if p['s1']<32 else 0)
meter=dict(rec_batches=0, rec_calls=0)
orig_batch=R.batch
orig_recover=R.recover
state={'in':False}
def wb(*a):
    if state['in']: meter['rec_batches']+=1
    return orig_batch(*a)
def wrec(pp,r,a,b):
    state['in']=True; meter['rec_calls']+=1; meter['rec_a']=max(meter.get('rec_a',0),a[1],b[1])
    try: return orig_recover(pp,r,a,b)
    finally: state['in']=False
R.batch=wb; R.recover=wrec
succ=halt=0; mx=dict(batches=0,stage2=0,finished=0,rec=0); maxfrac=0; maxlen_over=0
recmax=0; t0=time.time(); done=0
for a in range(A):
    if time.time()-t0>270: break
    r=int.from_bytes(hashlib.shake_256(("%s/%d"%(seed,a)).encode()).digest(32),'little')&(p['N']-1)
    meter['rec_batches']=0; meter['rec_calls']=0
    try:
        res,cnt=R.search(p,r)
    except R.Halt:
        halt+=1; done+=1; continue
    done+=1
    if res is not None: succ+=1
    mx['batches']=max(mx['batches'],cnt['batches']); mx['stage2']=max(mx['stage2'],cnt['stage2']); mx['finished']=max(mx['finished'],cnt['finished'])
    recmax=max(recmax,meter['rec_batches'])
    # metered ops of this attempt, charged at the ledger's per-item prices
    ops=(Fraction(lg['per_body'],R.U_UNROLL)*cnt['batches'] + cnt['stage2']*R.STAGE2_OPS
         + cnt['finished']*(R.DP_EVENT_OPS+3*p['tmax']) + meter['rec_batches']*(R.PH+R.RECOVER_EXTRA)+600 + 2000)
    maxfrac=max(maxfrac, float(ops/lg['total']))
print('n=%d attempts run %d (time %.0fs) successes %d halts %d  success rate %.4f  halted %.4f'%(n,done,time.time()-t0,succ,halt,succ/max(done,1),halt/max(done,1)))
print('plan: B=%d (ledger batches), E2max=%d, tmax=%d, capr=%d, c=%d, Sb=%d'%(p['B'],p['e2max'],p['tmax'],p['capr'],p['c'],p['Sb']))
print('max metered: batches %d (%.3f of B), stage2 %d (%.4f of E2max), finished trails %d (%.3f of tmax), recovery batches %d (%.4f of capr), max stored trail length seen %d'%(
    mx['batches'],mx['batches']/p['B'],mx['stage2'],mx['stage2']/p['e2max'],mx['finished'],mx['finished']/p['tmax'],recmax,recmax/p['capr'],meter.get('rec_a',0)))
print('largest metered attempt total / ledger total (must be <= 1): %.4f'%maxfrac)
lam=-log2(1)  # placeholder
print('predicted success: 1-exp(-lambda)=%.4f minus losses (proof: >= 0.3915 at n=256; at small n the in-flight and cut losses are relatively larger)'%(1-exp(-0.497)))
