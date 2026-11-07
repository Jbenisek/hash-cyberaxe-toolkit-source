# own BLAKE3 reduced-round reference, block level, with round-state access (scan-once-wave2, blake3-r2-G05-U08)

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

import struct, sys, random
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/hash-smash/verifier'))
M=0xFFFFFFFF
IV=(0x6A09E667,0xBB67AE85,0x3C6EF372,0xA54FF53A,0x510E527F,0x9B05688C,0x1F83D9AB,0x5BE0CD19)
PERM=(2,6,3,10,7,0,4,13,1,11,12,5,9,14,15,8)
CALLS=((0,4,8,12),(1,5,9,13),(2,6,10,14),(3,7,11,15),(0,5,10,15),(1,6,11,12),(2,7,8,13),(3,4,9,14))
def ror(x,n): return ((x>>n)|(x<<(32-n)))&M
def rol(x,n): return ror(x,32-n)
def g(v,a,b,c,d,x,y):
    v[a]=(v[a]+v[b]+x)&M; v[d]=ror(v[d]^v[a],16); v[c]=(v[c]+v[d])&M; v[b]=ror(v[b]^v[c],12)
    v[a]=(v[a]+v[b]+y)&M; v[d]=ror(v[d]^v[a],8);  v[c]=(v[c]+v[d])&M; v[b]=ror(v[b]^v[c],7)
def init(h,t,b,f): return list(h)+list(IV[:4])+[t&M,(t>>32)&M,b,f]
def rounds_states(h,words,t,b,f,rounds):
    """list of states after each round (X after round 0, Z after the last)"""
    v=init(h,t,b,f); m=list(words); out=[]
    for r in range(rounds):
        for k,(a,bb,c,d) in enumerate(CALLS): g(v,a,bb,c,d,m[2*k],m[2*k+1])
        m=[m[i] for i in PERM]; out.append(list(v))
    return out
def comp(h,words,t,b,f,rounds):
    z=rounds_states(h,words,t,b,f,rounds)[-1]
    return tuple(z[i]^z[i+8] for i in range(8)), tuple(z[i+8]^h[i] for i in range(8))
def words_of(block): return struct.unpack('<16I',block.ljust(64,b'\0'))
def chunk_out(chunk,t,rounds):
    h=IV; last=max(0,(len(chunk)-1)//64*64)
    for off in range(0,last+1,64):
        blk=chunk[off:off+64]; f=1 if off==0 else 0
        if off==last: return h,words_of(blk),t,len(blk),f|2
        h=comp(h,words_of(blk),t,64,f,rounds)[0]
def hash_(data,rounds):
    n=max(1,(len(data)+1023)//1024)
    def sub(lo,hi):  # chunks lo..hi-1 -> (cv) ; returns node output tuple (args to comp)
        if hi-lo==1: return chunk_out(data[lo*1024:(lo+1)*1024],lo,rounds)
        k=1
        while k*2<hi-lo: k*=2
        L=cv(sub(lo,lo+k)); R=cv(sub(lo+k,hi))
        return IV,tuple(L)+tuple(R),0,64,4
    def cv(o): return comp(o[0],o[1],o[2],o[3],o[4],rounds)[0]
    o=sub(0,n); h,w,t,b,f=o
    d=comp(h,w,t,b,f|8,rounds)[0]
    return struct.pack('<8I',*d)
