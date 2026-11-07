M=0xffffffff
IV=[0x6A09E667,0xBB67AE85,0x3C6EF372,0xA54FF53A,0x510E527F,0x9B05688C,0x1F83D9AB,0x5BE0CD19]
PI=[2,6,3,10,7,0,4,13,1,11,12,5,9,14,15,8]
def ror(x,n): return ((x>>n)|(x<<(32-n)))&M
def G(v,a,b,c,d,mx,my):
    v[a]=(v[a]+v[b]+mx)&M; v[d]=ror(v[d]^v[a],16); v[c]=(v[c]+v[d])&M; v[b]=ror(v[b]^v[c],12)
    v[a]=(v[a]+v[b]+my)&M; v[d]=ror(v[d]^v[a],8); v[c]=(v[c]+v[d])&M; v[b]=ror(v[b]^v[c],7)
COLS=[(0,4,8,12),(1,5,9,13),(2,6,10,14),(3,7,11,15)]
DIAG=[(0,5,10,15),(1,6,11,12),(2,7,8,13),(3,4,9,14)]
def rnd(v,m):
    for i,(a,b,c,d) in enumerate(COLS): G(v,a,b,c,d,m[2*i],m[2*i+1])
    for i,(a,b,c,d) in enumerate(DIAG): G(v,a,b,c,d,m[8+2*i],m[9+2*i])
def init(h,m,tlo,thi,b,d): return list(h)+IV[:4]+[tlo,thi,b,d]
def states(h,m,tlo,thi,b,d,rounds=2):
    """returns list of states after each round (index 0 = init)"""
    v=init(h,m,tlo,thi,b,d); m=list(m); out=[list(v)]
    for r in range(rounds):
        rnd(v,m); out.append(list(v)); m=[m[p] for p in PI]
    return out
def compress(h,m,tlo,thi,b,d,rounds=2,full=False):
    v=states(h,m,tlo,thi,b,d,rounds)[-1]
    o=[v[i]^v[i+8] for i in range(8)]
    if full: o+= [v[i+8]^h[i] for i in range(8)]
    return o
