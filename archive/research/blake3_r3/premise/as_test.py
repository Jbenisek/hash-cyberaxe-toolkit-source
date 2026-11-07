"""Algorithmic success test: the shipped search (rho.py, plan(n)) on the target chain and on an ideal function.
usage: as_test.py <rho.py dir> <n> <target|ideal> <first attempt> <count>
One attempt = one call of rho.search(plan(n), r), r from the frozen seed string below.  An attempt succeeds if
search returns a pair; target pairs are re-checked with the scalar digest, ideal pairs with the ideal function.
"""
import sys, hashlib, json, time
sys.path.insert(0, sys.argv[1])
import rho

n, cond, first, count = int(sys.argv[2]), sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
p = rho.plan(n)
mask = p["N"] - 1
M32 = rho.M32
ideal_key = [b""]


def ideal(x):
    h = hashlib.blake2b(x.to_bytes(8, "little"), digest_size=8, key=ideal_key[0])
    return int.from_bytes(h.digest(), "little") & mask


def ideal_batch(*inp):
    ys = [ideal(rho.lane_x(inp, l) & mask) for l in range(rho.LANES)]
    out = [0] * 8
    out[0] = rho.pack([y & M32 for y in ys])
    out[1] = rho.pack([y >> 32 for y in ys])
    return tuple(out)


if cond == "ideal":
    rho.batch = ideal_batch
succ = bad = halts = 0
t0 = time.time()
for a in range(first, first + count):
    seed = "PREREG-b3r3-AS/%d/%s/%d" % (n, cond, a)
    r = int.from_bytes(hashlib.shake_256(seed.encode()).digest(32), "little") & mask
    if cond == "ideal":
        ideal_key[0] = hashlib.shake_256((seed + "/key").encode()).digest(16)
    try:
        res, cnt = rho.search(p, r)
    except rho.Halt:
        halts += 1
        continue
    if res is not None:
        x, y = res
        f = (lambda v: rho.f_scalar(v, n)) if cond == "target" else ideal
        if x == y or f(x) != f(y):
            bad += 1
        else:
            succ += 1
print(json.dumps(dict(n=n, cond=cond, first=first, count=count, successes=succ, bad_pairs=bad, halts=halts,
                      seconds=round(time.time() - t0, 1))))
