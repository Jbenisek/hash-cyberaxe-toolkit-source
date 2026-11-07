
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

import sys,random,numpy as np
sys.path.insert(0,_hca_public_path_text('__HCA_WORKSPACE__/hash-smash/verifier'))
sys.path.insert(0,_hca_public_path_text('__HCA_WORKSPACE__/hash-smash'))
import importlib.util
spec=importlib.util.spec_from_file_location('vb3',_hca_public_path_text('__HCA_WORKSPACE__/hash-smash/verifier/blake3.py')); vb=importlib.util.module_from_spec(spec); spec.loader.exec_module(vb)
from b3own import *
random.seed(5); bad=0
for rounds in (1,2,7):
    for _ in range(300):
        cv=[random.getrandbits(32) for _ in range(8)]; m=[random.getrandbits(32) for _ in range(16)]
        t=random.getrandbits(32); b=random.choice((55,63,64)); f=random.choice((1,2,3,8,11,12))
        ref=vb._compress(cv,m,t,b,f,rounds)[:8]
        v,d=compress(cv,m,t,b,f,rounds)
        if tuple(int(x[0]) for x in d)!=ref: bad+=1
print('compress mismatches vs organizer _compress (900 random, rounds 1/2/7):',bad)
# known vector: BLAKE3("") at 7 rounds
print('verifier blake3("") 7r =',vb.blake3(b'',7).hex(),'expected af1349b9f5f9a1a6a0404dea36dcc9499bcb25c9adc112b7cc9a93cae41f3262')
# own: empty message root block: cv=IV,m=0,t=0,b=0,flags=1|2|8=11
v,d=compress(list(IV),[0]*16,0,0,11,7)
print('own 7r empty =',b''.join(int(x[0]).to_bytes(4,'little') for x in d).hex())
