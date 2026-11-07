# MODE.ctr: where the chunk counter words (v12 = t_lo, v13 = t_hi) are read at 2 rounds; own compressor validated against the verifier.

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

import sys,random,struct
sys.path.insert(0,_hca_public_path_text('__HCA_WORKSPACE__/hash-smash'))
from verifier import blake3 as ref
M=0xFFFFFFFF
IV=[0x6A09E667,0xBB67AE85,0x3C6EF372,0xA54FF53A,0x510E527F,0x9B05688C,0x1F83D9AB,0x5BE0CD19]
PERM=[2,6,3,10,7,0,4,13,1,11,12,5,9,14,15,8]
ror=lambda x,r:((x>>r)|(x<<(32-r)))&M
GS=[(0,4,8,12),(1,5,9,13),(2,6,10,14),(3,7,11,15),(0,5,10,15),(1,6,11,12),(2,7,8,13),(3,4,9,14)]
def comp(h,m,t,b,fl,rounds=2):
    v=list(h)+IV[:4]+[t&M,(t>>32)&M,b,fl]; m=list(m)
    for r in range(rounds):
        for k,(a,bb,c,d) in enumerate(GS):
            x,y=m[2*k],m[2*k+1]
            v[a]=(v[a]+v[bb]+x)&M; v[d]=ror(v[d]^v[a],16); v[c]=(v[c]+v[d])&M; v[bb]=ror(v[bb]^v[c],12)
            v[a]=(v[a]+v[bb]+y)&M; v[d]=ror(v[d]^v[a],8); v[c]=(v[c]+v[d])&M; v[bb]=ror(v[bb]^v[c],7)
        m=[m[i] for i in PERM]
    return [v[i]^v[i+8] for i in range(8)]
# validate on verifier: single-chunk root hash of 64 bytes (counter 0, flags CHUNK_START|CHUNK_END|ROOT = 11)
random.seed(5)
for _ in range(20):
    msg=bytes(random.getrandbits(8) for _ in range(64)); w=struct.unpack('<16I',msg)
    for rr in (1,2,7):
        assert struct.pack('<8I',*comp(IV,w,0,64,11,rr))==ref.blake3(msg,rr),'mismatch'
print('own compressor == organizer verifier on 60 cases (rounds 1,2,7; single block root, t=0)')
# word-level may-be-active taint (no cancellation)
def taint(init):
    act=[i in init for i in range(16)]; log=[]
    for r in range(2):
        for k,(a,b,c,d) in enumerate(GS):
            ins=[act[a],act[b],act[c],act[d]]
            if any(ins): log.append((r,k,ins))
            # ops: a1=a+b+x ; d1=d^a1 ; c1=c+d1 ; b1=b^c1 ; a2=a1+b1+y ; d2 ; c2 ; b2 -> all four outputs active if any input active (no cancellation)
            if any(ins): act[a]=act[b]=act[c]=act[d]=True
    dig=[act[i] or act[i+8] for i in range(8)]
    return log,[i for i in range(8) if dig[i]]
for name,init in (('v12=t_lo',{12}),('v13=t_hi',{13}),('both',{12,13})):
    log,dw=taint(init)
    first=[(r,('K' if k<4 else 'D') if r==0 else ('C' if k<4 else 'E'),k%4) for (r,k,ins) in log if sum(ins)>=1][:4]
    print(name,'first calls reading an active input:',first,'| G calls with active input:',len(log),'of 16 | digest words reachable:',dw)
# empirical: flip single counter bits, count which digest words change (2000 random messages/CVs each)
def emp(bits,n=2000):
    cnt=[0]*8
    for _ in range(n):
        m=[random.getrandbits(32) for _ in range(16)]; h=[random.getrandbits(32) for _ in range(8)]
        t=random.getrandbits(51)
        a=comp(h,m,t,64,3); b=comp(h,m,t^bits,64,3)
        for i in range(8): cnt[i]+= a[i]!=b[i]
    return cnt
print('digest word i changed when t_lo bit0 flipped (of 2000):',emp(1))
print('digest word i changed when t_lo bit31 flipped:',emp(1<<31))
print('digest word i changed when t_hi bit0 (t bit32) flipped:',emp(1<<32))
print('digest word i changed when t_hi bit18 (t bit50, top legal) flipped:',emp(1<<50))
# exact bijection facts at K0 / K1 (the only round-0 calls reading t): d1 = ror(t ^ a1, 16) is injective in t for fixed (h,w0). exhaustive over 2^20 low t values + check 2^32 algebraically
def k0_d1(h0,h4,w0,t): a1=(h0+h4+w0)&M; return ror(t^a1,16)
s=set(); h0,h4,w0=IV[0],IV[4],0x12345678
for t in range(1<<20): s.add(k0_d1(h0,h4,w0,t))
print('K0 d1 injective on t in [0,2^20):',len(s)==1<<20)
