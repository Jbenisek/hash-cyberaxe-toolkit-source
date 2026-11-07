"""Shared helpers for the blake3-r3 dig scan (own code). Imports the filed rho.py only as a library (own code)."""
import sys, os, re, math, hashlib
from fractions import Fraction
from math import isqrt, log2
HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(WS, "research", "blake3_r3", "candidate_blake3", "experiments"))
sys.path.insert(0, os.path.join(WS, "research", "poseidon", "pareto_clone"))
import rho
from verifier import blake3 as ref

def validate():
    out = {}
    out["empty_7r"] = ref.blake3(b"", 7).hex()
    out["empty_vector_ok"] = out["empty_7r"] == "af1349b9f5f9a1a6a0404dea36dcc9499bcb25c9adc112b7cc9a93cae41f3262"
    ok = True; n = 0
    for rounds in (7, 3):
        for s in range(200):
            m = hashlib.shake_256(b"v%d/%d" % (rounds, s)).digest(64)
            w = [int.from_bytes(m[4*i:4*i+4], "little") for i in range(16)]
            d = rho.digest_words(w, rounds=rounds)
            mine = b"".join(x.to_bytes(4, "little") for x in d)
            if mine != ref.blake3(m, rounds): ok = False
            n += 1
    out["rho_vs_verifier_64B_7r_and_3r"] = ok; out["cases"] = n
    out["packed_selftest"] = rho.selftest()
    return out

C = 638
def led(ph=595, stage1=4, U=16, loop=3, d=114, lam=Fraction(497, 1000), inflight=28, cutloss=Fraction(15, 100000),
        kappa=12, extra=64, st2=300, tmax=None, s1=32, group=False, lanes=7, events_ops=700, recov_fixed=600, ndp_scale=None):
    """Copy of rho.ledger(256) with every knob exposed. Returns dict with total ops, time_log2, memory bytes, score."""
    N = 1 << 256
    L = int(round(2.0 ** (d - 100))) * (1 << 100) if d != int(d) else (1 << int(d))
    if d != int(d):
        L = int(2.0 ** (d - 100) * (1 << 60)) << 40   # float mantissa then shift (d near 100..120 ok)
    ureq = isqrt(2 * N * lam.numerator // lam.denominator) + 2
    num, den = ureq + inflight * L + 1, cutloss.denominator
    q = -(-num * den // (den - cutloss.numerator))
    b = -(-q // lanes)
    sb = 1 << 48
    c = kappa * L
    if tmax is None:
        tmax = int(round(((1 << 14) + (1 << 11)) * (2.0 ** (114 - d))))
    e2max = 2 * b * lanes // (1 << s1) + 64
    st1 = stage1 + (1 if s1 < 32 else 0)
    if group:
        per_body = U * ph + (U + (U - 1) + 1 + 2) + loop      # U adds, U-1 ands, 1 and(B), cmp, branch
    else:
        per_body = U * (ph + st1) + loop
    main = Fraction(per_body, U) * b
    parts = dict(main=main, slices=-(-b // sb) * 100, stage2=e2max * st2, events=tmax * (events_ops + 3 * tmax),
                 recovery=(c + sb) * (ph + extra) + recov_fixed, init=2000)
    tot = sum(parts.values())
    code = 39 * 600 * U
    mem = 32 * tmax + code + 2048
    t = log2(tot / C)
    return dict(total=tot, time=t, mem=mem, score=t + max(0.0, log2(mem) - 20), parts=parts, B=b, Q=b * lanes, tmax=tmax, e2max=e2max, per_body=per_body)

BASE = None
def base():
    global BASE
    if BASE is None: BASE = led()
    return BASE
