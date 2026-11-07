"""Q4 theta cell: theta2 column-parity kernel membership of the z-space chi1-output differences, for the leader pair and all 21 aligned pairs."""
import sys,json,itertools; sys.path.insert(0,'.')
import numpy as np
from kk6 import *
cols={0:[0,5,10,15],1:[1,6,11,16],2:[2,7,12],3:[3,8,13],4:[4,9,14]}
rng=np.random.default_rng(13)
def varying(l,j):
    x,y=l%5,l//5; X=y;Y=(2*x+3*y)%5; return X+5*Y,(j+RHO[l])%64
def nullspace(vecs):
    """vecs[j] = int; return basis of {u: XOR_j u_j vecs[j]=0} as list of ints over j"""
    rows=[(v,1<<j) for j,v in enumerate(vecs)]; ker=[]; piv={}
    for v,m in rows:
        while v:
            p=v.bit_length()-1
            if p in piv: pv,pm=piv[p]; v^=pv; m^=pm
            else: piv[p]=(v,m); break
        if v==0: ker.append(m)
    return ker
def O2P(S):
    Bc=chi(rhopi(S)); Bc[0]^=M64(RC[1]); return theta(Bc)
out=[]
for x,ls in cols.items():
    for a,b in itertools.combinations(ls,2):
        # parity vectors (column x, plane) of A1 diff per z bit
        par=[]
        for j in range(32):
            v=0
            for l in (a,b):
                Bi,p=varying(l,j); X=Bi%5; v^=1<<(X*64+p)
            par.append(v)
        ker=nullspace(par)
        info=dict(pair=(a,b),kernel_dim=len(ker))
        if ker:
            # lowest-weight basis vector footprint
            ker.sort(key=lambda m:bin(m).count('1'))
            N=256; A1=rng.integers(0,2**64,size=(25,N),dtype=np.uint64); A2=theta(A1); O0=O2P(A2)
            fp=[]
            for m in ker:
                d=np.zeros((25,N),np.uint64)
                for j in range(32):
                    if (m>>j)&1:
                        for l in (a,b):
                            Bi,p=varying(l,j); d[Bi]^=np.uint64(1<<p)
                assert (theta(d)==d).all()   # in the theta kernel
                dO=O2P(A2^d)^O0
                fp.append((bin(m).count('1')*2,sum(int(((dO[ll]>>np.uint64(bb))&np.uint64(1)).any()) for ll in range(25) for bb in range(64))))
            info['kernel_dirs_(A2_words,O2P_words)_lowest5']=fp[:5]; info['kernel_dirs_count']=len(fp)
        out.append(info); print(info)
json.dump(out,open('t7_theta_kernel_out.json','w'),indent=1)
