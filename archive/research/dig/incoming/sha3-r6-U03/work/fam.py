import numpy as np
from kk import *
def rotl1(a): return rotl(a,1)
def make_family(G,rng):
    """G random prefixes satisfying the round-1 prefix conditions (Lemma 1): L8=0, L5=L15=D0, C2=NOT rotl(C4,1). lanes (25,G)"""
    L=rng.integers(0,2**64,(25,G),dtype=np.uint64); L[16:]=0; L[16]=U(0x8000000000000006)
    L[8]=0
    C4=L[4]^L[9]^L[14]
    C1=L[1]^L[6]^L[11]^L[16]
    D0=C4^rotl(C1,1)
    L[5]=D0; L[15]=D0
    L[12]=~rotl(C4,1)^L[2]^L[7]
    return L
def apply_z(L,z):
    A=L.copy(); zz=U(z&0xffffffff); A[4]=A[4]^zz; A[14]=A[14]^zz; return A
def stages(A):
    """returns dict of states: S1 after round1; A2 after theta2; S2 after round2; T3 theta3 applied; S3 after round3; S4; S5; S6"""
    d={}
    S1=rnd(A,0); d['S1']=S1; d['A2']=theta(S1)
    S2=rnd(S1,1); d['S2']=S2; d['T3']=theta(S2)
    S3=rnd(S2,2); d['S3']=S3; d['T4']=theta(S3)
    S4=rnd(S3,3); d['S4']=S4; d['T5']=theta(S4)
    S5=rnd(S4,4); d['S5']=S5; d['T6']=theta(S5)
    S6=rnd(S5,5); d['S6']=S6
    return d
