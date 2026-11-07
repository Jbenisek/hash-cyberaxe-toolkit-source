import sys, math, json
sys.argv=['x']
import lowm_w as L
BASE_B = 607744
ORIG = {k: getattr(L, k) for k in ('SCAN_FIX','SCAN_LANE','CLS_LANE','SURV_FIX','SURV_LANE','EX_OPS','CT_DET','FIXED','FB_DET','SWEEP_OVH','RECOMP','EXTRA_L','GROUP_BODY','cprep_ops')}
def ceil_div(a,b): return -(-a//b)
def plane_scan_fix(w):
    tot=0
    for r in range(4):
        tot += (1 if r in (0,3) else 2)
        n = ceil_div(64,w)
        if n==1: tot += 1
        else: tot += sum((1 if k in (0,n-1) else 2)+1 for k in range(n))
    return tot
def surv_fix(w):
    n=ceil_div(32,w)
    if n==1: return 1+1
    return 1+sum((1 if k in (0,n-1) else 2)+1 for k in range(n))
def pop(bits):
    return 7 if bits<=4 else 10 if bits<=8 else 13 if bits<=16 else 16 if bits<=32 else 19
def run(**ov):
    for k,v in ORIG.items(): setattr(L,k,v)
    for k,v in ov.items(): setattr(L,k,v)
    if 'SCAN_FIX' in ov or 'FB_DET' in ov:
        L.CT_DET = 2 + L.bgen(range(32)) + 63 + L.F7_OPS + 1 + L.SCAN_FIX
        L.FIXED = 30 + L.CTRL_FB + L.FB_DET + L.CT_DET
    o = L.ledger(show=False)
    for k,v in ORIG.items(): setattr(L,k,v)
    return o
if __name__=='__main__':
    assert plane_scan_fix(11)==70 and surv_fix(11)==8, (plane_scan_fix(11), surv_fix(11))
    b = run(); print('base', b['time_log2'], b['log2_T'], 'FIXED', ORIG['FIXED'], 'nfb', b['nfb'])
    assert b['time_log2']==60.99099
    T0=b['log2_T']; res=[]
    def S(t,B): return t+max(0,math.log2(B)-20)
    # table w sweep
    for w in range(3,17):
        o=run(SCAN_FIX=plane_scan_fix(w), SURV_FIX=surv_fix(w))
        B=BASE_B-65536+(1<<w)*32
        res.append(dict(kind='table',w=w,table_B=(1<<w)*32,B=B,time_log2=o['time_log2'],dT=o['log2_T']-T0,S=S(o['time_log2'],B)))
    # table-free
    for w in (4,8,11,16,32,64):
        pc=pop(w-1)
        sl=8-2+1+1+pc-(1 if w>=64 else 0); cl=6-2+1+1+pc-(1 if w>=64 else 0); su=7-2+1+1+pc-(1 if w>=32 else 0)
        o=run(SCAN_FIX=plane_scan_fix(w), SURV_FIX=surv_fix(w), SCAN_LANE=sl, CLS_LANE=cl, SURV_LANE=su)
        B=BASE_B-65536
        res.append(dict(kind='tablefree',w=w,lane=(sl,cl,su),B=B,time_log2=o['time_log2'],dT=o['log2_T']-T0,S=S(o['time_log2'],B)))
    for r in res: print(json.dumps(r))
    json.dump(res,open('scant_results.json','w'),indent=1)
