
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

import sys,json,os,random
sys.path.insert(0,os.path.dirname(__file__))
import b3core as B
VER=_hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/pareto_clone')
sys.path.insert(0,VER)
from verifier import blake3 as V
import pathlib
vec=json.loads(pathlib.Path(VER,'tests/fixtures/blake3-vectors.json').read_text())
ok=True
for it in vec:
    if it['length']==64:
        data=bytes(i%251 for i in range(64)); mine=B.digest_bytes(data,it['rounds']).hex()
        print('fixture len64 rounds',it['rounds'],mine==it['digest']); ok&=mine==it['digest']
# empty-input style official 7-round check for a 64-byte one-block message vs verifier (rounds 7 and 3)
rnd=random.Random(1)
for rounds in (7,3):
    for _ in range(200):
        d=bytes(rnd.getrandbits(8) for _ in range(64))
        a=B.digest_bytes(d,rounds); b=V.blake3(d,rounds)[:32]
        if a!=b: ok=False; print('MISMATCH',rounds); break
    else: print('verifier match rounds',rounds,'200 msgs')
# official all-zero... 7-round known vector: BLAKE3 of 64 bytes i%251 (official test vector, len 64) digest prefix
print('official 7-round len64 first 32 bytes', B.digest_bytes(bytes(i%251 for i in range(64)),7).hex())
# packed circuit vs scalar, 3 rounds
prog,out=B.build(3); print('ops',len(prog))
from collections import Counter; print(Counter(o['kind'] for o in prog))
good=all(B.check(prog,out,[rnd.getrandbits(256) for _ in range(7)]) for _ in range(30)); print('packed circuit == scalar',good); ok&=good
print('ALLOK',ok)
