#!/usr/bin/env python3
"""prereg_HA step 4: the preregistered decision (PREREG.txt section 6) from main_result.json, plus the hash recheck."""
import hashlib
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DELTA = 0.00135
BOUND = 3339 / 6400


def kl(x, y):
    t = 0.0
    if x > 0:
        t += x * math.log(x / y)
    if x < 1:
        t += (1 - x) * math.log((1 - x) / (1 - y))
    return t


def kl_upper(m, n, delta):
    lo, hi, tgt = m, 1.0 - 1e-15, math.log(1 / delta) / n
    while hi - lo > 1e-12:
        mid = (lo + hi) / 2
        if kl(m, mid) <= tgt:
            lo = mid
        else:
            hi = mid
    return lo


def main():
    r = json.load(open(os.path.join(HERE, "main_result.json")))
    n, k = r["n"], r["opens"]
    m = k / n
    V = m * (1 - m) * n / (n - 1)
    l2 = math.log(2 / DELTA)
    eb = m + math.sqrt(2 * V * l2 / n) + 7 * l2 / (3 * (n - 1))
    klu = kl_upper(m, n, DELTA)
    se = math.sqrt(V / n)
    want = open(os.path.join(HERE, "PREREG.sha256")).read().split()[0]
    got = hashlib.sha256(open(os.path.join(HERE, "PREREG.txt"), "rb").read()).hexdigest()
    out = {"seed64": r["seed64"], "n": n, "opens": k, "mean": m, "se": se, "eb_upper": eb, "kl_upper": klu,
           "bound": BOUND, "eb_margin": BOUND - eb, "kl_margin": BOUND - klu,
           "verdict": "SUPPORTED" if eb <= BOUND and klu <= BOUND else "NOT SUPPORTED",
           "prereg_sha256_recorded": want, "prereg_sha256_now": got, "hash_match": want == got,
           "seed64_expected": "%016x" % int.from_bytes(hashlib.sha256(b"prereg_HA 2026-10-09").digest()[:8], "big")}
    print(json.dumps(out, indent=1))
    with open(os.path.join(HERE, "decision.json"), "w") as f:
        json.dump(out, f, indent=1)


if __name__ == "__main__":
    main()
