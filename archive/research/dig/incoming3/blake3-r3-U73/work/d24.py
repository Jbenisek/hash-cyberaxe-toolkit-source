# DOOR.d24 D1 at 3 rounds: (A) bijection check E1/E3 inputs (r2 script rerun with rounds=3, cross-checked at 3 rounds)
# (B) build the legal 55/63 length-cancel pair and count digest words that agree for every sample at r=1,2,3 (r2 = known answer: 4 pins)
import numpy as np
from common import *
from b3own import *
def rol(x,n): return ror(x,32-n)
rng=np.random.default_rng(2424)
def R(n): return rng.integers(0,2**32,n,dtype=np.uint64).astype(U)
ROUNDS=3
print('=== A. bijection check at rounds =',ROUNDS)
N=1<<22
for step in range(3):
    m0=[int(R(1)[0]) for _ in range(16)]; q0=int(R(1)[0]); blen=(55,63,64)[step]; fl=(11,3,11)[step]
    cv=list(IV)
    a1=U(cv[0])+U(cv[4])+U(m0[0]); d1=ror(U(q0)^a1,16); c1=U(IV[0])+d1; b1=ror(U(cv[4])^c1,12)
    a2=a1+b1+U(m0[1])
    w0=R(N); a1n=U(cv[0])+U(cv[4])+w0
    q=rol(d1,16)^a1n; w1=a2-a1n-b1
    m=[w0,w1]+[U(x) for x in m0[2:]]
    snap={}
    def hook(r,k,v,mm):
        if r==0 and k==8: snap['X']=[x.copy() for x in v]
        if r==1 and k==4: snap['Y']=[x.copy() for x in v]; snap['Mp']=[x.copy() for x in mm]
        if r==1 and k==2: snap['C2in']=[v[6].copy(),v[10].copy()]
        if r==2 and k==0: snap['Z']=[x.copy() for x in v]
    v,dg=compress(cv,m,q,blen,fl,ROUNDS,hook)
    for i in range(20):
        ref=vb._compress(cv,[int(x[i]) if np.size(x)>1 else int(x) for x in m],int(q[i]),blen,fl,ROUNDS)[:8]
        assert tuple(int(x[i]) for x in dg)==ref
    X=snap['X']; Xvar=[i for i in range(16) if len(np.unique(X[i]))>1]
    Y=snap['Y']; Mp=snap['Mp']
    E1in={'Y1':Y[1],'Y6':Y[6],'Y11':Y[11],'Y12':Y[12],'wx':Mp[10],'wy':Mp[11]}
    E3in={'Y3':Y[3],'Y4':Y[4],'Y9':Y[9],'Y14':Y[14],'wx':Mp[14],'wy':Mp[15]}
    var1=[k for k,x in E1in.items() if len(np.unique(x))>1]; var3=[k for k,x in E3in.items() if len(np.unique(x))>1]
    nY6=len(np.unique(Y[6])); nY14=len(np.unique(Y[14]))
    pairs=len(np.unique(Y[6].astype(np.uint64)<<np.uint64(32)|Y[14].astype(np.uint64)))
    nw0=len(np.unique(w0))
    xa,xb,xc,xd=X[2][0],X[6][0],X[10][0],X[14][0]; x7=Mp[4][0]
    A1=xa+xb+x7; D1=ror(xd^A1,16); C1=xc+D1; B1=ror(xb^C1,12)
    link=bool(((ror(B1^(C1+Y[14]),7))==Y[6]).all())
    # round-2 state entering the third round: how many words vary with w0
    Zvar=[i for i in range(16) if len(np.unique(snap['Z'][i]))>1]
    print(f'step {step} (b={blen} f={fl}): distinct w0={nw0}; X words varying: {Xvar}; E1 inputs varying {var1}; E3 inputs varying {var3}')
    print(f'  distinct Y6={nY6} Y14={nY14} (Y6,Y14) pairs={pairs} product={nY6*nY14}; bijection: {nY6==nY14==pairs==nw0}; closed form link on all points: {link}; round-2-entry words varying: {len(Zvar)} of 16')
print('=== B. legal 55/63 pair (b 55,f 3) vs (b 63,f 11); message words m4..m7 re-signed so round 0 state is identical')
def pair(n,rounds,fA=3,fB=11,bA=55,bB=63,cvv=None):
    cv=list(IV) if cvv is None else cvv
    mA=[R(n) for _ in range(16)]; mB=[x.copy() for x in mA]
    # K2=(2,6,10,14): a1=cv2+cv6+m4 ; dA=bA , dB=bB ; need a1B = a1A ^ (bA^bB)
    a=U(cv[2])+U(cv[6]); a1A=a+mA[4]; a1B=a1A^U(bA^bB); mB[4]=a1B-a; mB[5]=mA[5]-(a1B-a1A)
    a=U(cv[3])+U(cv[7]); a1A=a+mA[6]; a1B=a1A^U(fA^fB); mB[6]=a1B-a; mB[7]=mA[7]-(a1B-a1A)
    out={}
    def hk(tag):
        def h(r,k,v,mm):
            if r==0 and k==8: out[tag]=[x.copy() for x in v]
        return h
    vA,dA=compress(cv,mA,0,bA,fA,rounds,hk('A')); vB,dB=compress(cv,mB,0,bB,fB,rounds,hk('B'))
    return mA,mB,dA,dB,out
for rounds in (1,2,3):
    mA,mB,dA,dB,out=pair(1<<18,rounds)
    X0=all((out['A'][i]==out['B'][i]).all() for i in range(16))
    eq=[float((dA[i]==dB[i]).mean()) for i in range(8)]
    pinned=[i for i in range(8) if eq[i]==1.0]
    # also bit-level: bits of digest xor difference that are always zero
    allz=0
    for i in range(8):
        x=np.bitwise_or.reduce(dA[i]^dB[i]); allz+=32-bin(int(x)).count('1')
    print(f'rounds={rounds}: round-0 state identical in all 16 words: {X0}; digest words equal in 100% of {1<<18} pairs: {pinned} (count {len(pinned)}); per-word equal fraction {["%.4f"%e for e in eq]}; digest bits never differing: {allz} of 256')
# organizer cross-check of the pair at 3 rounds on 20 points
mA,mB,dA,dB,out=pair(20,3)
for i in range(20):
    assert tuple(int(x[i]) for x in dA)==vb._compress(list(IV),[int(x[i]) for x in mA],0,55,3,3)[:8]
    assert tuple(int(x[i]) for x in dB)==vb._compress(list(IV),[int(x[i]) for x in mB],0,63,11,3)[:8]
print('pair cross-check vs verifier _compress at 3 rounds: 20/20')
