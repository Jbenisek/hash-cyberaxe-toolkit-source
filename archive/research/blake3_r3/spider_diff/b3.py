import numpy as np, itertools, sys
M=np.uint32
IV=[0x6A09E667,0xBB67AE85,0x3C6EF372,0xA54FF53A,0x510E527F,0x9B05688C,0x1F83D9AB,0x5BE0CD19]
SIG=[2,6,3,10,7,0,4,13,1,11,12,5,9,14,15,8]
def rotr(x,n): return (x>>M(n))|(x<<M(32-n))
def G(v,a,b,c,d,mx,my):
    v[a]=v[a]+v[b]+mx; v[d]=rotr(v[d]^v[a],16)
    v[c]=v[c]+v[d]; v[b]=rotr(v[b]^v[c],12)
    v[a]=v[a]+v[b]+my; v[d]=rotr(v[d]^v[a],8)
    v[c]=v[c]+v[d]; v[b]=rotr(v[b]^v[c],7)
def rnd(v,m):
    G(v,0,4,8,12,m[0],m[1]);G(v,1,5,9,13,m[2],m[3]);G(v,2,6,10,14,m[4],m[5]);G(v,3,7,11,15,m[6],m[7])
    G(v,0,5,10,15,m[8],m[9]);G(v,1,6,11,12,m[10],m[11]);G(v,2,7,8,13,m[12],m[13]);G(v,3,4,9,14,m[14],m[15])
def perm(m): return [m[i] for i in SIG]
def init(m,blen,flags,N):
    z=lambda x: np.full(N,x,dtype=M)
    return [z(x) for x in IV]+[z(IV[0]),z(IV[1]),z(IV[2]),z(IV[3]),z(0),z(0),z(blen),z(flags)]
def compress(m,rounds,blen,flags,N,snap=None):
    v=init(m,blen,flags,N); m=list(m)
    for r in range(rounds):
        rnd(v,m); 
        if snap is not None: snap.append([x.copy() for x in v])
        m=perm(m)
    return v
def digest(v): return [v[i]^v[i+8] for i in range(8)]
if __name__=="__main__":
    # test vector: empty input
    with np.errstate(over='ignore'):
        v=compress([np.zeros(1,dtype=M) for _ in range(16)],7,0,11,1)
    d=digest(v); print(b''.join(int(x[0]).to_bytes(4,'little') for x in d).hex())
    print("af1349b9f5f9a1a6a0404dea36dcc9499bcb25c9adc112b7cc9a93cae41f3262")
