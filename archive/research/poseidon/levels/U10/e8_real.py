"""U10 real-target checks (our implementation poseidon_ref.py, constants read as data).
 a) X2/X5/X7 on 2000 real inputs (r=1,2); b) same with a random NON-Cauchy MDS substituted;
 c) zero constants + cap=0: y(lam x)=lam y(x) for lam in mu4 (partial rounds), lam^(5^8) for r=0; real cap breaks it;
 d) S-layer fixed point set size on real p; e) 5th root exponent d Hamming weight."""

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
sys.path.insert(0,_hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/orchard/impl'))
import poseidon_ref as P
p=P.P
rnd=random.Random(3)
def mat_inv(M):
    d=(M[0][0]*(M[1][1]*M[2][2]-M[1][2]*M[2][1])-M[0][1]*(M[1][0]*M[2][2]-M[1][2]*M[2][0])+M[0][2]*(M[1][0]*M[2][1]-M[1][1]*M[2][0]))%p
    di=pow(d,-1,p)
    def mn(i,j):
        r=[a for a in range(3) if a!=i];c=[b for b in range(3) if b!=j]
        return M[r[0]][c[0]]*M[r[1]][c[1]]-M[r[0]][c[1]]*M[r[1]][c[0]]
    return [[((-1)**(i+j))*mn(j,i)*di%p for j in range(3)] for i in range(3)]
def is_mds(M):
    if any(x%p==0 for r in M for x in r): return False
    for i1 in range(3):
        for i2 in range(i1+1,3):
            for j1 in range(3):
                for j2 in range(j1+1,3):
                    if (M[i1][j1]*M[i2][j2]-M[i1][j2]*M[i2][j1])%p==0: return False
    return True
def is_cauchy(M):
    N=[[pow(M[i][j],-1,p) for j in range(3)] for i in range(3)]
    return all((N[i][j]-N[i][0]-N[0][j]+N[0][0])%p==0 for i in range(3) for j in range(3))
def make_run(MDS,RC,cap):
    def rnd_(s,idx,full):
        s=[(s[i]+RC[idx][i])%p for i in range(3)]
        for i in (range(3) if full else range(1)): s[i]=pow(s[i],5,p)
        return [sum(MDS[i][j]*s[j] for j in range(3))%p for i in range(3)]
    def run(nk,rho,r,upto=None):
        s=[nk,rho,cap]
        for n,idx in enumerate(P.schedule(r)):
            if upto is not None and n>=upto: break
            s=rnd_(s,idx,idx<4 or idx>=60)
        return s
    return run,rnd_
def checks(MDS,label,N=2000):
    run,rd=make_run(MDS,P.RC,P.CAPACITY)
    Mi=mat_inv(MDS); K=pow(P.CAPACITY+P.RC[0][2],5,p)
    for r in (1,2):
        ok2=ok5=ok7=0
        for _ in range(N):
            nk,rho=rnd.randrange(p),rnd.randrange(p)
            s0=run(nk,rho,r,upto=1)
            ok2+= sum(Mi[2][j]*s0[j] for j in range(3))%p==K
            s3=run(nk,rho,r,upto=4)
            w=pow((s3[0]+P.RC[4][0])%p,5,p)
            v=[w,(s3[1]+P.RC[4][1])%p,(s3[2]+P.RC[4][2])%p]
            ok5+= [sum(MDS[i][j]*v[j] for j in range(3))%p for i in range(3)]==run(nk,rho,r,upto=5)
            sB=run(nk,rho,r,upto=len(P.schedule(r))-1)
            T=[pow((sB[i]+P.RC[63][i])%p,5,p) for i in range(3)]
            ok7+= sum(MDS[0][j]*T[j] for j in range(3))%p==run(nk,rho,r)[0]
        print(f"{label} r={r}: X2 {ok2}/{N} X5 {ok5}/{N} X7 {ok7}/{N}",flush=True)
print("real MDS is_mds",is_mds(P.MDS),"is_cauchy",is_cauchy(P.MDS))
# reference sanity: our generic run equals poseidon_ref
run,_=make_run(P.MDS,P.RC,P.CAPACITY)
print("generic runner == poseidon_ref on 50 inputs:",all(run(a,b,r)[0]==P.hash_reduced(a,b,r) for a,b in [(rnd.randrange(p),rnd.randrange(p)) for _ in range(25)] for r in (1,2)))
checks(P.MDS,"REAL Cauchy MDS")
while True:
    M2=[[rnd.randrange(p) for _ in range(3)] for _ in range(3)]
    if is_mds(M2) and not is_cauchy(M2): break
print("random MDS is_mds",is_mds(M2),"is_cauchy",is_cauchy(M2))
checks(M2,"NON-Cauchy random MDS on real p")
# X6 trail vector with non-Cauchy: lane0 stays equal over two partial rounds
for lab,MD in (("real",P.MDS),("noncauchy",M2)):
    d=(0,MD[0][2],(-MD[0][1])%p); ok=0
    for _ in range(300):
        s=[rnd.randrange(p) for _ in range(3)]; s2=[(s[i]+d[i])%p for i in range(3)]
        def pr(s,idx):
            s=[(s[i]+P.RC[idx][i])%p for i in range(3)]; s[0]=pow(s[0],5,p)
            return [sum(MD[i][j]*s[j] for j in range(3))%p for i in range(3)]
        a=pr(pr(s,4),5); b=pr(pr(s2,4),5)
        ok+= a[0]==b[0]
    print(f"X6 trail vector {lab}: lane0 equal after R4,R5 in {ok}/300 random states (and states differ: {a!=b})")
# c) symmetry
i4=pow(2,(p-1)//4,p)
for t in range(2,50):
    if pow(t,(p-1)//4,p)**2%p==p-1: i4=pow(t,(p-1)//4,p);break
print("i^2 == -1:",i4*i4%p==p-1)
Z=[[0,0,0]]*64
for cap,lab in ((0,"cap=0"),(P.CAPACITY,"cap=2^65")):
  for RCn,cl in ((Z,"zero consts"),(P.RC,"real consts")):
    runz,_=make_run(P.MDS,RCn,cap)
    for r in (0,1,2):
        ok=0
        for _ in range(40):
            nk,rho=rnd.randrange(p),rnd.randrange(p)
            ok+= runz(i4*nk%p,i4*rho%p,r)[0]==i4*runz(nk,rho,r)[0]%p
        lam=rnd.randrange(2,p)
        e=pow(5,8,p-1); okf=0
        for _ in range(20):
            nk,rho=rnd.randrange(p),rnd.randrange(p)
            okf+= runz(lam*nk%p,lam*rho%p,r)[0]==pow(lam,e,p)*runz(nk,rho,r)[0]%p
        print(f"{cl}, {lab}, r={r}: y(i x)=i y(x) in {ok}/40 ; y(lam x)=lam^(5^8) y(x) (arbitrary lam) in {okf}/20")
# d) fixed points: x^5=x count via polynomial x^4=1: roots count
roots=[x for x in (0,1,p-1,i4,p-i4) if pow(x,5,p)==x]
print("x^5=x solutions found in {0,1,-1,i,-i}:",len(roots),"=> S-layer fixed triples 125 (x^4-1 has exactly 4 roots since 4 | p-1)")
d=pow(5,-1,p-1); print("5th root exponent d bits",d.bit_length(),"popcount",bin(d).count('1'),"hex",hex(d))
