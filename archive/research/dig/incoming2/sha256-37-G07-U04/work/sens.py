import sys,json; sys.dont_write_bytecode=True
import lowm as lw
base=lw.ledger(show=False); out={'base_time_log2':base['log2_T'],'vbar':base['vbar'],'FIXED':base['fixed'],'nfb':base['nfb']}
def lt(**kw):
    old={k:getattr(lw,k) for k in kw}
    for k,v in kw.items(): setattr(lw,k,v)
    try: r=lw.ledger(show=False)
    finally:
        for k,v in old.items(): setattr(lw,k,v)
    return r
r=lt(FIXED=lw.FIXED+1); out['per_fixed_op_bits']=r['log2_T']-base['log2_T']
r=lt(GROUP_BODY=lw.GROUP_BODY+1); out['groupbody+1']=dict(dvbar=r['vbar']-base['vbar'],bits=r['log2_T']-base['log2_T'])
r=lt(SCAN_LANE=lw.SCAN_LANE+1); out['scanlane+1']=dict(dvbar=r['vbar']-base['vbar'],bits=r['log2_T']-base['log2_T'])
r=lt(SURV_FIX=lw.SURV_FIX+1); out['survfix+1']=dict(dvbar=r['vbar']-base['vbar'],bits=r['log2_T']-base['log2_T'])
r=lt(PAD_OPS=lw.PAD_OPS+1); out['pad+1']=dict(dvbar=r['vbar']-base['vbar'],bits=r['log2_T']-base['log2_T'])
r=lt(SLACK=lw.Fr(0)); out['slack0_bits']=r['log2_T']-base['log2_T']
r=lt(PRE_OPS=0); out['pre0_bits']=r['log2_T']-base['log2_T']
out['ac_bits_if_2^59']=lw.ledger(show=False,ac_log2=59)['log2_T']-base['log2_T']
json.dump(out,open('sens.json','w'),indent=1,default=float); print(json.dumps(out,indent=1,default=float))
