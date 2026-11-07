import numpy as np
IV=[0x6A09E667,0xBB67AE85,0x3C6EF372,0xA54FF53A,0x510E527F,0x9B05688C,0x1F83D9AB,0x5BE0CD19]
PERM=(2,6,3,10,7,0,4,13,1,11,12,5,9,14,15,8)
G=((0,4,8,12),(1,5,9,13),(2,6,10,14),(3,7,11,15),(0,5,10,15),(1,6,11,12),(2,7,8,13),(3,4,9,14))
U=np.uint32
def ror(x,k): return (x>>U(k))|(x<<U(32-k))
def comp(m,rounds=3,flags=11,blen=64):
    """m: list of 16 uint32 arrays (same length N). returns list of 8 digest-word arrays."""
    N=len(m[0])
    v=[np.full(N,c,U) for c in IV+IV[:4]+[0,0,blen,flags]]
    m=list(m)
    for _ in range(rounds):
        for j,(a,b,c,d) in enumerate(G):
            x,y=m[2*j],m[2*j+1]
            v[a]=v[a]+v[b]+x; v[d]=ror(v[d]^v[a],16)
            v[c]=v[c]+v[d]; v[b]=ror(v[b]^v[c],12)
            v[a]=v[a]+v[b]+y; v[d]=ror(v[d]^v[a],8)
            v[c]=v[c]+v[d]; v[b]=ror(v[b]^v[c],7)
        m=[m[i] for i in PERM]
    return [v[i]^v[i+8] for i in range(8)]
if __name__=="__main__":
    import sys,os,struct,random
    sys.path.insert(0,"../../poseidon/pareto_clone/verifier")
    import blake3 as ref
    random.seed(1)
    for r in (3,7):
        N=64
        msgs=[os.urandom(64) for _ in range(N)]
        w=np.array([struct.unpack("<16I",x) for x in msgs],dtype=U)
        d=comp([w[:,i].copy() for i in range(16)],rounds=r)
        ok=all(struct.pack("<8I",*[int(d[i][k]) for i in range(8)])==ref.blake3(msgs[k],r) for k in range(N))
        print("rounds",r,"match",ok)
