
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

import sys, random, time
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/orchard/impl'))
import poseidon_ref as R
P = R.P
def inv(x, p=P): return pow(x, p-2, p)
class Sys:
    def __init__(s, p, M, RC):
        s.p=p; s.M=M; s.RC=RC; s.d=pow(5, -1, p-1)
        s.Mi=s.minv(M)
    def minv(s, M):
        p=s.p
        a,b,c=M[0];d,e,f=M[1];g,h,i=M[2]
        det=(a*(e*i-f*h)-b*(d*i-f*g)+c*(d*h-e*g))%p
        di=pow(det,-1,p)
        adj=[[e*i-f*h, c*h-b*i, b*f-c*e],[f*g-d*i, a*i-c*g, c*d-a*f],[d*h-e*g, b*g-a*h, a*e-b*d]]
        return [[adj[r][k]*di%p for k in range(3)] for r in range(3)]
    def mul(s, v, M=None):
        M=M or s.M; p=s.p
        return [sum(M[i][j]*v[j] for j in range(3))%p for i in range(3)]
    def rnd(s, v, idx, full=True):
        p=s.p
        v=[(v[i]+s.RC[idx][i])%p for i in range(3)]
        v=[pow(x,5,p) if (full or i==0) else x for i,x in enumerate(v)]
        return s.mul(v)
    def tail(s, v, idxs=(60,61,62,63)):
        for k in idxs: v=s.rnd(v,k)
        return v
    def back_round(s, v, idx, cnt):  # v = state after full round idx -> state before
        T=s.mul(v, s.Mi); cnt[0]+=3
        t=[pow(x,s.d,s.p) for x in T]
        return [(t[i]-s.RC[idx][i])%s.p for i in range(3)]
real=Sys(P, [list(r) for r in R.MDS], [list(r) for r in R.RC])
rng=random.Random(20261012)
def rv(): return [rng.randrange(P) for _ in range(3)]
out=[]
def log(*a):
    s=' '.join(str(x) for x in a); print(s); out.append(s)
H=lambda x: hex(x)
M0=real.M[0]
log("== Q1 X7: y = sum_j M0j * T_j, T=S(state after R62 + c63), 1000 inputs per r (real hash)")
for r in (1,2):
    bad=0
    for _ in range(1000):
        nk,rho=rng.randrange(P),rng.randrange(P)
        s=[nk,rho,R.CAPACITY]
        for k in R.schedule(r)[:-1]:
            s=R.round_full(s,k) if (k<4 or k>=60) else R.round_partial(s,k)
        t=[(s[i]+R.RC[63][i])%P for i in range(3)]
        T=[pow(x,5,P) for x in t]
        y=sum(M0[j]*T[j] for j in range(3))%P
        if y!=R.hash_reduced(nk,rho,r): bad+=1
    log("r=%d mismatches: %d of 1000"%(r,bad))
log("== Q2 backward map")
mism=0
N=1000
for _ in range(N):
    y=rng.randrange(P); T0=rng.randrange(P); T1=rng.randrange(P)
    T2=(y-M0[0]*T0-M0[1]*T1)*inv(M0[2])%P
    c1=[3]
    t=[pow(x,real.d,P) for x in (T0,T1,T2)]
    s=[(t[i]-R.RC[63][i])%P for i in range(3)]   # state after R62.M
    if real.rnd(s,63)[0]!=y: mism+=1
    s2=s
    for k in (62,61,60): s2=real.back_round(s2,k,c1)
    if real.tail(s2)[0]!=y: mism+=1
    cnt=c1
log("backward: %d trials, forward-mismatch count %d (checked at R62.M level and at R60-entry level)"%(N,mism))
log("5th-root exponentiations: R63 backward = 3 (T0,T1,T2 each need x^d, d=254 bits), each further full round = 3; total R63..R60 = %d (counter)"%cnt[0])
log("derived totals from y back to R0 entry: r=1: 12+1+12=25 ; r=2: 12+2+12=26 (the R0 lane-2 root is not an unknown: that value must equal the constant K, so it is a CONSTRAINT checked, 1 equation)")
log("== Q3 degree of last four rounds at R60 entry, exact line (finite differences)")
def deg_line(f, base, u, N, p=P):
    vals=[f([(base[i]+t*u[i])%p for i in range(3)]) for t in range(N)]
    row=vals; deg=-1
    for k in range(N):
        if any(row): deg=k
        row=[(row[i+1]-row[i])%p for i in range(len(row)-1)]
        if not row: break
    return deg
