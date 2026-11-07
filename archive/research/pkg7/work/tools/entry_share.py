#!/usr/bin/env python3
"""MEASUREMENT, not used in any budget: rule A and the batches that enter stage 2, on real trials in the order of the list.

    python -B work/tools/entry_share.py OUTER MIDDLE [seed text, default 1] [anchors per context, default 8]

Windows Python with numpy; one thread; CPU only. A port of tools/rule_share_h8.py of the package before this one to
the two-level trial. Research helper, not submitted.

OUTER outer steps are drawn (six words each from SHAKE-256 of "entry share <seed> <i>"), and for each of them
MIDDLE values of X2 (from SHAKE-256 of "entry share <seed> <i> <m>"). With MIDDLE = 1 every context is independent
of every other. For each context all members of the sub-class (131,072) are tried in the order of the program's list:
seven consecutive members are one batch, and the last batch holds the last four members (its three spare lanes
repeat the last member and add no trial). For every trial the word h1, the second value of E3 on message A, is
computed with the formulas of the trial written here once more for arrays of 32-bit words: the lines of the
program's member() up to X6 and C0.a1 once per outer step, then the eleven lines from X0 to E3.h1 per value of X2.
For each of the three rules of the program (four, six and eight conditions on h1) the tool counts the trials that
satisfy it and the batches in which at least one trial does, in all, per context and per outer step.

Anchors: for some members of every context, h1 of this tool is compared with the h1 that the program's
reference() takes from its complete 2-round compression of the trial's real 55-byte message, and the three rules
on it with the program's rules. The tool stops if an anchor differs.

The output goes to work/evidence/entry_share_<OUTER>x<MIDDLE>_<seed>.txt. Its first line holds the SHA-256 of the
program and of this tool.

What this does not measure: trials that satisfy rule A together with R = 0; the E1 test; and contexts in the
ranges of the algorithm (here all words are drawn at random; the algorithm steps w5 and X2 by one).
"""
import hashlib
import struct
import sys
import time
from pathlib import Path

import numpy as np

from common import program, sha, write

hs = program()
U = np.uint32


def ror(v, n):
    return (v >> U(n)) | (v << U(32 - n))


def rol(v, n):
    return ror(v, 32 - n)


def parity(h1, mask):
    out = np.zeros(h1.shape, dtype=np.uint32)
    for i in range(32):
        if mask >> i & 1:
            out ^= h1 >> U(i)
    return out & U(1)


