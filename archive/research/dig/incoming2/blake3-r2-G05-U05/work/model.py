
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
from verifier import blake3 as V
M=0xFFFFFFFF
ror=V._ror
IV=V.IV; PERM=V.PERMUTATION
def g(v,a,b,c,d,x,y): V._g(v,a,b,c,d,x,y)
G4=[(0,4,8,12),(1,5,9,13),(2,6,10,14),(3,7,11,15),(0,5,10,15),(1,6,11,12),(2,7,8,13),(3,4,9,14)]
def round_(v,m):
    for k,(a,b,c,d) in enumerate(G4): g(v,a,b,c,d,m[2*k],m[2*k+1])
def comp(cv,m,t,bl,fl,rounds=2):
    v=list(cv)+list(IV[:4])+[t&M,t>>32,bl,fl]; m=list(m)
    for _ in range(rounds):
        round_(v,m); m=[m[i] for i in PERM]
    return v
def digest(v): return tuple(v[i]^v[i+8] for i in range(8))
K=(IV[2]+IV[6])&M
def w4p(w4): return ((((K+w4)&M)^8)-K)&M
if __name__=='__main__':
    # known answer: 7-round empty hash
    h=V.blake3(b'',7).hex()
    assert h=='af1349b9f5f9a1a6a0404dea36dcc9499bcb25c9adc112b7cc9a93cae41f3262',h
    print('7-round empty ok')
    random.seed(5)
    for _ in range(200):
        n=random.randrange(1,65); d=random.randbytes(n)
        w=list(struct.unpack('<16I',d.ljust(64,b'\0')))
        for R in (1,2,7):
            v=comp(IV,w,0,n,11,R)
            assert struct.pack('<8I',*digest(v))==V.blake3(d,R),(n,R)
    print('model == verifier at 1,2,7 rounds on 600 cases')
    print('W4 pin check', hex(w4p(0x97475638)))
    # Lemma L pair: lengths 55/63
    ok=0
    for _ in range(300):
        w=[random.getrandbits(32) for _ in range(16)]; w[14]=w[15]=0; w[13]&=0x00FFFFFF
        w2=list(w); w2[4]=w4p(w[4]); w2[5]=(w[5]+w[4]-w2[4])&M
        va=comp(IV,w,0,55,11,1); vb=comp(IV,w2,0,63,11,1)
        # state after round 0 only
        def r0(wd,bl):
            v=list(IV)+list(IV[:4])+[0,0,bl,11]; round_(v,wd); return v
        assert r0(w,55)==r0(w2,63); ok+=1
    print('Lemma L: X identical after round 0 in',ok,'/300')
