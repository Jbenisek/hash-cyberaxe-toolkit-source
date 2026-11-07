import sys,json,itertools,time; sys.path.insert(0,'.')
import numpy as np
from kk6 import *
from t1_q1_chi2 import A2of
t0=time.time()
rng=np.random.default_rng(21)
N=1
L0=leader_state(rng,1); A20=A2of(L0)
# constant chi2 input differences per z coordinate (slice independent)
din=[]
for j in range(32):
    L=L0.copy(); L[4]^=np.uint64(1<<j); L[14]^=np.uint64(1<<j)
    d=rhopi(A2of(L)^A20)[:,0]
    din.append([int(v) for v in d])
def rowmask(d,Y,p): return sum(((d[X+5*Y]>>p)&1)<<X for X in range(5))
ROWS=[{(Y,p):rowmask(d,Y,p) for Y in range(5) for p in range(64) if rowmask(d,Y,p)} for d in din]
def Bform2(i,j):
    r=0
    for (Y,p),ma in ROWS[i].items():
        mb=ROWS[j].get((Y,p),0)
        if mb:
            for k in range(5):
                v=((ma>>((k+1)%5))&1)&((mb>>((k+2)%5))&1) ^ ((ma>>((k+2)%5))&1)&((mb>>((k+1)%5))&1)
                if v: r|=1<<((k+5*Y)*64+p)
    return r
def Bform(a,b):
    """second derivative of chi2 in directions a,b (5x5 lane ints) as 1600-bit int; independent of the state"""
    r=0
    for Y in range(5):
        for p in range(64):
            ma,mb=rowmask(a,Y,p),rowmask(b,Y,p)
            if ma and mb:
                for k in range(5):
                    v=((ma>>((k+1)%5))&1)&((mb>>((k+2)%5))&1) ^ ((ma>>((k+2)%5))&1)&((mb>>((k+1)%5))&1)
                    if v: r|=1<<((k+5*Y)*64+p)
    return r
T=[[0]*32 for _ in range(32)]
for i in range(32):
    for j in range(i+1,32): T[i][j]=T[j][i]=Bform2(i,j)
conf=[(i,j) for i in range(32) for j in range(i+1,32) if T[i][j]]
print("chi2: conflicting z-coordinate pairs:",len(conf),"of 496")
adj=[[0]*32 for _ in range(32)]
for i in range(32):
    for j in range(32):
        if i!=j and not T[i][j]: adj[i][j]=1
# exact max clique (coordinate subsets) via simple Bron-Kerbosch
best=[0,[]]
def bk(R,P,X):
    if not P and not X:
        if len(R)>best[0]: best[0]=len(R);best[1]=list(R)
        return
    for v in list(P):
        bk(R+[v],[u for u in P if adj[v][u]],[u for u in X if adj[v][u]])
        P.remove(v);X.append(v)
bk([],list(range(32)),[])
print("max clique of coordinate z-directions affine through chi2:",best)
def Bvec(u,v):
    r=0
    for i in range(32):
        if (u>>i)&1:
            for j in range(32):
                if (v>>j)&1 and i!=j: r^=T[i][j]
    return r
# general subspaces (not only coordinate): randomized greedy for maximal totally isotropic subspace
bestd=0;bestU=None
def reduce_(v,ech):
    for p,b in ech:
        if (v>>p)&1: v^=b
    return v
t1=time.time(); tries=0
while time.time()-t1<40:
    tries+=1
    basis=[];ech=[];fails=0
    while fails<300 and len(basis)<32:
        w=int(rng.integers(1,8)); v=0
        for b in rng.choice(32,size=w,replace=False): v|=1<<int(b)
        r=reduce_(v,ech)
        if r==0: fails+=1;continue
        if all(Bvec(b,v)==0 for b in basis):
            basis.append(v); ech.append((r.bit_length()-1,r)); ech.sort(key=lambda t:-t[0]); fails=0
        else: fails+=1
    if len(basis)>bestd: bestd=len(basis);bestU=list(basis)
print("random greedy isotropic subspaces (proper elimination): best dim",bestd,"tries",tries)
# verify: all pairs in bestU zero
assert all(Bvec(u,v)==0 for u in bestU for v in bestU)
json.dump(dict(conflict_pairs=len(conf),clique=best,greedy_best_dim=bestd,greedy_basis=bestU),open('t4_chi2_affine_out.json','w'))
print("time",time.time()-t0)