def main():
    outers, middles = int(sys.argv[1]), int(sys.argv[2])
    seed = sys.argv[3] if len(sys.argv) > 3 else "1"
    anchors = int(sys.argv[4]) if len(sys.argv) > 4 else 8
    size, lanes, batches = hs.CLASS_SIZE, hs.LANES, hs.BATCHES
    full = size // lanes                                     # batches with seven different members
    k = np.arange(size, dtype=np.uint32)
    e1 = np.full(size, hs.CLASS_VALUE, dtype=np.uint32)
    for j, i in enumerate(hs.CLASS_FREE):
        e1 |= ((k >> U(j)) & U(1)) << U(i)
    y4 = e1 - U(hs.Y3)
    probe = [0, 1, 6, 7, size - 2, size - 1, 12345, size // 2 + 17]
    if [int(y4[i]) for i in probe] != [hs.class_member(i) for i in probe]:
        raise SystemExit("the members of this tool are not those of the program")
    rules = {n: hs.RULES[n] for n in sorted(hs.RULES)}
    passes = {n: 0 for n in rules}
    entered = {n: 0 for n in rules}
    largest = {n: (0.0, "") for n in rules}
    smallest = {n: (1.0, "") for n in rules}
    per_outer = {n: [] for n in rules}
    checked = 0
    start = time.time()
    with np.errstate(over="ignore"):
        for c in range(outers):
            six = struct.unpack("<6I", hashlib.shake_256(b"entry share %s %d" % (seed.encode(), c)).digest(24))
            o = hs.outer(six)
            # once per outer step: the lines of member() up to C0.a1 and X6
            y12 = (rol(y4, 7) ^ U(o["C0.b1"])) - U(o["C0.c1"])
            a1 = (rol(y12, 8) ^ U(o["C0.d1"])) - U(o["C0.b1"]) - U(o["w6"])
            x12 = U(hs.rol(o["C0.d1"], 16)) ^ a1
            x6 = ror(ror(U(o["S6"]) ^ (U(hs.X11) - x12), 12) ^ U(hs.X11), 7)
            xa = a1 - U(o["X4"])
            here = {n: 0 for n in rules}
            for mid in range(middles):
                x2 = struct.unpack("<I", hashlib.shake_256(b"entry share %s %d %d" % (seed.encode(), c, mid)).digest(4))[0]
                v = hs.middle(o, x2)
                # per value of X2: the eleven lines from X0 to E3.h1
                x0 = xa - U(v["w2"])
                x10 = U(v["S10"]) + (U(hs.rol(hs.X15, 8)) ^ x0) + U(hs.X15)
                ra = U(x2) + x6 + U(v["w7"])
                rd = ror(U(v["X14"]) ^ ra, 16)
                rc = x10 + rd
                rb = ror(x6 ^ rc, 12)
                y14 = ror(rd ^ (ra + rb + U(v["w0"])), 8)
                h1 = ror(y14 ^ e1, 16)
                ok = np.ones(size, dtype=bool)
                done = 0
                for n, rule in rules.items():                    # each rule contains the one before it
                    for mask, value in rule[done:]:
                        ok &= parity(h1, mask) == U(value)
                    done = len(rule)
                    in_batch = int(ok[:full * lanes].reshape(full, lanes).any(axis=1).sum()) + int(ok[full * lanes:].any())
                    passes[n] += int(ok.sum())
                    entered[n] += in_batch
                    here[n] += in_batch
                    share = in_batch / batches
                    largest[n] = max(largest[n], (share, f"{c}/{mid}"))
                    smallest[n] = min(smallest[n], (share, f"{c}/{mid}"))
                for a in range(anchors):
                    i = struct.unpack("<I", hashlib.shake_256(b"anchor %s %d %d %d" % (seed.encode(), c, mid, a)).digest(4))[0] % size
                    r = hs.reference(v, int(y4[i]))
                    right = r["h1"] == int(h1[i]) and r["y4"] == int(y4[i]) and r["half"] == 1 and r["words"] == 1
                    for n, rule in rules.items():
                        on_h1 = all(bin(r["h1"] & mask).count("1") & 1 == value for mask, value in rule)
                        on_tool = all(int(parity(h1[i:i + 1], mask)[0]) == value for mask, value in rule)
                        right = right and on_h1 == on_tool
                    if not right:
                        raise SystemExit(f"anchor differs: outer step {c}, value {mid}, member {i}")
                    checked += 1
            for n in rules:
                per_outer[n].append(here[n] / (middles * batches))
    contexts = outers * middles
    trials, all_batches = contexts * size, contexts * batches
    own = hashlib.sha256(Path(__file__).read_bytes().replace(b"\r\n", b"\n")).hexdigest()
    lines = [f"PROGRAM sha256 {sha()} TOOL entry_share.py sha256 {own}",
             "MEASUREMENT (not used in the budget of the program or of the cost table)",
             f"outer steps {outers}, values of X2 per outer step {middles} (seed text {seed}): contexts {contexts}"
             f"{', every one independent of the others' if middles == 1 else ''}; members {size}, trials {trials} "
             f"(2^{np.log2(trials):.2f}), batches {all_batches} ({batches} per context, the last with {size - full * lanes} members); anchors against "
             f"the complete compression of message A: {checked} of {checked} equal; {time.time() - start:.0f} s",
             "rule: conditions | trials that satisfy it | share of the trials | as a power of two | batches with such a trial | "
             "share of the batches | 1 - (1 - share of the trials)^7 | 7 * share of the trials | budget of the program | largest and "
             "smallest share of the batches of one context (outer step/value) | largest and smallest share of the batches of one "
             "outer step"]
    for n in rules:
        rate = passes[n] / trials
        lines.append(f"RULE {n} | {passes[n]} | {rate:.8f} | 2^-{-np.log2(rate):.4f} | {entered[n]} | {entered[n] / all_batches:.6f} | "
                     f"{1 - (1 - rate) ** 7:.6f} | {7 * rate:.6f} | 1/{2 ** (n - 3)} = {1 / 2 ** (n - 3):.6f} | {largest[n][0]:.6f} "
                     f"({largest[n][1]}) {smallest[n][0]:.6f} ({smallest[n][1]}) | {max(per_outer[n]):.6f} {min(per_outer[n]):.6f}")
    text = write(f"entry_share_{outers}x{middles}_{seed}.txt", lines)
    print("\n".join(line[:330] for line in text.split("\n")[2:]), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
