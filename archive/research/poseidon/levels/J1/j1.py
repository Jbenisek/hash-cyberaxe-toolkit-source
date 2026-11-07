"""J1: R60-R62 card (toy exhaustive). usage: python j1.py q seed r   (single process, numpy)
Parts: V validation, Z zero loci, C rank-1 census by source, W difference-weight transitions."""

# Publication path adapter: resolve data paths from the extracted source tree.
def _hca_public_path_text(value):
    if "__HCA_WORKSPACE__/" not in value:
        return value
    import os as _hca_os
    from pathlib import Path as _hca_Path
    root = _hca_os.environ.get("HASHCYBERAXE_WORKSPACE")
    if root is None:
        here = _hca_Path(__file__).resolve().parent
        root = next((str(p) for p in (here, *here.parents) if (p / "research").is_dir()), None)
    if root is None:
        raise FileNotFoundError("Extract the research source tree, or set HASHCYBERAXE_WORKSPACE to its archive directory.")
    return value.replace("__HCA_WORKSPACE__/", str(_hca_Path(root).resolve()).replace("\\", "/") + "/")

import sys, random
import numpy as np
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/levels/U9'))
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/orchard/impl'))
from u9_toylib import toy_params
def sched(r): return list(range(0,4))+list(range(4,4+r))+list(range(60,64))
def full(i): return i<4 or i>=60
def gperm(s, M, RC, mod, r):          # generic scalar reference (same algorithm, any modulus)
    s=list(s)
    for idx in sched(r):
        s=[(s[i]+RC[idx][i])%mod for i in range(3)]
        for i in (range(3) if full(idx) else range(1)): s[i]=pow(s[i],5,mod)
        s=[sum(M[i][j]*s[j] for j in range(3))%mod for i in range(3)]
    return s
def validate_real():
    import poseidon_ref as pr
    rnd=random.Random(5)
    for r in (1,2,5):
        for _ in range(3):
            a,b=rnd.randrange(pr.P),rnd.randrange(pr.P)
            assert gperm([a,b,pr.CAPACITY],pr.MDS,pr.RC,pr.P,r)[0]==pr.hash_reduced(a,b,r)
    return 'generic scalar perm == poseidon_ref.hash_reduced (r=1,2,5, 3 random inputs each)'
q,seed,r=int(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3])
print('q=%d seed=%d r=%d'%(q,seed,r))
if q==257 and seed==1 and r==1: print('V:',validate_real())
M,RC,cap=toy_params(q,seed)
rr=random.Random(7)
A,B=np.meshgrid(np.arange(q,dtype=np.int64),np.arange(q,dtype=np.int64),indexing='ij'); A=A.ravel(); B=B.ravel(); n=A.size
# start: the plane after R0 in (A,B)=(nk^5,rho^5): lanes M*(A,B,K)
K=pow((cap+RC[0][2])%q,5,q)
s=[(M[i][0]*A+M[i][1]*B+M[i][2]*K)%q for i in range(3)]
# validate numpy chain against scalar generic perm on random (nk,rho) (A,B)=(nk^5,rho^5)
def check_chain():
    for _ in range(5):
        nk,rho=rr.randrange(q),rr.randrange(q)
        ref=gperm([nk,rho,cap],M,RC,q,r)
        a,b=pow(nk+RC[0][0],5,q),pow(rho+RC[0][1],5,q)
        t=[(M[i][0]*a+M[i][1]*b+M[i][2]*K)%q for i in range(3)]
        for idx in sched(r)[1:]:
            t=[(t[i]+RC[idx][i])%q for i in range(3)]
            for i in (range(3) if full(idx) else range(1)): t[i]=pow(t[i],5,q)
            t=[sum(M[i][j]*t[j] for j in range(3))%q for i in range(3)]
        assert t==ref
check_chain(); print('V: toy (A,B)-chain == generic scalar perm on 5 random inputs')
J=[[np.full(n,M[i][0],dtype=np.int64),np.full(n,M[i][1],dtype=np.int64)] for i in range(3)]
def low_rank(J):
    m=[(J[a][0]*J[b][1]-J[a][1]*J[b][0])%q for a,b in ((0,1),(0,2),(1,2))]
    return (m[0]==0)&(m[1]==0)&(m[2]==0)
