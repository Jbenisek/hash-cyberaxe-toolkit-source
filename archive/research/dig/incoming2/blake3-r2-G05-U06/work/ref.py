
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

import sys, os, random, struct
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/hash-smash'))
from verifier import blake3 as V
M=0xFFFFFFFF
def ror(x,n): return ((x>>n)|(x<<(32-n)))&M
def G(v,a,b,c,d,x,y):
    V._g(v,a,b,c,d,x,y)
def round1(X, mp):
    """one more round on state X with ROUND-1 ordered message mp[0..15]; returns Y (after columns), Z"""
    v=list(X)
    for k,(a,b,c,d) in enumerate([(0,4,8,12),(1,5,9,13),(2,6,10,14),(3,7,11,15)]):
        G(v,a,b,c,d,mp[2*k],mp[2*k+1])
    Y=list(v)
    for k,(a,b,c,d) in enumerate([(0,5,10,15),(1,6,11,12),(2,7,8,13),(3,4,9,14)]):
        G(v,a,b,c,d,mp[8+2*k],mp[9+2*k])
    return Y,v
def fold(Z): return [Z[i]^Z[i+8] for i in range(8)]
def mp_from_w(w): return [w[i] for i in V.PERMUTATION]
if __name__=="__main__":
    # known answer 1: full 7-round BLAKE3 empty-string digest of the verifier equals official
    assert V.blake3(b"",7).hex()=="af1349b9f5f9a1a6a0404dea36dcc9499bcb25c9adc112b7cc9a93cae41f3262"
    # known answer 2: my 2-round compression (init, round0 via verifier _g, round1 via round1()) == verifier r=2
    random.seed(1)
    for t in range(200):
        n=random.randrange(1,64); data=bytes(random.randrange(256) for _ in range(n))
        w=struct.unpack("<16I",data.ljust(64,b"\0"))
        v=list(V.IV)+list(V.IV[:4])+[0,0,n,3|8]
        m=list(w)
        for (a,b,c,d,i) in [(0,4,8,12,0),(1,5,9,13,2),(2,6,10,14,4),(3,7,11,15,6),(0,5,10,15,8),(1,6,11,12,10),(2,7,8,13,12),(3,4,9,14,14)]:
            G(v,a,b,c,d,m[i],m[i+1])
        mp=mp_from_w(w)
        Y,Z=round1(v,mp)
        d=fold(Z)
        h=b"".join(struct.pack("<I",x) for x in d)
        assert h==V.blake3(data,2),t
    print("round1 ref == verifier on 200 random msgs (r=2): OK")
    # pins
    X=[0]*16; X[3]=0x29d4fa98;X[7]=0xbee3af28;X[11]=0x44036000;X[15]=0x40c58500
    for sgn in (8,-8):
        outs=[]
        for w4 in (0x97475638,(0x97475638+sgn)&M):
            v=list(X); G(v,3,7,11,15,w4,0x0007c006); outs.append(tuple(v[i] for i in (3,7,11,15)))
        print(sgn,[tuple('%08x'%x for x in o) for o in outs])
