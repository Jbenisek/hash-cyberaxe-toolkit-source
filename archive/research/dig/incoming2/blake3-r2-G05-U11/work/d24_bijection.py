# door 24 RELABEL test: own bijection check on E1/E3 inputs over a sampled outer step (free inner word w0, counter q and w1 solved so round 0 is untouched)

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

import numpy as np
from b3own import *
import importlib.util
spec=importlib.util.spec_from_file_location('vb3',_hca_public_path_text('__HCA_WORKSPACE__/hash-smash/verifier/blake3.py')); vb=importlib.util.module_from_spec(spec); spec.loader.exec_module(vb)
def rol(x,n): return ror(x,32-n)
rng=np.random.default_rng(2424)
def R(n): return rng.integers(0,2**32,n,dtype=np.uint64).astype(U)
N=1<<22
for step in range(3):
    m0=[int(R(1)[0]) for _ in range(16)]; q0=int(R(1)[0]); blen=(55,63,64)[step]; fl=(11,3,11)[step]
    cv=list(IV)
    # reference K0 values at base point
    a1=U(IV[0])+U(IV[4])+U(m0[0]); d1=ror(U(q0)^a1,16); c1=U(IV[0+0]) if False else U(IV[0])  # placeholder removed below
    # K0 = G(0,4,8,12): a=v0=cv0, b=v4=cv4, c=v8=IV0, d=v12=q
    a1=U(cv[0])+U(cv[4])+U(m0[0]); d1=ror(U(q0)^a1,16); c1=U(IV[0])+d1; b1=ror(U(cv[4])^c1,12)
    a2=a1+b1+U(m0[1])
    w0=R(N); a1n=U(cv[0])+U(cv[4])+w0
    q=rol(d1,16)^a1n                       # counter solved so K0.d1 stays fixed
    w1=a2-a1n-b1                           # w1 solved so K0.a2 stays fixed
    m=[w0,w1]+[U(x) for x in m0[2:]]
    snap={}
    def hook(r,k,v,mm):
        if r==0 and k==8: snap['X']=[x.copy() for x in v]
        if r==1 and k==4: snap['Y']=[x.copy() for x in v]; snap['Mp']=[x.copy() for x in mm]
        if r==1 and k==2: snap['C2in']=[v[6].copy(),v[10].copy()]
    v,dg=compress(cv,m,q,blen,fl,2,hook)
    # organizer cross-check on 20 points
    for i in range(20):
        ref=vb._compress(cv,[int(x[i]) if np.size(x)>1 else int(x) for x in m],int(q[i]),blen,fl,2)[:8]
        assert tuple(int(x[i]) for x in dg)==ref
    X=snap['X']; Xvar=[i for i in range(16) if len(np.unique(X[i]))>1]
    Y=snap['Y']; Mp=snap['Mp']
    # message words read by E1 (Mp[10],Mp[11]) and E3 (Mp[14],Mp[15]) after round-1 permutation
    E1in={'Y1':Y[1],'Y6':Y[6],'Y11':Y[11],'Y12':Y[12],'wx':Mp[10],'wy':Mp[11]}
    E3in={'Y3':Y[3],'Y4':Y[4],'Y9':Y[9],'Y14':Y[14],'wx':Mp[14],'wy':Mp[15]}
    var1=[k for k,x in E1in.items() if len(np.unique(x))>1]; var3=[k for k,x in E3in.items() if len(np.unique(x))>1]
    nY6=len(np.unique(Y[6])); nY14=len(np.unique(Y[14]))
    pairs=len(np.unique(Y[6].astype(np.uint64)<<np.uint64(32)|Y[14].astype(np.uint64)))
    nw0=len(np.unique(w0))
    # closed form link Y6 = ror7(C2.b1 xor (C2.c1 + Y14)); C2.b1,c1 are state after C2 first half: recompute from X
    c2b1=snap['C2in'][0][0]  # v6 before C2 (=X6) constant: recompute first half generically below
    # recompute C2 first half with own code from X6,X2,X10,X14 and message m7 (x) -> constant for fixed outer step
    xa,xb,xc,xd=X[2][0],X[6][0],X[10][0],X[14][0]; x7=Mp[4][0]; 
    A1=xa+xb+x7; D1=ror(xd^A1,16); C1=xc+D1; B1=ror(xb^C1,12)
    link=bool(((ror(B1^(C1+Y[14]),7))==Y[6]).all())
    print(f'outer step {step}: N={N} w0 samples, distinct w0={nw0}; X words varying with w0: {Xvar}')
    print(f'  E1 inputs varying: {var1}; E3 inputs varying: {var3}')
    print(f'  distinct Y6={nY6} distinct Y14={nY14} distinct (Y6,Y14) pairs={pairs}  (product would be {nY6*nY14}); graph is a bijection: {nY6==nY14==pairs==nw0}')
    print(f'  closed-form link Y6 = ROR7(C2.b1 ^ (C2.c1+Y14)) holds on all {N}: {link}')
    print(f'  counter q varies (distinct q = {len(np.unique(q))}); with q fixed (root) w0 would be pinned')
# exhaustive-in-slice permutation proof of Y14 map: Y14 = ror(D1 ^ (A1'+...)) composition, check 2^24 consecutive w0 are distinct
print('done')