prev=None; states={}
print('rows: round | zero-count lane0,1,2 (mean over lanes/q) | pair-zero pts 01,02,12 | triple | rank<=1 total | NEW: dbl-zero / single-zero / no-zero | inherited')
for idx in sched(r)[1:]:
    s=[(s[i]+RC[idx][i])%q for i in range(3)]
    z=[(s[i]==0) for i in range(3)]
    zc=[int(x.sum()) for x in z]
    pz=[int((z[a]&z[b]).sum()) for a,b in ((0,1),(0,2),(1,2))]
    tz=int((z[0]&z[1]&z[2]).sum())
    S=[];d=[]
    for i in range(3):
        if full(idx) or i==0:
            s2=s[i]*s[i]%q; s4=s2*s2%q; S.append(s4*s[i]%q); d.append(5*s4%q)
        else: S.append(s[i]); d.append(np.ones(n,dtype=np.int64))
    Jd=[[d[i]*J[i][j]%q for j in range(2)] for i in range(3)]
    s=[sum(M[i][l]*S[l] for l in range(3))%q for i in range(3)]
    J=[[sum(M[i][l]*Jd[l][j] for l in range(3))%q for j in range(2)] for i in range(3)]
    low=low_rank(J); zs=sum(x.astype(np.int64) for x in z)
    new=low if prev is None else low&~prev
    inh=0 if prev is None else int((low&prev).sum())
    assert prev is None or bool(np.all(low[prev]))
    nd=int((new&(zs>=2)).sum()); ns=int((new&(zs==1)).sum()); nn=int((new&(zs==0)).sum())
    print('R%-2d %s | zeros %d %d %d (q=%d) | pairs %d %d %d | triple %d | low %d | NEW %d / %d / %d | inh %d'%(idx,'F' if full(idx) else 'P',zc[0],zc[1],zc[2],q,pz[0],pz[1],pz[2],tz,int(low.sum()),nd,ns,nn,inh),flush=True)
    prev=low.copy()
    if idx==(4+r-1): states['pre']=[x.copy() for x in s]     # state after last partial round = R60 entry
    # weight transition data collected below
# ---- W: difference weights. pairs equal in lane 0 after last partial round (entry to R60), plus control random pairs
s0=states['pre']
def trans(sa,sb,tag):
    dd=[(sa[i]-sb[i])%q for i in range(3)]
    out=[]
    w=sum((x!=0).astype(np.int64) for x in dd)
    res={}
    cur=(sa,sb)
    line=[]
    for idx in range(60,64):
        ca=[(cur[0][i]+RC[idx][i])%q for i in range(3)]; cb=[(cur[1][i]+RC[idx][i])%q for i in range(3)]
        def sb5(x): x2=x*x%q; return x2*x2%q*x%q
        Sa=[sb5(x) for x in ca]; Sb=[sb5(x) for x in cb]
        wS=sum(((Sa[i]-Sb[i])%q!=0).astype(np.int64) for i in range(3))   # after S
        wi=sum(((ca[i]-cb[i])%q!=0).astype(np.int64) for i in range(3))   # before S
        Ma=[sum(M[i][j]*Sa[j] for j in range(3))%q for i in range(3)]; Mb=[sum(M[i][j]*Sb[j] for j in range(3))%q for i in range(3)]
        wM=sum(((Ma[i]-Mb[i])%q!=0).astype(np.int64) for i in range(3))
        T=np.zeros((4,4),dtype=np.int64)
        for a in range(4):
            for b in range(4): T[a,b]=int(((wi==a)&(wM==b)).sum())
        line.append((idx,T,int((wS!=wi).sum())))
        cur=(Ma,Mb)
    col=(cur[0][0]==cur[1][0])
    return line,col
# build pairs
rng=np.random.default_rng(seed)
lane0=s0[0]; order=np.argsort(lane0,kind='stable'); sl=lane0[order]
starts=np.searchsorted(sl,np.arange(q+1))
NP=min(4_000_000,int(n*n/2/q)) 
a_idx=rng.integers(0,n,size=NP*2); 
pa=a_idx; g=lane0[pa]; lo=starts[g]; sz=starts[g+1]-lo
ok=sz>1
pa=pa[ok]; g=g[ok]; lo=lo[ok]; sz=sz[ok]
off=rng.integers(0,sz-1)   # pick other member
posA=np.searchsorted(sl,g)  # not used
# choose b as random group member != a: draw k in [0,sz-1), skip a's own position
rankA=np.empty(n,dtype=np.int64); rankA[order]=np.arange(n)
ra=rankA[pa]-lo
kk=rng.integers(0,sz-1); kk=kk+(kk>=ra)
pb=order[lo+kk]
pa=pa[:NP]; pb=pb[:NP]
sa=[x[pa] for x in s0]; sbb=[x[pb] for x in s0]
dw0=sum(((sa[i]-sbb[i])%q!=0).astype(np.int64) for i in range(3))
print('W: pairs equal in lane 0 at R60 entry (r=%d): %d sampled; entry weight histogram w1,w2,w3 = %s'%(r,len(pa),[int((dw0==w).sum()) for w in (0,1,2,3)]))
line,col=trans(sa,sbb,'trail')
for idx,T,ch in line:
    print('  R%d trail pairs: rows=weight before S (0..3), cols=weight after M: %s ; S changed weight in %d'%(idx,T.tolist(),ch))
print('  trail pairs with equal output lane 0 (collisions in sample): %d  (random expectation %.1f)'%(int(col.sum()),len(pa)/q))
# control: random pairs
ia=rng.integers(0,n,size=500000); ib=rng.integers(0,n,size=500000); m=ia!=ib
sa=[x[ia[m]] for x in s0]; sbb=[x[ib[m]] for x in s0]
line,col=trans(sa,sbb,'rand')
for idx,T,ch in line: print('  R%d random pairs: %s'%(idx,T.tolist()))
