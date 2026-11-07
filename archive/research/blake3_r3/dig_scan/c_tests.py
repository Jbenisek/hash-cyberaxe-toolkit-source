from common import *
import json, random, time, sys
res = {}
# ---- 1. group filter logic (own code): any lane of any of k batches has low 32 bits zero  <=>  ((AND_i (z0_i + REP*0xFFFFFFFF)) & BIT32REP) != BIT32REP
REP, M32 = rho.REP, rho.M32
BIT = REP << 32; FF = REP * M32
rng = random.Random(5)
bad = 0; trig = 0; trials = 200000
for t in range(trials):
    k = rng.choice((2, 4, 16))
    words = []
    anyzero = False
    for i in range(k):
        lanes = []
        for l in range(7):
            v = rng.getrandbits(32)
            if rng.random() < 0.02: v = 0
            if v == 0: anyzero = True
            lanes.append(v)
        words.append(rho.pack(lanes))
    w = None
    for z0 in words:
        u = z0 + FF
        w = u if w is None else (w & u)
    flag = (w & BIT) != BIT
    trig += flag
    if flag != anyzero: bad += 1
res["group_filter_logic"] = dict(trials=trials, mismatches=bad, triggered=trig)

# ---- 2. shipped search at small widths, own run: success fraction and recovery lengths
def run_n(n, attempts, seed):
    p = rho.plan(n)
    ok = halt = 0; lens = []; tables = []
    t0 = time.time()
    for a in range(attempts):
        r = int.from_bytes(hashlib.shake_256(("dig%d/%d/%d" % (seed, n, a)).encode()).digest(32), "little") & (p["N"] - 1)
        try:
            pair, cnt = rho.search(p, r)
        except rho.Halt as e:
            halt += 1; continue
        if pair is not None:
            x, y = pair
            assert x != y and rho.f_scalar(x, n) == rho.f_scalar(y, n)
            ok += 1; lens.append(cnt["batches"])
    return dict(n=n, attempts=attempts, success=ok, halts=halt, frac=ok / attempts, time_s=time.time() - t0,
                B=p["B"], mean_batches_on_success=sum(lens) / max(1, len(lens)))
res["search_n22"] = run_n(22, 1500, 1)
res["search_n32_small"] = run_n(32, 40, 2)
json.dump(res, open("c_tests.json", "w"), indent=1)
print(json.dumps(res, indent=1))
