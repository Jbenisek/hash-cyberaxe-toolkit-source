
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

import sys, os, random, itertools
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/hash-smash/verifier'))
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/blake3_r3/b3r3s/pkg/blake3/experiments'))
import blake3 as org, rho
M32=0xFFFFFFFF
def comp(cv, m, counter, blen, flags, rounds=3):
    v = list(cv)+list(rho.IV[:4])+[counter&M32,counter>>32,blen,flags]
    m=list(m)
    for _ in range(rounds):
        for j,(a,b,c,d) in enumerate(rho.GCALLS):
            x,y=m[2*j],m[2*j+1]
            v[a]=(v[a]+v[b]+x)&M32; v[d]=rho._ror(v[d]^v[a],16)
            v[c]=(v[c]+v[d])&M32; v[b]=rho._ror(v[b]^v[c],12)
            v[a]=(v[a]+v[b]+y)&M32; v[d]=rho._ror(v[d]^v[a],8)
            v[c]=(v[c]+v[d])&M32; v[b]=rho._ror(v[b]^v[c],7)
        m=[m[i] for i in rho.PERM]
    return [v[i]^v[i+8] for i in range(8)], [v[i+8]^cv[i] for i in range(8)]
def words(b): return [int.from_bytes(b[4*i:4*i+4],'little') for i in range(16)]
rng=random.Random(1); bad=0; N=200
for t in range(N):
    P=bytes(rng.randrange(256) for _ in range(64)); x=rng.getrandbits(256)
    msg=P+bytes(32)+x.to_bytes(32,'little')
    ref=org.blake3(msg,3)
    cv=(lambda r:r[0][:8] if False else None)
    lo,hi=comp(list(rho.IV),words(P),0,64,1)
    h=lo  # non-root cv = first 8 words of the 16-word output = v[i]^v[i+8]
    d,_=comp(h,[0]*8+[(x>>(32*i))&M32 for i in range(8)],0,64,10)
    mine=b''.join(w.to_bytes(4,'little') for w in d)
    bad+= (mine!=ref)
print("mechanics: 2-block P||0^32||x, organizer blake3 rounds=3 vs model h=cv(P), flags CHUNK_END|ROOT=10: mismatches",bad,"of",N)
# single-block control
bad=0
for t in range(50):
    x=rng.getrandbits(256); ref=org.blake3(bytes(32)+x.to_bytes(32,'little'),3)
    mine=b''.join(w.to_bytes(4,'little') for w in rho.digest_words([0]*8+[(x>>(32*i))&M32 for i in range(8)]))
    bad+=(mine!=ref)
print("control single block mismatches",bad,"of 50")
