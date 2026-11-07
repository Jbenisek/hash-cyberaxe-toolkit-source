# validation: (1) own compress vs organizer verifier on single-block messages at 7 and 2 rounds; known BLAKE3 vector (empty, 7 rounds)

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
sys.path.insert(0,_hca_public_path_text('__HCA_WORKSPACE__/hash-smash')); sys.path.insert(0,'.')
from verifier import blake3 as vb
from initlib import *
def own(data,rounds):
    w=struct.unpack('<16I',data.ljust(64,b'\0'))
    st,o=compress(IV,w,len(data),0,0,11,rounds)
    return struct.pack('<8I',*o)
assert own(b'',7).hex()=='af1349b9f5f9a1a6a0404dea36dcc9499bcb25c9adc112b7cc9a93cae41f3262','empty vector'
print('known vector empty/7 rounds ok')
rng=random.Random(1); n=0
for r in (2,7):
    for _ in range(500):
        L=rng.randrange(0,65); d=bytes(rng.randrange(256) for _ in range(L))
        assert own(d,r)==vb.blake3(d,r),(r,L); n+=1
print('own == organizer verifier on',n,'single-block messages (2 and 7 rounds)')
# control builder with h=IV
def rnd(): return rng.getrandbits(32)
ok=0
for _ in range(3000):
    a=[rnd() for _ in range(8)]
    A,B,_w=build(IV,*a)
    sa,oa=compress(IV,A,55); sb,ob=compress(IV,B,63)
    X=sa['X']
    assert (X[3],X[7],X[11],X[15])==(X3,X7,X11,X15) and sa['Y'][4]==a[7] and sa['X']==sb['X'] and all(oa[i]==ob[i] for i in (0,2,5,7))
    # bytes level: verifier confirms
    ba=struct.pack('<16I',*A)[:55]; bb=struct.pack('<16I',*B)[:63]
    ha=vb.blake3(ba,2); hb=vb.blake3(bb,2)
    assert all(ha[4*i:4*i+4]==hb[4*i:4*i+4] for i in (0,2,5,7)); ok+=1
print('control h=IV builder: pins, Y4=y, X equal, digest words 0,2,5,7 equal; also via organizer verifier on byte strings (w14=w15=0 -> 55/63 bytes honest if top byte of w13 0):',ok,'/3000')
