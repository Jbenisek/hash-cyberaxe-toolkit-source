"""256-lane search driver on the bit-sliced chain step (bitslice.py): distinguished-point trails, lane insert/extract on
events and restarts, the stage-2 check, collision recovery on the packed 595-op circuit (rho.py batch / recover).

One batch = one bit-sliced step for 256 lanes.  After each batch: stage 1 (OR of the s1 low planes of word 0, one 256-bit
mask of lanes whose tested bits are zero); for each such lane, stage 2 (extract the lane, test the window below Tp); a
finished trail is looked up in the table, a new start is inserted into the lane.  Trails older than c batches are cut and
restarted.  A match of two finished trails goes to rho.recover (packed circuit, 2 lanes).

Run: python driver.py [--n22]   (the reduced instance: the rho-n22 experiment's chain at n = 22, 256-lane search)
"""
import sys
import json
import hashlib
from fractions import Fraction
from math import isqrt, ceil

import bitslice as bs
import rho

LANES, ALL, M32 = bs.LANES, bs.ALL, bs.M32
LAMBDA, KAPPA = rho.LAMBDA, rho.KAPPA


class Halt(Exception):
    pass


def plan_bs(n, s1, W, Tp, kappa=KAPPA, inflight_trails=2):
    """Budgets for the 256-lane search (reduced instances).  B batches of 256 lanes; the in-flight allowance is
    inflight_trails * 256 * L points (the 256 unfinished trails; the restated Lemma 2 for the real width is item 3)."""
    D, N = s1 + W, 1 << n
    L = Fraction(1 << D, Tp)
    ureq = isqrt(2 * N * LAMBDA.numerator // LAMBDA.denominator) + 2
    B = ceil((ureq + inflight_trails * LANES * L) / LANES)
    fb = (Tp - 1).bit_length()
    return dict(n=n, s1=s1, W=W, D=D, Tp=Tp, fb=fb, kb=min(64 - fb, n - D), L=L, N=N, B=B, Q=B * LANES,
                c=ceil(kappa * L), Sb=8, tmax=4 * (B * LANES // int(L)) + 64)


class Counters(dict):
    def __missing__(self, k):
        return 0


def stage1(planes, s1, pin):
    """Mask of lanes whose s1 low digest bits are all zero, and its operation count.  A plane stored inverted (pin = 1) holds
    the true bit complemented: lane zero iff stored 1.  nonzero = OR(positive planes) | ~AND(inverted planes)."""
    pos = [planes[j] for j in range(s1) if not pin[j]]
    neg = [planes[j] for j in range(s1) if pin[j]]
    ops, nz = 0, 0
    if pos:
        acc = pos[0]
        for q in pos[1:]:
            acc |= q
            ops += 1
        nz |= acc
    if neg:
        acc = neg[0]
        for q in neg[1:]:
            acc &= q
            ops += 1
        nz |= acc ^ ALL
        ops += 2 if pos else 1                 # the complement and the final OR (or just the complement)
    return ALL ^ nz, ops + 1                   # one more to turn nonzero into zero lanes


def search(st, p, r, cnt, ledger_hook=None):
    """One attempt with fresh random word r.  Returns (x, y) with f(x) = f(y) or None; raises Halt at a budget."""
    n, mask, pin = p["n"], p["N"] - 1, st.pin
    table, births = {}, [0] * LANES
    ts, nxt = list(range(LANES)), LANES
    planes = bs.pack_lanes([(r + t) & mask for t in ts], n, pin)
    cnt["inserts"] += LANES
    batches = 0
    while batches < p["B"]:
        planes = list(st.step(*planes))
        batches += 1
        cnt["batches"] += 1
        cnt["step_ops"] += st.ops
        hit, fo = stage1(planes, p["s1"], pin)
        cnt["filter_ops"] += fo + 2            # + compare and branch
        l = 0
        while hit:
            if hit & 1:
                cnt["stage2"] += 1
                x = bs.lane_value(planes, l, pin, n)
                cnt["extracts"] += 1
                if rho.is_dp(x, p):
                    key, length = rho.dp_key(x, p), batches - births[l]
                    cnt["finished"] += 1
                    if key in table:
                        _, t0, l0 = rho.unpack_entry(table[key])
                        cnt["recoveries"] += 1
                        res = rho.recover(p, r, (t0, l0), (ts[l], length))
                        if res is None:
                            raise Halt("recovery found no pair")
                        return res
                    if len(table) >= p["tmax"]:
                        raise Halt("table full")
                    table[key] = rho.pack_entry(key, ts[l], length)
                    ts[l], nxt, births[l] = nxt, nxt + 1, batches
                    planes = bs.set_lane(planes, l, (r + ts[l]) & mask, pin, n)
                    cnt["inserts"] += 1
            hit >>= 1
            l += 1
        if batches % p["Sb"] == 0:
            for l in range(LANES):
                if batches - births[l] >= p["c"]:
                    cnt["cut"] += 1
                    ts[l], nxt, births[l] = nxt, nxt + 1, batches
                    planes = bs.set_lane(planes, l, (r + ts[l]) & mask, pin, n)
                    cnt["inserts"] += 1
    return None


def run_trial(st, p, seed, attempts=60):
    cnt, nrec = Counters(), [0]
    orig = rho.batch

    def counting(*a):
        nrec[0] += 1
        return orig(*a)
    rho.batch = counting
    try:
        for a in range(attempts):
            cnt["attempts"] += 1
            r = int.from_bytes(hashlib.shake_256(("%s/%d" % (seed, a)).encode()).digest(32), "little") & (p["N"] - 1)
            try:
                res = search(st, p, r, cnt)
            except Halt as e:
                cnt["halt:" + str(e)] += 1
                continue
            if res is not None:
                cnt["packed_recovery_batches"] = nrec[0]
                return res, cnt
    finally:
        rho.batch = orig
    cnt["packed_recovery_batches"] = nrec[0]
    return None, cnt


def check_pair(x, y, n):
    """Distinct n-bit inputs whose complete 3-round digests agree on the low n bits (scalar chain, independent of both circuits)."""
    dx = rho.digest_words([0] * 8 + [(x >> (32 * i)) & M32 for i in range(8)])
    dy = rho.digest_words([0] * 8 + [(y >> (32 * i)) & M32 for i in range(8)])
    ix, iy = sum(dx[i] << (32 * i) for i in range(8)), sum(dy[i] << (32 * i) for i in range(8))
    m = (1 << n) - 1
    return x != y and (ix & m) == (iy & m)


def reduced(n=22, s1=2, W=1, Tp=1, trials=20, kappa=KAPPA, tag="main"):
    st = bs.Step(n)
    p = plan_bs(n, s1, W, Tp, kappa)
    ok = bad = none = 0
    tot = Counters()
    for t in range(trials):
        res, cnt = run_trial(st, p, "bs-%s-%d" % (tag, t))
        for k, v in cnt.items():
            tot[k] += v
        if res is None:
            none += 1
        elif check_pair(res[0], res[1], n):
            ok += 1
        else:
            bad += 1
    summ = dict(tag=tag, n=n, s1=s1, W=W, Tp=Tp, L=str(p["L"]), B=p["B"], Q=p["Q"], c=p["c"], step_ops=st.ops,
                step_gates=st.gates, trials=trials, pairs_ok=ok, pairs_bad=bad, no_pair=none, totals=dict(tot))
    return summ


if __name__ == "__main__":
    out = [reduced(22, 2, 1, 1, 20, tag="s2w1"), reduced(22, 3, 2, 2, 20, tag="s3w2T2"),
           reduced(22, 2, 1, 1, 6, kappa=Fraction(3, 2), tag="cuts")]
    for s in out:
        print(json.dumps(s))
