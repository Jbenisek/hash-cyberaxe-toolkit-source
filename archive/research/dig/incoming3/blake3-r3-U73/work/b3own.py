# own vectorised BLAKE3 compression (numpy uint32), trace of G calls; validated against organizer verifier in validate_own.py
import numpy as np
IV=(0x6A09E667,0xBB67AE85,0x3C6EF372,0xA54FF53A,0x510E527F,0x9B05688C,0x1F83D9AB,0x5BE0CD19)
PERM=(2,6,3,10,7,0,4,13,1,11,12,5,9,14,15,8)
U=np.uint32
def ror(x,n): return (x>>U(n))|(x<<U(32-n))
def G(v,a,b,c,d,x,y):
    v[a]=v[a]+v[b]+x; v[d]=ror(v[d]^v[a],16); v[c]=v[c]+v[d]; v[b]=ror(v[b]^v[c],12)
    v[a]=v[a]+v[b]+y; v[d]=ror(v[d]^v[a],8);  v[c]=v[c]+v[d]; v[b]=ror(v[b]^v[c],7)
CALLS=[(0,4,8,12),(1,5,9,13),(2,6,10,14),(3,7,11,15),(0,5,10,15),(1,6,11,12),(2,7,8,13),(3,4,9,14)]
NAMES=['K0','K1','K2','K3','D0','D1','D2','D3','C0','C1','C2','C3','E0','E1','E2','E3']
def compress(cv,m,t,b,f,rounds=2,hook=None):
    """cv,m: lists of arrays/ints; returns list v after rounds, and digest8"""
    n=max(np.size(x) for x in list(cv)+list(m)+[t,b,f])
    def A(x): return np.broadcast_to(np.asarray(x,dtype=U),(n,)).copy()
    v=[A(x) for x in cv]+[A(IV[i]) for i in range(4)]+[A(t),A(0),A(b),A(f)]
    mm=[A(x) for x in m]
    for r in range(rounds):
        for k,(a,bb,c,d) in enumerate(CALLS):
            if hook: hook(r,k,v,mm)
            G(v,a,bb,c,d,mm[2*k],mm[2*k+1])
        if hook: hook(r,8,v,mm)
        mm=[mm[i] for i in PERM]
    dig=[v[i]^v[i+8] for i in range(8)]
    return v,dig
