import lowm, copy, math
b=lowm.ledger(show=False)['log2_T']
def with_(**kw):
    s={k:copy.copy(getattr(lowm,k)) for k in kw}
    for k,v in kw.items(): setattr(lowm,k,v)
    try: return b-lowm.ledger(show=False)['log2_T']
    finally:
        for k,v in s.items(): setattr(lowm,k,v)
print('GROUP_BODY->0',with_(GROUP_BODY=0)); print('PROBE->0',with_(PROBE=(0,0,0,0)))
for i in range(4):
    p=list(lowm.PROBE);p[i]-=1;print('PROBE[%d]-1'%i,with_(PROBE=tuple(p)))
for k in lowm.W6_OPS:
    w=dict(lowm.W6_OPS);w[k]-=1;print('W6',k,lowm.W6_OPS[k],'-1 ->',with_(W6_OPS=w))
for k in lowm.SUBF_OPS:
    w=dict(lowm.SUBF_OPS);w[k]-=1;print('SUBF',k,lowm.SUBF_OPS[k],'-1 ->',with_(SUBF_OPS=w))
print('FIXED-166 (F7 free)',with_(FIXED=lowm.FIXED-166))
for n in ('SCAN_LANE','EX_OPS','SURV_LANE','SURV_FIX','RECOMP','ROWCOMP','ROWCHECK','RARE_LOOKUP','PAD_OPS','CLS_LANE'):
    if hasattr(lowm,n): v=getattr(lowm,n); print(n,v,'-1 ->',with_(**{n:v-1}))
