#!/usr/bin/env python3
"""Independent check of CLUSTER.md item (1): exception rate and the DEAD-representative claim.

Own numpy evaluator of outer.LINES (only the slice reaching w8), omega = Y3 + y + w8 exactly as
outer.scalar_outer; cross-checked against outer.scalar_outer on random samples. Automaton (2) =
outer.build_tables() t2 (last table AND S). alive9 from reachability over t2 (own code).
Random generator: numpy PCG64 (not SplitMix64). Usage: python exc_check.py LOG2_PAIRS SEED
"""
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "..", "impl")))
import outer  # noqa: E402

U32 = np.uint32
MASK = 0xFFFFFFFF
np.seterr(over="ignore")


def ev(e, v):
    if isinstance(e, int):
        return U32(e & MASK)
    if isinstance(e, str):
        return v[e]
    k = e[0]
    if k == "sum":
        s = None
        for t in e[1]:
            if isinstance(t, tuple) and t[0] == "neg":
                x = U32(0) - ev(t[1], v)
            else:
                x = ev(t, v)
            s = x if s is None else s + x
        return s
    if k == "xor":
        return ev(e[1], v) ^ ev(e[2], v)
    if k == "ror":
        n = e[2] % 32
        x = ev(e[1], v)
        return x if n == 0 else (x >> U32(n)) | (x << U32(32 - n))
    raise ValueError(k)


def refs(e, out):
    if isinstance(e, str):
        out.add(e)
    elif isinstance(e, tuple):
        if e[0] == "sum":
            for t in e[1]:
                refs(t, out)
        elif e[0] == "neg":
            refs(e[1], out)
        elif e[0] in ("xor", "ror"):
            refs(e[1], out)
            if e[0] == "xor":
                refs(e[2], out)


def my_slice():
    need, keep = {"w8"}, []
    for name, e in reversed(outer.LINES):
        if name in need:
            keep.append((name, e))
            d = set()
            refs(e, d)
            need |= d
    return list(reversed(keep))


SLICE = my_slice()


def omega_of(ctx, W):
    """ctx: dict word->uint32 array, W: uint32 array (same length). Returns omega."""
    v = dict(ctx)
    e1 = U32(outer.CLASS_VALUE) | (W & U32(outer.FREE_MASK))
    v["Y4"] = e1 - U32(outer.Y3)
    v["e1"] = e1
    for name, e in SLICE:
        v[name] = ev(e, v)
    return U32(outer.Y3) + v["Y4"] + v["w8"]


def tables():
    _, _, t2 = outer.build_tables()
    T = [np.array(t, dtype=np.int64) for t in t2]
    # reachability: can a state at table p reach a nonzero final mask?
    a3 = T[3].reshape(-1, 256).any(axis=1)                      # per state of table 3
    a2 = a3[T[2] // 256].reshape(-1, 256).any(axis=1)           # per state of table 2
    a1 = a2[T[1] // 256]                                        # per (state of table 1, byte)
    alive9 = np.zeros(512, dtype=bool)
    for x in range(512):
        off1 = T[0][x & 255]
        row = a1[off1: off1 + 256]
        alive9[x] = row[(x >> 8) & 1::2].any()                  # byte b with b&1 = omega bit 8
    return T, alive9


def look(T, x):
    x = x.astype(np.int64)
    s = T[0][x & 255]
    s = T[1][s + ((x >> 8) & 255)]
    s = T[2][s + ((x >> 16) & 255)]
    return T[3][s + ((x >> 24) & 255)]


def crosscheck(rng, n=3000):
    bad = 0
    for _ in range(n):
        eight = [int(z) for z in rng.integers(0, 1 << 32, 8, dtype=np.uint64)]
        ref = outer.scalar_outer(eight)["omega"]
        ctx = {w: np.array([eight[i]], dtype=U32) for i, w in enumerate(outer.OUTER_WORDS)}
        got = int(omega_of(ctx, np.array([eight[7]], dtype=U32))[0])
        bad += (got != ref)
    return bad


def main():
    log2_pairs, seed = int(sys.argv[1]), int(sys.argv[2])
    rng = np.random.default_rng(seed)
    t0 = time.time()
    T, alive9 = tables()
    xc = crosscheck(rng)
    # cross-check look on random words vs outer.look
    _, _, t2 = outer.build_tables()
    ws = rng.integers(0, 1 << 32, 20000, dtype=np.uint64)
    look_bad = int(sum(int(a) != outer.look(t2, int(w)) for a, w in zip(look(T, ws), ws)))
    # alive9 vs brute force on a sample: a 9-bit prefix is alive iff some completion passes
    t_tab = time.time() - t0
    CPC = int(sys.argv[3]) if len(sys.argv) > 3 else 16  # clusters per context
    C = 1 << 15                   # clusters per chunk
    target = 1 << log2_pairs
    pairs = exc = dead_reps = reps = 0
    dead_pass = dead_pass_nonexc = 0
    # alive9 by sampling: dead prefixes must never pass test (2) on random completions
    comp = rng.integers(0, 1 << 23, 1 << 12, dtype=np.uint64) << np.uint64(9)
    dead_prefix_hits = sum(int((look(T, comp | np.uint64(x)) != 0).sum()) for x in range(512) if not alive9[x])
    per_bit = np.zeros(32, dtype=np.int64)
    while pairs < target:
        nctx = C // CPC
        ctx = {w: np.repeat(rng.integers(0, 1 << 32, nctx, dtype=np.uint64).astype(U32), CPC * 32)
               for w in outer.OUTER_WORDS}
        W0 = rng.integers(0, 1 << 32, C, dtype=np.uint64).astype(U32) & U32(~0x7C00 & MASK)
        W = (W0[:, None] | (np.arange(32, dtype=U32) << U32(10))[None, :]).reshape(-1)
        om = omega_of(ctx, W).reshape(C, 32)
        rep = om[:, :1]
        part = om[:, 1:]
        diff = ((part ^ rep) & U32(0x1FF)) != 0
        exc += int(diff.sum())
        per_bit[1:] += diff.sum(axis=0)
        pairs += C * 31
        reps += C
        dead = ~alive9[(rep[:, 0] & U32(0x1FF)).astype(np.int64)]
        dead_reps += int(dead.sum())
        p2 = look(T, part.reshape(-1)).reshape(C, 31) != 0
        dp = p2 & dead[:, None]
        dead_pass += int(dp.sum())
        dead_pass_nonexc += int((dp & ~diff).sum())
    out = {"seed": seed, "cpc": CPC, "pairs": pairs, "log2_pairs": float(np.log2(pairs)), "exceptions": exc,
           "rate": exc / pairs, "rate_log2": float(np.log2(exc / pairs)) if exc else None,
           "reps": reps, "dead_rep_share": dead_reps / reps,
           "alive9_count": int(alive9.sum()), "dead_partners_passing_test2": dead_pass,
           "of_which_non_exceptions": dead_pass_nonexc,
           "dead_prefix_random_completion_passes": dead_prefix_hits,
           "crosscheck_omega_mismatches_of_3000": xc, "look_mismatches_of_20000": look_bad,
           "exceptions_by_pattern": per_bit[1:].tolist(),
           "table_s": round(t_tab, 1), "total_s": round(time.time() - t0, 1)}
    print(json.dumps(out, indent=1))
    with open(os.path.join(HERE, "exc_seed%d_2e%d_cpc%d.json" % (seed, log2_pairs, CPC)), "w") as f:
        json.dump(out, f, indent=1)


if __name__ == "__main__":
    main()
