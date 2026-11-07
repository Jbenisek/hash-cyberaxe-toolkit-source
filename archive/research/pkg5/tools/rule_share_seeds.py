#!/usr/bin/env python3
"""Heuristic H3 over many sets of seed words, in the layout of proof.md 6.4. CPU only; needs numpy (Windows Python
here). Research helper, not submitted. Output evidence/rule_share_seeds_<SEEDS>_<LOG2_BATCHES>_<FIRST>.txt, read by
tools/pkg5_data.py.

    python -B tools/rule_share_seeds.py SEEDS LOG2_BATCHES WORKERS [FIRST]

Written by a reviewing helper agent (lens: a hostile judge) as review/judge_h3.py; this copy differs from it in this
comment and in the name of the output file. Its text follows.

H3 says that no run has a share of trials that satisfy rule A as large as 9,363 * 2^85 / 2^104 = 2^-5.807 (1.1429 times
2^-6), so that at most one eighth of the batches run stage 2. The package supports it with four runs (four sets of
seed words) of 2^38 trials in a layout that leaves X13 unrestricted and X10 random. This program takes many sets of
seed words and, for each, a random sample of batches of the run that 6.4 defines for it:

    seed words X2, X5, X6, X9 (from SHAKE-256 of the seed number), X1 = X10 = 0,
    context X12 < 2^8, X13 < 2^16, X14 any; alpha any; batch j of the 9,363 batches of the class; its seven lanes.

For every lane it computes the trial of 6.1 as far as C2 with numpy (32-bit arithmetic), h1 = ROR(Y14 XOR (Y3 + Y4), 16)
and rule A as written in 6.3. Contexts, alphas and batches are sampled, not enumerated. As a check of this file, for
the first CHECK lanes of every worker h1 is compared with halfsearch.reference(), which builds the two real messages of
the trial and compresses them in full. Output: review/judge_h3_<SEEDS>_<LOG2_BATCHES>_<FIRST>.out (one line per seed
set and a summary). Nothing of the package is written.
"""
import hashlib
import math
import struct
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np

sys.dont_write_bytecode = True
PKG = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PKG / "blake3-r2" / "experiments"))
import halfsearch as hs  # noqa: E402

U = np.uint32
CHECK = 96


def ror(v, n):
    return (v >> U(n)) | (v << U(32 - n))


def rol(v, n):
    return (v << U(n)) | (v >> U(32 - n))


def colinv(j, sb, sc, d0):
    a0, b0, c0 = U(hs.IV[j]), U(hs.IV[4 + j]), U(hs.IV[j])
    b1 = rol(sb, 7) ^ sc
    c1 = rol(b1, 12) ^ b0
    sd = sc - c1
    d1 = c1 - c0
    a1 = rol(d1, 16) ^ U(d0)
    sa = rol(sd, 8) ^ d1
    return sa, sd, a1 - a0 - b0, sa - a1 - b1


MEMBERS = None


