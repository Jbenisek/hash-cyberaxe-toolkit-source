"""INIT dig Q2 (circuit side): replace ONE initial-state word v_i by 2000 random values, trace the circuit, record ops min/max and zero hits. Own code."""
import json, random, os
from b3r3lib import *
rng = random.Random(99)
out = {}
for i in range(12):
    ops = []
    for _ in range(2000):
        st = init_state()
        st[i] = rng.getrandbits(32)
        tr, _ = trace(state=st)
        ops.append(tr.ops)
    out[str(i)] = dict(min=min(ops), max=max(ops), n=len(ops), distinct=sorted(set(ops)))
json.dump(out, open(os.path.join(HERE, "init_ops.json"), "w"), indent=1)
print(out)
