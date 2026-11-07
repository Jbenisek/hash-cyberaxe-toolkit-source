#!/usr/bin/env python3
"""Run impl/solver.py on passing steps dumped by rates.cu. Per passing step: roots with g7=False, precheck=False
(step-intrinsic: rows = X restricted to S) and with g7=True, precheck=True (C, B uniform per step, as in rates.cu).
Usage: solver_run.py out.json N file1.bin [file2.bin ...]"""
import os, struct, sys, json, random
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "impl"))
REC = struct.Struct("<14IQ")
Y3, FREE, CVAL = 0x8127C181, 0xFC307CFC, 0x030C0303

def work(chunk):
    import solver
    solver.arrays()
    seed, recs = chunk
    rnd = random.Random(seed)
    out = []
    for (Q, W, E, X, base, k) in recs:
        y = ((CVAL | (W & FREE)) - Y3) & 0xFFFFFFFF
        a = solver.solve(Q, y, E, X=X, g7=False, precheck=False)
        b = solver.solve(Q, y, E, C=rnd.getrandbits(32), B=rnd.getrandbits(32), X=X, g7=True, precheck=True)
        out.append((len(a["roots"]), len(b["roots"]), base, k))
    return out

def load(path, n):
    with open(path, "rb") as f:
        data = f.read(n * REC.size)
    recs = []
    for i in range(len(data) // REC.size):
        r = REC.unpack_from(data, i * REC.size)
        X = r[10] & r[11] & 0x5F
        assert X
        recs.append((r[8], r[7], r[9], X, r[14], r[12]))
    return recs

def stats(vals):
    n = len(vals)
    mu = sum(vals) / n
    var = sum((v - mu) ** 2 for v in vals) / max(1, n - 1)
    return {"n": n, "roots": sum(vals), "mean": mu, "se": (var / n) ** 0.5, "share_ge1": sum(v > 0 for v in vals) / n}

if __name__ == "__main__":
    outp, N = sys.argv[1], int(sys.argv[2])
    res = {}
    with Pool(22) as pool:
        for p in sys.argv[3:]:
            recs = load(p, N)
            chunks = [(i, recs[i:i + 2000]) for i in range(0, len(recs), 2000)]
            got = [x for part in pool.map(work, chunks) for x in part]
            res[os.path.basename(p)] = {"nog7_noprecheck": stats([g[0] for g in got]),
                                        "g7_precheck_randomCB": stats([g[1] for g in got])}
            print(p, json.dumps(res[os.path.basename(p)]), flush=True)
    with open(outp, "w") as f:
        json.dump(res, f, indent=1)