def one_seed(args):
    number, log2_batches, check, stream = args
    global MEMBERS
    if MEMBERS is None:
        MEMBERS = np.array([hs.class_member(k) for k in range(hs.CLASS_SIZE)], dtype=U)
    x2, x5, x6, x9 = struct.unpack("<4I", hashlib.shake_256(b"judge H3 seed words %d" % number).digest(16))
    # stream 0 is the first sample of batches for this set of seed words; another stream is another, independent sample
    rng = np.random.default_rng([20261006, number] if stream == 0 else [20261006, number, stream])
    B = 1 << log2_batches
    X12 = rng.integers(0, 1 << 8, B, dtype=np.uint64).astype(U)
    X13 = rng.integers(0, 1 << 16, B, dtype=np.uint64).astype(U)
    X14 = rng.integers(0, 1 << 32, B, dtype=np.uint64).astype(U)
    alpha = rng.integers(0, 1 << 32, B, dtype=np.uint64).astype(U)
    j = rng.integers(0, hs.BATCHES, B, dtype=np.int64)
    IV = [U(v) for v in hs.IV]
    X1, X2, X5, X6, X9, X10 = U(0), U(x2), U(x5), U(x6), U(x9), U(0)
    X3, X7, X11, X15, W4, W13, K = U(hs.X3), U(hs.X7), U(hs.X11), U(hs.X15), U(hs.W4), U(hs.W13), U(hs.K)
    with np.errstate(over="ignore"):
        # step S1 of proof.md Section 4, as far as the trial and C2 need it
        a1_c2 = W4 + K
        d1_c2 = ror(a1_c2 ^ U(hs.LEN_A), 16)
        c1_c2 = d1_c2 + IV[2]
        b1_c2 = ror(c1_c2 ^ IV[6], 12)
        b1_d1 = rol(X6, 7) ^ X11
        c1_d1 = X11 - X12
        S6 = rol(b1_d1, 12) ^ c1_d1
        S10 = b1_c2 ^ rol(S6, 7)
        b1_d0 = rol(X5, 7) ^ X10
        c1_d0 = X10 - X15
        S5 = rol(b1_d0, 12) ^ c1_d0
        S14 = S10 - c1_c2
        d1_d3 = rol(X14, 8) ^ X3
        a1_d3 = rol(d1_d3, 16) ^ S14
        b1_d3 = X3 - a1_d3
        X4 = ror(b1_d3 ^ X9, 7)
        c1_d3 = X9 - X14
        S4 = rol(b1_d3, 12) ^ c1_d3
        S9 = c1_d3 - d1_d3
        S1, S13, w2, w3 = colinv(1, S5, S9, 0)
        d1_d2 = rol(X13, 8) ^ X2
        a1_d2 = rol(d1_d2, 16) ^ S13
        b1_d2 = X2 - a1_d2 - W13
        X8 = b1_d2 ^ rol(X7, 7)
        c1_d2 = X8 - X13
        S7 = rol(b1_d2, 12) ^ c1_d2
        S8 = c1_d2 - d1_d2
        S0, S12, w0, w1 = colinv(0, S4, S8, 0)
        # the D0 family and the first half of C0 (6.1), per batch
        c = alpha - X15
        d_d0 = c - S10
        x0 = rol(X15, 8) ^ d_d0
        pa = x0 + X4 + w2
        pd = ror(X12 ^ pa, 16)
        pc = X8 + pd
        pb = ror(X4 ^ pc, 12)
        # the seven lanes
        k = np.minimum(j[:, None] * hs.LANES + np.arange(hs.LANES)[None, :], hs.CLASS_SIZE - 1)
        valid = (j[:, None] * hs.LANES + np.arange(hs.LANES)[None, :]) < hs.CLASS_SIZE
        y4 = MEMBERS[k]
        col = lambda v: v[:, None]  # noqa: E731
        y8 = rol(y4, 7) ^ col(pb)
        y12 = y8 - col(pc)
        y0 = rol(y12, 8) ^ col(pd)
        w6 = y0 - col(pa) - col(pb)
        ka = IV[3] + IV[7] + w6
        kd = ror(U(11) ^ ka, 16)
        kc = IV[3] + kd
        kb = ror(IV[7] ^ kc, 12)
        s11 = col(rol(S7, 7)) ^ kb
        s15 = s11 - kc
        s3 = rol(s15, 8) ^ kd
        w7 = s3 - ka - kb
        # C2 = G(X2, X6, alpha, X14; w7, w0)
        ra = X2 + X6 + w7
        rd = ror(col(X14) ^ ra, 16)
        rc = col(alpha) + rd
        rb = ror(X6 ^ rc, 12)
        ra2 = ra + rb + col(w0)
        y14 = ror(rd ^ ra2, 8)
        h1 = ror(y14 ^ (U(hs.Y3) + y4), 16)
    b = lambda i: (h1 >> U(i)) & U(1)  # noqa: E731
    ok = (b(16) == 1) & (b(0) == b(1)) & (b(1) == b(2)) & (b(2) == b(3)) & (b(3) != b(4)) & (b(23) != b(24))
    wrong = 0
    for n in range(min(check, B)):
        i = n % hs.LANES
        X, S, w = hs.context((0, x2, x5, x6, x9, 0, int(X12[n]), int(X13[n]), int(X14[n])))
        ref = hs.reference(X, S, w, int(alpha[n]), int(y4[n, i]))
        wrong += int(ref["h1"] != int(h1[n, i]) or ref["half"] != 1 or ref["y4"] != int(y4[n, i])
                     or hs.rule_a(ref["h1"]) != bool(ok[n, i]))
    lanes = int(valid.sum())
    passing = int((ok & valid).sum())
    entered = int(ok.any(axis=1).sum())
    return number, B, lanes, passing, entered, wrong, min(check, B)


