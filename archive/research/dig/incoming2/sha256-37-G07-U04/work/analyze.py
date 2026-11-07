import sys,json,math; sys.dont_write_bytecode=True
import numpy as np, pandas as pd
import lowm as lw
def load(f):
    d=pd.read_csv(f); 
    d['v_scan']=6*d.classes
    d['v_pass']=d.cprep+d.sweep+d.w6+d.spill+d.runs+d.scan_etc+d.member-d.pad
    d['v_grp']=d.group+d.probe+d.pad
    d['v_surv']=d.surv
    d['v_rare']=d.total-615-(d.v_scan+d.v_pass+d.v_grp+d.v_surv)   # rare + step3b rows 16.. (all remaining categories)
    d['v_tot']=d.total-615
    d['fixed_chk']=d.total-d.v_tot
    return d
ex=lw.expected(); P7=float(lw.P7); Ecl=222*P7; Epr=float(ex['g'])
CH={'v_scan':float(ex['ct_var']),'v_pass':float(ex['perclass']),'v_grp':float(ex['grp']),'v_surv':float(ex['surv']),'v_rare':float(ex['rare']),'v_tot':float(ex['vbar'])}
def cvadj(y,x1,x2,m1,m2):
    X=np.column_stack([np.ones(len(y)),x1-m1,x2-m2]); beta,res,_,_=np.linalg.lstsq(X,y,rcond=None)
    r=y-X@beta; n=len(y); s2=r@r/(n-3); cov=s2*np.linalg.inv(X.T@X); return beta[0],math.sqrt(cov[0,0])
def table(d,label):
    n=len(d); out={'n':n,'blocks_no_pass':int((d.classes==0).sum()),'no_pass_total_all_615':bool((d.total[d.classes==0]==615).all()),'min_total':int(d.total.min()),'rare_resid_nonzero_without_r16':int(((d.v_rare!=0)&(d.r16==0)).sum()),'blocks_with_r16':int((d.r16>0).sum())}
    cl=d.classes.values; pr=d.pairs.values
    out['classes_mean']=cl.mean(); out['classes_exact']=Ecl; out['classes_z']=(cl.mean()-Ecl)/(cl.std(ddof=1)/math.sqrt(n))
    out['pairs_mean']=pr.mean(); out['pairs_exact']=Epr; out['pairs_z']=(pr.mean()-Epr)/(pr.std(ddof=1)/math.sqrt(n)); out['pairs_vmr']=pr.var(ddof=1)/pr.mean()
    rows={}
    for k,ch in CH.items():
        y=d[k].values.astype(float); m=y.mean(); se=y.std(ddof=1)/math.sqrt(n)
        a,sa=cvadj(y,cl,pr,Ecl,Epr)
        def verdict(m_,s_):
            lo,hi=m_-2.576*s_,m_+2.576*s_
            return 'COVERED' if lo<=ch<=hi else ('UNDER' if ch<lo else 'OVER')
        rows[k]=dict(charged=ch,raw=m,raw_se=se,raw_verdict=verdict(m,se),cv=a,cv_se=sa,cv_lo=a-2.576*sa,cv_hi=a+2.576*sa,cv_verdict=verdict(a,sa),cv_diff=a-ch)
    out['rows']=rows
    # H3(b) row16 factor
    N=pr.astype(float); r=d.r16.values.astype(float)
    def F(idx):
        return (r[idx]*(r[idx]-1)).sum()/(N[idx]*(N[idx]-1)).sum() / ((r[idx].sum()/N[idx].sum())**2)
    allidx=np.arange(n); out['F_all']=F(allidx)
    b=np.array_split(allidx,20); Fs=[F(i) for i in b]; out['F_batch_mean']=float(np.mean(Fs)); out['F_batch_se']=float(np.std(Fs,ddof=1)/math.sqrt(20))
    out['r16_total']=int(r.sum()); out['r16_per_block']=r.mean(); out['r16_exp_per_block']=float(ex['rare'] and (Epr+3)*float(lw.R16F))
    out['pair_hits_extra']=float((r*(r-1)).sum()/max(1,r.sum()))
    return out
if __name__=='__main__':
    d=load(sys.argv[1]); t=table(d,sys.argv[1]); json.dump(t,open(sys.argv[2],'w'),indent=1,default=float)
    print(json.dumps(t,indent=1,default=float))