fy=lambda st: real.tail(st)[0]
for trial in range(2):
    b,u=rv(),rv()
    log("generic line", trial, "deg of y(R60 entry + t u) =", deg_line(fy,b,u,640))
for k,name,pred in ((60,'after R60.M',5),(61,'after R61.M',25),(62,'after R62.M',125)):
    b,u=rv(),rv()
    f=lambda st,k=k: (lambda v:(v[0]+3*v[1]+7*v[2])%P)(real.tail(st,tuple(range(60,k+1))))
    log("lane-combination",name,"deg:",deg_line(f,b,u,200),"(predicted %d)"%pred)
def G(u):
    for _ in range(4): u=real.mul([pow(x,5,P) for x in u])
    return u
u=rv(); log("G (constant-free 4 rounds) homogeneous of degree 625:", G([3*x%P for x in u])[0]==pow(3,625,P)*G(u)[0]%P)
w=[0,rng.randrange(P),rng.randrange(P)]
ud=w
for _ in range(4):
    v=real.mul(ud,real.Mi); ud=[pow(x,real.d,P) for x in v]
log("constructed direction ud (backward through constant-free rounds from (0,a,b)) has G(ud)_0 == 0 :", G(ud)[0]==0)
b=rv()
log("degree of y on a line with direction ud (predicted <625):", deg_line(fy,b,ud,640))
log("== Q4 special lane values at R63.S")
cands=[x for x in [pow(g,(P-1)//4,P) for g in range(2,30)] if pow(x,2,P)==P-1]
I=cands[0]
fixed=[0,1,P-1,I,P-I]
assert all(pow(x,5,P)==x for x in fixed)
x=rng.randrange(P)
for pair,name in (((0,1),"t0=t1=0"),((0,2),"t0=t2=0"),((1,2),"t1=t2=0")):
    j=3-pair[0]-pair[1]
    t=[0,0,0]; t[j]=x
    st=[(t[i]-R.RC[63][i])%P for i in range(3)]
    yy=real.rnd(st,63)[0]
    log(name,": y == M0%d * t%d^5 :"%(j,j), yy==M0[j]*pow(x,5,P)%P)
ok=0
for combo in range(125):
    t=[fixed[combo%5],fixed[(combo//5)%5],fixed[combo//25]]
    st=[(t[i]-R.RC[63][i])%P for i in range(3)]
    if real.rnd(st,63)[0]==sum(M0[j]*t[j] for j in range(3))%P: ok+=1
log("125 combos of fixed-point t (0,1,-1,i,-i)^3: y equals the LINEAR form M0.t in", ok, "of 125")
for combo in range(125):
    t=[fixed[combo%5],fixed[(combo//5)%5],fixed[combo//25]]
    st=[(t[i]-R.RC[63][i])%P for i in range(3)]
    c=[0]; s2=st
    for k in (62,61,60): s2=real.back_round(s2,k,c)
    assert fy(s2)==sum(M0[j]*t[j] for j in range(3))%P
    if combo==0: first=s2
log("each of the 125 pulled back through R62,R61,R60 (9 roots) to R60 entry and forward-checked: all OK; first (t=(0,0,0)):",[H(v) for v in first])
log("== Q5 top byte")
for r,Nn in ((1,100000),(2,30000)):
    t0=time.time()
    hist=[0]*256; b255=b254=0; mx=0; mn=255
    top6=[0]*64
    for _ in range(Nn):
        y=R.hash_reduced(rng.randrange(P),rng.randrange(P),r)
        by=(y.to_bytes(32,'little'))[31]
        hist[by]+=1; mx=max(mx,by); mn=min(mn,by)
        b255+=(y>>255)&1; b254+=(y>>254)&1; top6[y>>250]+=1
    nz=[i for i in range(256) if hist[i]]
    exp=Nn/64
    chi=sum((c-exp)**2/exp for c in top6)
    log("r=%d N=%d: top byte min %d max %d (0x%02x); bit255 set %d, bit254 set %d, byte==0x40: %d, distinct top bytes %d, top-6-bit(y>>250) chi2(63df)=%.1f, time %.0fs"%(r,Nn,mn,mx,mx,b255,b254,hist[0x40],len(nz),chi,time.time()-t0))
log("p>>248 =", hex(P>>248), " prob(y>=2^254) = %.3e"%((P-2**254)/P), " prob(top byte==0x40)=%.3e"%((P-(0x40<<248))/P))
log("== Q6 R60..R63 identical for r=1 and r=2")
log("schedule r=1 tail", R.schedule(1)[-4:], "r=2 tail", R.schedule(2)[-4:], "equal:", R.schedule(1)[-4:]==R.schedule(2)[-4:])
same=0
for _ in range(1000):
    nk,rho=rng.randrange(P),rng.randrange(P)
    ok2=True
    for r in (1,2):
        s=[nk,rho,R.CAPACITY]
        for k in R.schedule(r)[:-4]:
            s=R.round_full(s,k) if k<4 else R.round_partial(s,k)
        ok2 = ok2 and real.tail(s)[0]==R.hash_reduced(nk,rho,r)
    same+=ok2
log("1000 inputs: hash == one common function Tail(R60..R63) applied to the partial-block output, for both r:", same)
log("hash(5,6) differs between r=1 and r=2:", R.hash_reduced(5,6,1)!=R.hash_reduced(5,6,2))
log("== Q7 dead / constant computations (perturbation + dependence tables)")
def steps(r):
    L=[]
    for k in R.schedule(r):
        full=(k<4 or k>=60)
        L+= [(k,'C',full),(k,'S',full),(k,'M',full)]
    return L
def run(nk,rho,r,hook=None):
    s=[nk,rho,R.CAPACITY]; trace=[]
    for n,(k,st,full) in enumerate(steps(r)):
        if st=='C': s=[(s[i]+R.RC[k][i])%P for i in range(3)]
        elif st=='S': s=[pow(x,5,P) if (full or i==0) else x for i,x in enumerate(s)]
        else: s=real.mul(s)
        if hook: s=hook(n,s)
        trace.append(list(s))
    return s[0],trace
for r in (1,2):
    nk,rho=rng.randrange(P),rng.randrange(P)
    nk2=rng.randrange(P)
    y0,tr=run(nk,rho,r)
    assert y0==R.hash_reduced(nk,rho,r)
    _,tr2=run(nk2,rho,r); _,tr3=run(nk,rng.randrange(P),r)
    S=steps(r); dead=[]; const=[]
    for n,(k,st,full) in enumerate(S):
        for lane in range(3):
            def hook(m,s,n=n,lane=lane):
                if m==n: s=list(s); s[lane]=(s[lane]+1)%P
                return s
            if run(nk,rho,r,hook)[0]==y0: dead.append((k,st,lane))
            if tr[n][lane]==tr2[n][lane] and tr[n][lane]==tr3[n][lane]: const.append((k,st,lane))
    log("r=%d, %d steps x 3 lanes = %d values"%(r,len(S),3*len(S)))
    log("  values whose +1 change does not alter the output (dead):", dead)
    log("  values that do NOT depend on (nk,rho) (constants):", const)
log("== Q8 reverse-mode influence (adjoint) on 100 points, r=1 and r=2")
for r in (1,2):
    S=steps(r); zero_counts={}
    for _ in range(100):
        nk,rho=rng.randrange(P),rng.randrange(P)
        y,tr=run(nk,rho,r)
        g=[1,0,0]; grads=[None]*len(S); grads[-1]=list(g)
        for n in range(len(S)-1,0,-1):
            k,st,full=S[n]
            if st=='M': g=[sum(real.M[i][j]*g[i] for i in range(3))%P for j in range(3)]
            elif st=='S':
                pre=tr[n-1]
                g=[g[i]*5*pow(pre[i],4,P)%P if (full or i==0) else g[i] for i in range(3)]
            grads[n-1]=list(g)
        for n in range(len(S)):
            for lane in range(3):
                if grads[n][lane]==0:
                    key=(S[n][0],S[n][1],lane); zero_counts[key]=zero_counts.get(key,0)+1
    log("r=%d: (round,step,lane) with zero gradient (count of 100 points):"%r, dict(sorted(zero_counts.items())))
nk,rho=rng.randrange(P),rng.randrange(P); y,tr=run(nk,rho,1)
S=steps(1); n62=[i for i,s in enumerate(S) if s[0]==62 and s[1]=='M'][0]
t=[(tr[n62][i]+R.RC[63][i])%P for i in range(3)]
log("closed form grad at R62.M = M0j*5*t_j^4 nonzero for all j:",[M0[j]*5*pow(t[j],4,P)%P!=0 for j in range(3)])
open(_hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/levels/U4/u4_facts_output.txt'),'w').write('\n'.join(out)+'\n')
