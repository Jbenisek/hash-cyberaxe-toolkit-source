"""own batch BLAKE3 compression (numpy), validated against verifier/blake3.py. alt-scan harness 2026-10-12"""

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

import numpy as np, struct, sys
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/pareto_clone'))
IV = np.array([0x6A09E667,0xBB67AE85,0x3C6EF372,0xA54FF53A,0x510E527F,0x9B05688C,0x1F83D9AB,0x5BE0CD19],dtype=np.uint32)
PERM=(2,6,3,10,7,0,4,13,1,11,12,5,9,14,15,8)
U=np.uint32
def ror(x,n): return (x>>U(n))|(x<<U(32-n))
def G(v,a,b,c,d,x,y):
    v[a]=v[a]+v[b]+x; v[d]=ror(v[d]^v[a],16); v[c]=v[c]+v[d]; v[b]=ror(v[b]^v[c],12)
    v[a]=v[a]+v[b]+y; v[d]=ror(v[d]^v[a],8);  v[c]=v[c]+v[d]; v[b]=ror(v[b]^v[c],7)
def rnd(v,m):
    G(v,0,4,8,12,m[0],m[1]);G(v,1,5,9,13,m[2],m[3]);G(v,2,6,10,14,m[4],m[5]);G(v,3,7,11,15,m[6],m[7])
    G(v,0,5,10,15,m[8],m[9]);G(v,1,6,11,12,m[10],m[11]);G(v,2,7,8,13,m[12],m[13]);G(v,3,4,9,14,m[14],m[15])
def init(cv,ctr,blen,flags,N):
    """cv: (8,N) or (8,) ; ctr,blen,flags: int or (N,)"""
    v=np.zeros((16,N),dtype=np.uint32)
    cv=np.asarray(cv,dtype=np.uint32)
    for i in range(8): v[i]=cv[i] if cv.ndim==1 else cv[i]
    for i in range(4): v[8+i]=IV[i]
    ctr=np.asarray(ctr,dtype=np.uint64)
    v[12]=(ctr&np.uint64(0xFFFFFFFF)).astype(np.uint32); v[13]=(ctr>>np.uint64(32)).astype(np.uint32)
    v[14]=np.asarray(blen,dtype=np.uint32); v[15]=np.asarray(flags,dtype=np.uint32)
    return v
def compress_state(m,cv=IV,ctr=0,blen=64,flags=11,rounds=3):
    """m: (16,N) uint32. returns final state v (16,N) before feed-forward."""
    N=m.shape[1]; v=init(cv,ctr,blen,flags,N); m=[m[i] for i in range(16)]
    for _ in range(rounds):
        rnd(v,m); m=[m[i] for i in PERM]
    return v
def compress(m,cv=IV,ctr=0,blen=64,flags=11,rounds=3,full=False):
    v=compress_state(m,cv,ctr,blen,flags,rounds)
    d=v[:8]^v[8:]
    if full:
        cvv=np.asarray(cv,dtype=np.uint32)
        if cvv.ndim==1: cvv=cvv[:,None]
        return np.concatenate([d,v[8:]^cvv])
    return d
def hw(a):  # popcount of uint32 array
    a=a.astype(np.uint64); c=np.zeros(a.shape,dtype=np.int64)
    for s in range(32): c+=((a>>np.uint64(s))&np.uint64(1)).astype(np.int64)
    return c
def words_to_bytes(w): return struct.pack("<%dI"%len(w),*[int(x) for x in w])
def bytes_to_words(b): return np.frombuffer(b,dtype="<u4")

def low_priority():
    try:
        import ctypes
        ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x4000)  # BELOW_NORMAL
    except Exception: pass
low_priority()

def run_rounds(v,m,rounds,snap=None):
    """v: (16,N) state (modified in place copy), m: (16,N). returns list of states after each round (index 0 = after round 1)."""
    v=v.copy(); m=[m[i] for i in range(16)]; outs=[]
    for _ in range(rounds):
        rnd(v,m); m=[m[i] for i in PERM]; outs.append(v.copy())
    return outs
def rand_words(rng,n,words=range(16)):
    m=np.zeros((16,n),dtype=np.uint32)
    for w in words: m[w]=rng.integers(0,2**32,n,dtype=np.uint64).astype(np.uint32)
    return m
