import numpy as np, random, time, json
IV=(0x6A09E667,0xBB67AE85,0x3C6EF372,0xA54FF53A)
D=(0,0,64,10)   # v12..v15: counter lo, hi, block len, flags (CHUNK_END|ROOT)
def ror(x,k): return ((x>>np.uint32(k))|(x<<np.uint32(32-k)))
def col(j,a,b):
    a=np.asarray(a,dtype=np.uint32);b=np.asarray(b,dtype=np.uint32)
    c=np.uint32(IV[j]);d=np.uint32(D[j])
    a1=a+b; d1=ror(np.uint32(d)^a1,16); c1=c+d1; b1=ror(b^c1,12)
    a2=a1+b1; d2=ror(d1^a2,8); c2=c1+d2; b2=ror(b1^c2,7)
    return a2,b2
def solve(j,a,target):
    """find b with B_j = b2 == target"""
    t0=time.time(); out=[]
    CH=1<<24
    for s in range(0,1<<32,CH):
        b=np.arange(s,s+CH,dtype=np.uint64).astype(np.uint32)
        _,b2=col(j,np.uint32(a),b)
        w=np.nonzero(b2==np.uint32(target))[0]
        for i in w: out.append(int(b[i]))
    print("solve col",j,"found",len(out),"in %.0fs"%(time.time()-t0),flush=True)
    return out
rng=random.Random(77); M=0xFFFFFFFF
h=[None]*8
h[1]=rng.getrandbits(32);h[5]=rng.getrandbits(32)
A1,_=col(1,h[1],h[5]); A1=int(A1)
h[2]=rng.getrandbits(32); h[6]=solve(2,h[2],(-A1)&M)[0]
A2,_=col(2,h[2],h[6]); A2=int(A2)
h[3]=rng.getrandbits(32); h[7]=solve(3,h[3],(-A2)&M)[0]
A3,_=col(3,h[3],h[7]); A3=int(A3)
h[0]=rng.getrandbits(32); h[4]=solve(0,h[0],(-A3)&M)[0]
print(json.dumps(h))
json.dump(h,open("h_tuned.json","w"))
