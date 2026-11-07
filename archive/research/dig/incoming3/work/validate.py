import sys, os
HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
WS=os.path.abspath(os.path.join(HERE,"..","..","..",".."))
sys.path.insert(0, os.path.join(WS,"research","poseidon","pareto_clone"))
from b3steps import *
import importlib
V=importlib.import_module("verifier.blake3")
try:
    import blake3 as pkg
except Exception:
    pkg=None
vf=lambda data,rounds: V.blake3(data,rounds)
rng=random.Random(7); ok=True
for _ in range(50):
    data=bytes(rng.getrandbits(8) for _ in range(64))
    ref=digest_words([int.from_bytes(data[4*i:4*i+4],"little") for i in range(16)],7)
    b=b"".join(w.to_bytes(4,"little") for w in ref)
    ok&= b==V.blake3(data,7)
    if pkg: ok&= b==pkg.blake3(data).digest()
print("scalar 7-round == verifier (== pip blake3: %s) on 50 random 64B:"%bool(pkg),ok)
ok3=True
for _ in range(50):
    data=bytes(rng.getrandbits(8) for _ in range(64))
    ref=digest_words([int.from_bytes(data[4*i:4*i+4],"little") for i in range(16)],3)
    ok3&= b"".join(w.to_bytes(4,"little") for w in ref)==V.blake3(data,3)
print("scalar 3-round == verifier 3-round:",ok3)
for R in (7,3):
    src,ops,by,rec,tr=build(rounds=R)
    print("rounds",R,"packed ok:",check(src,R,36,7,range(8,16),verifier=vf),"ops",ops,by)
