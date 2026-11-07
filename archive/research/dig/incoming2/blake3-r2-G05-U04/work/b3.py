# own BLAKE3 reduced-round reference with traces (scan-once-wave2, blake3-r2-G05-U04)

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
def ror(x,n): return ((x>>n)|(x<<(32-n)))&M
def rol(x,n): return ror(x,32-n)
def g(v,a,b,c,d,x,y):
    v[a]=(v[a]+v[b]+x)&M; v[d]=ror(v[d]^v[a],16); v[c]=(v[c]+v[d])&M; v[b]=ror(v[b]^v[c],12)
    v[a]=(v[a]+v[b]+y)&M; v[d]=ror(v[d]^v[a],8);  v[c]=(v[c]+v[d])&M; v[b]=ror(v[b]^v[c],7)
CALLS=((0,4,8,12),(1,5,9,13),(2,6,10,14),(3,7,11,15),(0,5,10,15),(1,6,11,12),(2,7,8,13),(3,4,9,14))
def init(cv,ctr,blen,flags): return list(cv)+list(IV[:4])+[ctr&M,ctr>>32,blen,flags]
def run(cv,words,ctr,blen,flags,rounds,trace=None):
    """returns final v; trace (list) gets state before each G call: (round,callidx,inputs a,b,c,d,x,y)"""
    v=init(cv,ctr,blen,flags); m=list(words)
    for r in range(rounds):
        for k,(a,b,c,d) in enumerate(CALLS):
            if trace is not None: trace.append((r,k,v[a],v[b],v[c],v[d],m[2*k],m[2*k+1]))
            g(v,a,b,c,d,m[2*k],m[2*k+1])
        m=[m[i] for i in PERM]
    return v
def digest(v,cv=IV): return tuple(v[i]^v[i+8] for i in range(8))
def single_block_hash(msg,rounds):
    words=struct.unpack('<16I',msg.ljust(64,b'\0'))
    v=run(IV,words,0,len(msg),11,rounds)
    return struct.pack('<8I',*digest(v))
if __name__=='__main__':
    import blake3 as ver
    e=single_block_hash(b'',7).hex()
    print('empty r7',e, e.startswith('af1349b9f5f9a1a6a0404dea36dcc949'))
    random.seed(1); bad=0
    for n in (0,1,31,55,63,64):
        for r in (2,7):
            for _ in range(20):
                m=bytes(random.getrandbits(8) for _ in range(n))
                if single_block_hash(m,r)!=ver.blake3(m,r): bad+=1
    print('mismatch vs organizer verifier (single-block, r2/r7):',bad)
