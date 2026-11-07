#!/usr/bin/env python3
"""Check GPU step records (sample.bin / pass.bin) against impl/outer.py scalar step CO and the raw automata:
Y9, omega, fq(Y9), fe(omega) equal; special records (mode 1/2) have X13 = D1.d1 = 0. Usage: verify.py file.bin [...]"""
import os, struct, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "impl"))
import outer
REC = struct.Struct("<14IQ")
raw, _, _ = outer.build_tables()

def records(path, limit=None):
    with open(path, "rb") as f:
        data = f.read()
    n = len(data) // REC.size
    if limit:
        n = min(n, limit)
    for i in range(n):
        yield REC.unpack_from(data, i * REC.size)

def check(path, limit=None):
    n = bad = spc = spc_bad = 0
    for r in records(path, limit):
        w, Y9, om, m1, m2, k, flags, base = list(r[:8]), r[8], r[9], r[10], r[11], r[12], r[13], r[14]
        v = outer.scalar_outer(w)
        ok = v["Y9"] == Y9 and v["omega"] == om and outer.look(raw[0], Y9) == m1 and outer.look(raw[1], om) == m2
        if flags & 15:
            spc += 1
            if v["X13"] != 0 or v["D1.d1"] != 0:
                spc_bad += 1
                ok = False
        n += 1
        bad += not ok
    return {"file": os.path.basename(path), "records": n, "mismatch": bad, "special": spc, "special_not_X13_D1d1_zero": spc_bad}

if __name__ == "__main__":
    out = [check(p, 20000) for p in sys.argv[1:]]
    print(json.dumps(out))
