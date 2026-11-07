
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

import numpy as np, hashlib, sys
sys.path.insert(0,'.')
from kk6 import *
rng=np.random.default_rng(1)
# 1. 24-round validation against hashlib (135-byte messages)
msgs=rng.integers(0,256,size=(20,135),dtype=np.uint8)
A=msg_to_lanes(msgs); A=perm(A,24)
dig=np.ascontiguousarray(A.T).astype('<u8').view(np.uint8).reshape(20,200)[:,:32]
ok=all(bytes(dig[i])==hashlib.sha3_256(bytes(msgs[i])).digest() for i in range(20))
print("24-round sha3_256 match (20 msgs):",ok)
# 2. 6-round vs organizer reference
sys.path.insert(0,_hca_public_path_text('__HCA_WORKSPACE__/research/sha3r5/htrail/sc12/SOLCLOUD_12_RESEARCH/inputs'))
import SOLCLOUD_12_INPUT_keccak as org
okk=True
for i in range(20):
    st=bytes(msgs[i])+bytes([0x86])+bytes(64)
    out=org.permutation(st,rounds=6)
    A6=perm(msg_to_lanes(msgs[i:i+1]),6)
    mine=np.ascontiguousarray(A6.T).astype('<u8').view(np.uint8).tobytes()
    okk&=(mine==out)
print("6-round organizer permutation match:",okk)
# 3. leader lemmas
L=leader_state(rng,512)
T=theta(L)
print("L5,L15 zero after theta1:", not T[5].any(), not T[15].any(), " L8,L23 all-ones:", (T[8]==np.uint64(2**64-1)).all(), (T[23]==np.uint64(2**64-1)).all())
