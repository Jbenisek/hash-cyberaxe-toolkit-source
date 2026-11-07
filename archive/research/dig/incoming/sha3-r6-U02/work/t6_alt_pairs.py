"""Q4 alternatives: all same-column aligned lane pairs (a,b) carrying one 32-bit z (cancels in theta1), same 'stop' recipe as the leader."""
import sys,json,itertools; sys.path.insert(0,'.')
import numpy as np
import t2_conditions as T2   # prints its tables on import; fine
from t2_conditions import Elim,B1,F,CB
from kk6 import *
cols={0:[0,5,10,15],1:[1,6,11,16],2:[2,7,12],3:[3,8,13],4:[4,9,14]}
rng=np.random.default_rng(3)
def varying(l,j):
    x,y=l%5,l//5; X=y;Y=(2*x+3*y)%5; return X+5*Y,(j+RHO[l])%64
res=[]
for x,ls in cols.items():
    for a,b in itertools.combinations(ls,2):
        info=dict(pair=(a,b))
        vary={}; coll=False
        for j in range(32):
            for l in (a,b):
                Bi,p=varying(l,j); 
                row=(Bi//5,p)
                if row in vary: coll=True
                vary[row]=(Bi,p,j,l)
        if coll: info.update(feasible=False,why="two varying inputs share a chi1 row"); res.append(info); continue
        need={}
        for (Y,p),(Bi,pp,j,l) in vary.items():
            X=Bi%5
            for nb,val in ((((X+1)%5)+5*Y,0),(((X+4)%5)+5*Y,1)): need[(nb,p)]=val
        # neighbor must not itself be a varying input
        varset={(Bi,p) for (Bi,p,j,l) in vary.values()}
        if any(k in varset for k in need): info.update(feasible=False,why="neighbor is varying"); res.append(info); continue
        # z-invariance of each neighbor form
        inv_ok=True
        for (nb,p),val in need.items():
            f_=B1[nb][p]
            for j in range(32):
                if ((f_>>(64*a+j))&1)^((f_>>(64*b+j))&1): inv_ok=False
        if not inv_ok: info.update(feasible=False,why="neighbor form not invariant under z"); res.append(info); continue
        e=Elim(); st=[e.add(B1[nb][p]^(val<<CB)) for (nb,p),val in need.items()]
        if 'INCONSISTENT' in st: info.update(feasible=False,why="conditions inconsistent with padding/capacity"); res.append(info); continue
        # footprint on random A2 base
        N=256
        A1=rng.integers(0,2**64,size=(25,N),dtype=np.uint64)
        A2=theta(A1); 
        def O2P(S):
            Bc=chi(rhopi(S)); Bc[0]^=M64(RC[1]); return theta(Bc)
        O0=O2P(A2)
        a2w=set();rows=[];o2p=[]
        for j in range(32):
            d=np.zeros((25,N),np.uint64)
            for l in (a,b):
                Bi,p=varying(l,j); d[Bi][:]^=np.uint64(1<<p)   # chi1 output flips at same position X
            dA2=theta(d)
            for lane in range(25):
                for bit in range(64):
                    if (dA2[lane,0]>>np.uint64(bit))&np.uint64(1): a2w.add((j,lane,bit))
            din=rhopi(dA2); 
            rows.append(sum(1 for Y in range(5) for p in range(64) if any((din[X+5*Y,0]>>np.uint64(p))&np.uint64(1) for X in range(5))))
            dO=O2P(A2^dA2)^O0
            o2p.append(sum(int(((dO[lane]>>np.uint64(bit))&np.uint64(1)).any()) for lane in range(25) for bit in range(64)))
        info.update(feasible=True,needed_neighbor_bits=len(need),cond_rank=e.rank(),a2_words_per_j=len([w for w in a2w if w[0]==0]),rows_per_j=int(np.mean(rows)),o2p_words_per_j_mean=float(np.mean(o2p)),o2p_min=min(o2p),o2p_max=max(o2p))
        res.append(info)
for r in res: print(r)
json.dump(res,open('t6_alt_pairs_out.json','w'),indent=1)
