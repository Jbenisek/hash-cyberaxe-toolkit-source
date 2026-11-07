# validate: our comp (b3ctr.py) vs organizer verifier _compress at 2 and 7 rounds; BLAKE3("") 7-round vector; construction pins

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

import sys, random
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/hash-smash/verifier'))
import blake3 as V
from b3ctr import *
R = random.Random(13)
print('verifier _compress sig', V._compress.__code__.co_varnames[:8])
bad = 0
for rounds in (2, 7):
    for _ in range(500):
        w = [R.getrandbits(32) for _ in range(16)]; t = R.getrandbits(40); n = R.choice([64, 55, 7]); fl = R.choice([1, 2, 3, 8, 11])
        cv = [R.getrandbits(32) for _ in range(8)]
        ref = V._compress(cv, w, t, n, fl, rounds)
        # our comp uses IV chaining value; compare only with cv = IV
        ref = V._compress(IV[:8], w, t, n, fl, rounds)
        o = comp(w, t, n, flags=fl, rounds=rounds)
        if list(ref[:8]) != o: bad += 1
print('comp vs verifier mismatches (1000 random, rounds 2 and 7):', bad)
# BLAKE3('') known vector, 7 rounds: af1349b9f5f9a1a6a0404dea36dcc9499bcb25c9adc112b7cc9a93cae41f3262
o = comp([0]*16, 0, 0, flags=11, rounds=7)
h = b''.join(x.to_bytes(4, 'little') for x in o).hex()
print('BLAKE3("") via comp 7 rounds:', h, h == 'af1349b9f5f9a1a6a0404dea36dcc9499bcb25c9adc112b7cc9a93cae41f3262')
print('verifier blake3(b"") :', V.blake3(b'', 7).hex())
assert bad == 0
