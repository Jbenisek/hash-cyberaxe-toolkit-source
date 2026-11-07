
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

import sys, random, struct
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/hash-smash'))
from verifier.blake3 import blake3 as ref
M=0xffffffff
IV=[0x6A09E667,0xBB67AE85,0x3C6EF372,0xA54FF53A,0x510E527F,0x9B05688C,0x1F83D9AB,0x5BE0CD19]
P=[2,6,3,10,7,0,4,13,1,11,12,5,9,14,15,8]
ror=lambda x,n:((x>>n)|(x<<(32-n)))&M
def G(v,a,b,c,d,x,y):
    v[a]=(v[a]+v[b]+x)&M; v[d]=ror(v[d]^v[a],16); v[c]=(v[c]+v[d])&M; v[b]=ror(v[b]^v[c],12)
    v[a]=(v[a]+v[b]+y)&M; v[d]=ror(v[d]^v[a],8); v[c]=(v[c]+v[d])&M; v[b]=ror(v[b]^v[c],7)
def rnd(v,m):
    G(v,0,4,8,12,m[0],m[1]);G(v,1,5,9,13,m[2],m[3]);G(v,2,6,10,14,m[4],m[5]);G(v,3,7,11,15,m[6],m[7])
    G(v,0,5,10,15,m[8],m[9]);G(v,1,6,11,12,m[10],m[11]);G(v,2,7,8,13,m[12],m[13]);G(v,3,4,9,14,m[14],m[15])
def perm(m): return [m[i] for i in P]
def comp_states(m,blen,R):
    v=IV[:]+IV[:4]+[0,0,blen,11]; out=[]
    for r in range(R): rnd(v,m); out.append(v[:]); m=perm(m)
    return out
def digest(v): return [v[i]^v[i+8] for i in range(8)]
K=(IV[2]+IV[6])&M
def pair(rng):
    w=[rng.getrandbits(32) for _ in range(16)]; w[14]=w[15]=0; w[13]&=0x00ffffff
    w2=w[:]; a1=(K+w[4])&M; w2[4]=((a1^8)-K)&M; w2[5]=(w[5]+w[4]-w2[4])&M
    A=b"".join(struct.pack("<I",x) for x in w)[:55]; B=b"".join(struct.pack("<I",x) for x in w2)[:63]
    return w,w2,A,B
rng=random.Random(20261020); N=int(sys.argv[1]) if len(sys.argv)>1 else 20000
# (1) real messages from IV: round-1 cancellation, ref agreement, digest bits at r1..r3
eq=[0]*4; bitagree={1:[0]*256,2:[0]*256,3:[0]*256}; refok=0; wordeq={1:[0]*16,2:[0]*16,3:[0]*16}
for t in range(N):
    w,w2,A,B=pair(rng)
    sa=comp_states(w,55,3); sb=comp_states(w2,63,3)
    for R in (1,2,3):
        for i in range(16): wordeq[R][i]+= sa[R-1][i]==sb[R-1][i]
        da=digest(sa[R-1]); db=digest(sb[R-1]); x=sum(((da[i]^db[i])<<(32*i)) for i in range(8))
        for b in range(256): bitagree[R][b]+= not (x>>b)&1
    if t<200:
        refok+= ref(A,3)==b"".join(struct.pack("<I",x) for x in digest(sa[2])) and ref(B,3)==b"".join(struct.pack("<I",x) for x in digest(sb[2]))
print("ref match r3 (first 200 pairs, both msgs):",refok)
for R in (1,2,3):
    print(f"R={R} state words always equal:",[i for i in range(16) if wordeq[R][i]==N],
          " digest bits always equal:",sum(1 for b in range(256) if bitagree[R][b]==N),
          " mean per-bit agree: %.4f"%(sum(bitagree[R])/256/N), " max: %.4f min: %.4f"%(max(bitagree[R])/N,min(bitagree[R])/N))
# (2) C3 pin (Fact P) sampled forward from round-1 state X with column 3 pinned, w4=W4, w13=W13
X3,X7,X11,X15,W4,W13=0x29d4fa98,0xbee3af28,0x44036000,0x40c58500,0x97475638,0x0007c006
W4b=((((K+W4)&M)^8)-K)&M
print("W4' =",hex(W4b))
weq={1:[0]*16,2:[0]*16}; bag={1:[0]*256,2:[0]*256}
for t in range(N):
    X=[rng.getrandbits(32) for _ in range(16)]; X[3],X[7],X[11],X[15]=X3,X7,X11,X15
    w=[rng.getrandbits(32) for _ in range(16)]; w[14]=w[15]=0; w[4]=W4; w[13]=W13
    w2=w[:]; w2[4]=W4b; w2[5]=(w[5]+W4-W4b)&M
    m1=perm(w); m1b=perm(w2); va=X[:]; vb=X[:]
    for R in (1,2):
        rnd(va,m1); rnd(vb,m1b); m1=perm(m1); m1b=perm(m1b)
        for i in range(16): weq[R][i]+= va[i]==vb[i]
        da=digest(va); db=digest(vb); x=sum(((da[i]^db[i])<<(32*i)) for i in range(8))
        for b in range(256): bag[R][b]+= not (x>>b)&1
for R in (1,2):
    print(f"pinned family, rounds after X = {R} (total rounds {R+1}): state words equal:",[i for i in range(16) if weq[R][i]==N],
          " digest bits always equal:",sum(1 for b in range(256) if bag[R][b]==N), " mean per-bit agree: %.4f"%(sum(bag[R])/256/N),
          " max %.4f"%(max(bag[R])/N))