def main():
    seeds, log2_batches, workers = int(sys.argv[1]), int(sys.argv[2]), min(int(sys.argv[3]), 5)
    first = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    streams = int(sys.argv[5]) if len(sys.argv) > 5 else 0
    if streams:
        # repeat mode: SEEDS sets of seed words, and for each of them `streams` further independent samples of
        # 2^LOG2_BATCHES batches (streams 1..streams), added up per set
        jobs = [(first + n, log2_batches, 4, s) for n in range(seeds) for s in range(1, streams + 1)]
        with Pool(workers) as pool:
            parts = pool.map(one_seed, jobs, chunksize=2)
        rows = []
        for n in range(seeds):
            mine = [r for r in parts if r[0] == first + n]
            rows.append((first + n,) + tuple(sum(r[i] for r in mine) for i in range(1, 7)))
        B = streams << log2_batches
    else:
        jobs = [(first + n, log2_batches, CHECK if n < workers * 2 else 4, 0) for n in range(seeds)]
        with Pool(workers) as pool:
            rows = pool.map(one_seed, jobs, chunksize=4)
        B = 1 << log2_batches
    lanes = sum(r[2] for r in rows)
    passing = sum(r[3] for r in rows)
    entered = sum(r[4] for r in rows)
    lane_share = [r[3] / r[2] for r in rows]
    batch_share = [r[4] / r[1] for r in rows]
    p = 1 / 64
    chi = sum((r[3] - r[2] * p) ** 2 / (r[2] * p * (1 - p)) for r in rows)
    pb = entered / (len(rows) * B)
    chib = sum((r[4] - B * pb) ** 2 / (B * pb * (1 - pb)) for r in rows)
    budget_trials = hs.BATCHES * 2.0 ** 85 / 2.0 ** 104
    out = [
        "# rule_share_seeds.py: %d sets of seed words (numbers %d..%d), 2^%d sampled batches each, layout of proof.md 6.4 "
        "(X1 = X10 = 0, X12 < 2^8, X13 < 2^16)%s" % (len(rows), first, first + seeds - 1, log2_batches,
                                                     "; %d further independent samples of that size per set, added up" % streams if streams else ""),
        "SUMMARY lanes %d, satisfy rule A %d, share 2^%.4f (2^-6 expected), %.2f binomial sd from 2^-6" % (
            lanes, passing, math.log2(passing / lanes), (passing - lanes * p) / math.sqrt(lanes * p * (1 - p))),
        "SUMMARY per set of seed words, share of lanes that satisfy rule A, relative to 2^-6: smallest %.4f, largest %.4f; "
        "H3 needs it below %.4f; sets at or above that: %d; one binomial sd per set is %.4f" % (
            min(lane_share) * 64, max(lane_share) * 64, budget_trials * 64, sum(s >= budget_trials for s in lane_share),
            math.sqrt((1 - p) / (rows[0][2] * p))),
        "SUMMARY spread between sets: chi-square of the lane counts against 2^-6: %.1f on %d degrees of freedom (ratio %.3f)" % (
            chi, len(rows), chi / len(rows)),
        "SUMMARY batches %d, with a lane that satisfies rule A %d, share %.5f (independent lanes: %.5f; bound 7 * 2^-6 = "
        "0.109375; budget 0.125)" % (len(rows) * B, entered, pb, 1 - (63 / 64) ** 7),
        "SUMMARY per set, share of batches that enter stage 2: smallest %.5f, largest %.5f; sets at or above 0.125: %d; at or above "
        "0.115: %d; chi-square against the common share %.1f on %d degrees of freedom" % (
            min(batch_share), max(batch_share), sum(s >= 0.125 for s in batch_share), sum(s >= 0.115 for s in batch_share),
            chib, len(rows) - 1),
        "SUMMARY check of this file against the real messages (halfsearch.reference): %d lanes compared, %d wrong" % (
            sum(r[6] for r in rows), sum(r[5] for r in rows)),
    ]
    out += ["SEED %d batches %d lanes %d pass %d entered %d" % r[:5] for r in rows]
    name = "rule_share_seeds_%d_%d_%d%s.txt" % (seeds, log2_batches, first, "_x%d" % streams if streams else "")
    (PKG / "evidence" / name).write_text("\n".join(out) + "\n", encoding="ascii", newline="\n")
    for line in out[1:7]:
        print(line)


if __name__ == "__main__":
    main()
