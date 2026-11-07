"""J2 toy: R3->R4 interface. Exhaustive over all q^2 inputs. numpy, single process.
Notation: s3 = state after R3.M; L3,L4,L5 = lane 0 after R3,R4,R5 (R4,R5 partial). Run: python j2_toy.py q seed [control]"""
import sys, random, math
import numpy as np
def egcd_inv(a,q): return pow(int(a),-1,q)
class Toy:
    def __init__(self,q,seed):
        self.q=q; rnd=random.Random(seed*1000003+q); self.cap=pow(2,65,q)
        while True:
            xs=rnd.sample(range(q),3); ys=rnd.sample(range(q),3)
            if all((x+y)%q for x in xs for y in ys): break
        self.M=[[pow(x+y,-1,q) for y in ys] for x in xs]
        self.RC=[[rnd.randrange(q) for _ in range(3)] for _ in range(64)]
    def rnd(self,s,idx,full):
        q,M,RC=self.q,self.M,self.RC
        s=[(s[i]+RC[idx][i])%q for i in range(3)]
        for i in (range(3) if full else range(1)):
            x=s[i]; x2=x*x%q; s[i]=x2*x2%q*x%q
        return [(M[i][0]*s[0]+M[i][1]*s[1]+M[i][2]*s[2])%q for i in range(3)]
    def det_trail(self):
        M,q=self.M,self.q
        e0=[1,0,0]
        v1=[M[0][j] for j in range(3)]               # e0 M (row 0)
        v2=[sum(v1[k]*M[k][j] for k in range(3))%q for j in range(3)]
        m=[e0,v1,v2]
        d=(m[0][0]*(m[1][1]*m[2][2]-m[1][2]*m[2][1])-m[0][1]*(m[1][0]*m[2][2]-m[1][2]*m[2][0])+m[0][2]*(m[1][0]*m[2][1]-m[1][1]*m[2][0]))%q
        return d
def stats_fibres(cnt,q):
    return dict(mean=cnt.mean(),var_over_q=cnt.var()/q,mn=int(cnt.min()),mx=int(cnt.max()),empty=int((cnt==0).sum()))
