#!/usr/bin/env python3
"""prereg_HA Python reference of the gate (numpy, exc_check evaluator) and the step-2 dry comparison.
Usage: python3 ref.py seed LABEL        -> prints seed64 hex
       python3 ref.py dry GPU_DUMP.bin  -> dry checks and comparison, writes dry_result.json
"""
import hashlib
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "check")))
import exc_check  # noqa: E402  (its module level: imports outer, builds SLICE; main() is not run)
outer = exc_check.outer

U32, U64 = np.uint32, np.uint64
GAMMA = U64(0x9E3779B97F4A7C15)
DRY_LABEL = "dry"
DRY_N = 65536


def seed64(label):
    return int.from_bytes(hashlib.sha256(label.encode("utf-8")).digest()[:8], "big")


def mix(z):
    z = (z ^ (z >> U64(30))) * U64(0xBF58476D1CE4E5B9)
    z = (z ^ (z >> U64(27))) * U64(0x94D049BB133111EB)
    return z ^ (z >> U64(31))


def words(label, n):
    s = U64(seed64(label))
    i = np.arange(n, dtype=U64)
    return np.stack([(mix(s + (U64(8) * i + U64(k + 1)) * GAMMA) >> U64(32)).astype(U32) for k in range(8)], axis=1)


def rol(x, r):
    return (x << U32(r)) | (x >> U32(32 - r))


def evaluate(wd):
    """All step-CO names of the slice to w8 for the representatives, plus p, A, L, C, omega."""
    v = {o: wd[:, k] for k, o in enumerate(outer.OUTER_WORDS)}
    wrep = wd[:, 7] & U32(~0x7C00 & 0xFFFFFFFF)
    e1 = U32(outer.CLASS_VALUE) | (wrep & U32(outer.FREE_MASK))
    v["e1"] = e1
    v["Y4"] = e1 - U32(outer.Y3)
    for name, e in exc_check.SLICE:
        v[name] = exc_check.ev(e, v)
    for need in ("Y0", "C0.b1", "X4", "w2", "S15", "S0", "S5", "w8"):
        assert need in v, need
    p = v["Y0"]
    A = v["C0.b1"] + v["w6"] + v["X4"] + v["w2"]
    L = rol(U32(outer.X15), 24) ^ v["S15"]
    C = e1 - v["S0"] - v["S5"]
    omega = U32(outer.Y3) + v["Y4"] + v["w8"]
    return p, A, L, C, omega, wrep


S7 = np.zeros(128, dtype=bool)
S7[0x25:0x3F] = True
S7[0x45:0x5F] = True


def gate(p, A, L, C):
    pH = (p >> U32(16)) & U32(511)
    u = (pH.astype(np.int64) - ((A >> U32(16)) & U32(511)).astype(np.int64)) % 512
    a = u % 128
    q = (L & U32(127)).astype(np.int64)
    c = (C.astype(np.int64)) % 128
    t0 = ((a ^ q) + c) % 128
    t1 = ((((a - 1) % 128) ^ q) + c) % 128
    op = (S7[t0] | S7[t1]).astype(np.int64)
    return a, q, c, op


def uniform_fraction():
    a = np.arange(128)[:, None, None]
    q = np.arange(128)[None, :, None]
    c = np.arange(128)[None, None, :]
    t0 = ((a ^ q) + c) % 128
    t1 = ((((a - 1) % 128) ^ q) + c) % 128
    k = int((S7[t0] | S7[t1]).sum())
    return k, 128 ** 3


def dry(dump):
    wd = words(DRY_LABEL, DRY_N)
    p, A, L, C, omega, wrep = evaluate(wd)
    a, q, c, op = gate(p, A, L, C)
    # identity omega == (ROL16(p - A) XOR L) + C
    ident_bad = int(((rol(p - A, 16) ^ L) + C != omega).sum())
    # scalar_outer on the first 2000 representatives
    sc_bad = 0
    for i in range(2000):
        eight = [int(wd[i, k]) for k in range(7)] + [int(wrep[i])]
        sv = outer.scalar_outer(eight)
        sp = sv["Y0"]
        sA = (sv["C0.b1"] + sv["w6"] + sv["X4"] + sv["w2"]) & 0xFFFFFFFF
        sL = outer.rol(outer.X15, 24) ^ sv["S15"]
        sC = (sv["e1"] - sv["S0"] - sv["S5"]) & 0xFFFFFFFF
        ok = (sp, sA, sL, sC, sv["omega"]) == (int(p[i]), int(A[i]), int(L[i]), int(C[i]), int(omega[i]))
        sc_bad += not ok
    g = np.fromfile(dump, dtype=np.uint32)
    assert g.size == DRY_N, g.size
    ga, gq, gc, gop = g & 255, (g >> 8) & 255, (g >> 16) & 255, g >> 24
    mism = {"a": int((ga != a).sum()), "q": int((gq != q).sum()), "c": int((gc != c).sum()),
            "open": int((gop != op).sum())}
    any_bad = int(((ga != a) | (gq != q) | (gc != c) | (gop != op)).sum())
    k_u, n_u = uniform_fraction()
    out = {"label": DRY_LABEL, "seed64": "%016x" % seed64(DRY_LABEL), "n": DRY_N,
           "ref_opens": int(op.sum()), "ref_open_mean": float(op.mean()), "gpu_opens": int(gop.sum()),
           "mismatch_by_field": mism, "clusters_with_any_mismatch": any_bad,
           "omega_identity_failures": ident_bad, "scalar_outer_failures_of_2000": sc_bad,
           "uniform_key_open": [k_u, n_u, k_u / n_u],
           "first_words_hex": ["%08x" % int(x) for x in wd[0]],
           "pass": any_bad == 0 and ident_bad == 0 and sc_bad == 0}
    print(json.dumps(out, indent=1))
    with open(os.path.join(HERE, "dry_result.json"), "w") as f:
        json.dump(out, f, indent=1)


if __name__ == "__main__":
    np.seterr(over="ignore")
    if sys.argv[1] == "seed":
        print("%016x" % seed64(sys.argv[2]))
    elif sys.argv[1] == "dry":
        dry(sys.argv[2])