def run(q,seed,log):
    t=Toy(q,seed); N=q*q
    NK=np.repeat(np.arange(q,dtype=np.int64),q); RHO=np.tile(np.arange(q,dtype=np.int64),q)
    s=[NK,RHO,np.full_like(NK,t.cap)]
    for i in range(4): s=t.rnd(s,i,True)
    s3=s; L3=s3[0]
    s4=t.rnd(list(s3),4,False); L4=s4[0]
    s5=t.rnd(list(s4),5,False); L5=s5[0]
    s6=t.rnd(list(s5),6,False); L6=s6[0]
    log('q=%d seed=%d det[e0;e0M;e0M^2]=%d (0 => trail for r=3)'%(q,seed,t.det_trail()))
    # 1 level-curve sizes
    c3=np.bincount(L3,minlength=q); st=stats_fibres(c3,q)
    log(' [1] |{L3=c}| over c: mean %.2f var/q %.3f min %d max %d empty %d   (random function of q^2 inputs into q cells: var/q ~ 1)'%(st['mean'],st['var_over_q'],st['mn'],st['mx'],st['empty']))
    c4=np.bincount(L4,minlength=q); log('     same for L4: var/q %.3f min %d max %d'%(c4.var()/q,c4.min(),c4.max()))
    # Hasse-Weil style: deviation |N_c - q| max vs 2g sqrt q
    log('     max |N_c-q| = %d  (sqrt q=%.1f ; ratio %.2f)'%(np.abs(c3-q).max(),q**.5,np.abs(c3-q).max()/q**.5))
    # R3-equal ordered pairs
    pairs3=int((c3*(c3-1)).sum())//2; log('     R3-equal unordered pairs %d (random N(N-1)/2/q=%.0f)'%(pairs3,N*(N-1)/2/q))
    # 2 groups by (L3,L4): trail pairs. (L3,L4,L5) etc
    def groups(*Ls):
        key=np.zeros(N,dtype=np.int64)
        for L in Ls: key=key*q+L
        _,cnt=np.unique(key,return_counts=True); return cnt
    for name,Ls in (('R3&R4',(L3,L4)),('R3&R4&R5',(L3,L4,L5)),('R3&R4&R5&R6',(L3,L4,L5,L6)),('R4 alone',(L4,)),('R4&R5 (no R3)',(L4,L5)),('R5 alone',(L5,))):
        g=groups(*Ls); pr=int((g*(g-1)//2).sum()); ncell=q**len(Ls)
        exp=N*(N-1)/2/ncell if len(Ls)<=3 else N*(N-1)/2/ncell
        log(' [2] pairs equal at %-14s: %9d  random expectation %.1f  ratio %.3f'%(name,pr,exp,pr/exp if exp else float('nan')))
    g=groups(L3,L4)
    # per-point number of trail partners: group size-1
    per=np.repeat(g-1,g); h=np.bincount(per); lam=1.0
    log('     trail-partner count per input (R3&R4 group size-1): hist %s ; mean %.3f var %.3f (Poisson mean~%.2f var same)'%(h[:8].tolist(),per.mean(),per.var(),(N-1)/q/q*1.0*q/q))
    # 3 balance on surface: within each L3 fibre, L4/L5 distinct-count and collision count vs random control
    rng=np.random.default_rng(seed)
    order=np.argsort(L3,kind='stable'); L3s=L3[order]
    bounds=np.searchsorted(L3s,np.arange(q+1))
    def fibre_stats(Lx):
        d=0;col=0
        for c in range(q):
            v=Lx[order[bounds[c]:bounds[c+1]]]; n=len(v)
            u=len(np.unique(v)); d+=u; col+=n-u
        return d,col
    for name,Lx in (('L4',L4),('L5',L5),('L6',L6)):
        d,col=fibre_stats(Lx)
        # random control: random values from F_q per input, same fibre shape (50 repetitions)
        ds=[]
        for _ in range(20): ds.append(fibre_stats(rng.integers(0,q,N))[0])
        log(' [3] on R3 surface, %s: sum of distinct values per fibre = %d ; random control mean %.1f sd %.1f  (z=%.2f)'%(name,d,np.mean(ds),np.std(ds),(d-np.mean(ds))/max(np.std(ds),1e-9)))
    # distribution of L4 pooled values at fixed value c... uniformity of L4 given L3=c0 for a few c0 (chi2 over q cells with N_c~q samples)
    zs=[]
    for c in range(q):
        v=L4[order[bounds[c]:bounds[c+1]]]
        zs.append(len(v)-len(np.unique(v)))
    # 4 control: free (s1,s2) at fixed s0
    q_=q; ok=True
    for s0 in (0,1,5%q):
        S1=np.repeat(np.arange(q,dtype=np.int64),q); S2=np.tile(np.arange(q,dtype=np.int64),q)
        a=t.rnd([np.full_like(S1,s0),S1,S2],4,False)[0]; b=t.rnd(t.rnd([np.full_like(S1,s0),S1,S2],4,False),5,False)[0]
        ok&=bool((np.bincount(a,minlength=q)==q).all() and (np.bincount(b,minlength=q)==q).all())
        c3_=t.rnd(t.rnd(t.rnd([np.full_like(S1,s0),S1,S2],4,False),5,False),6,False)[0]; bal3=bool((np.bincount(c3_,minlength=q)==q).all())
    log(' [4] CONTROL free (s1,s2): L4 and L5 take each value exactly q times for s0 in {0,1,5}: %s ; after 3 partial rounds balanced: %s'%(ok,bal3))
    # 5 full-state image: s3 image is a q^2 surface: lane 1,2 relation? count distinct (L3, s3_1) ... skip
if __name__=='__main__':
    q=int(sys.argv[1]); seeds=[int(x) for x in sys.argv[2:]]
    for sd in seeds: run(q,sd,lambda m:print(m,flush=True))
