#!/usr/bin/env python3
"""Rule A and the batches that enter stage 2, counted on real trials of the family in the order of the list.

    python -B tools/rule_share_h8.py CONTEXTS [seed text, default 1] [anchors per context, default 8]
    python -B tools/rule_share_h8.py layout QUADRUPLES PAIRS VALUES [seed text, default 1] [anchors, default 8]

Windows Python with numpy; one thread; about 0.05 s per context. Research helper, not submitted.

First form: for each of CONTEXTS contexts all seven words are drawn at random (SHAKE-256 of
"rule share h8 <seed> <i>"). Output: evidence/rule_share_h8_<CONTEXTS>_<seed>.txt.

Second form, the ranges of the algorithm (proof 6.4): QUADRUPLES sets of the four seed words (S11, S4, X13, w0);
for each of them PAIRS pairs (vc, vd) with vd below 2^19; for each pair VALUES consecutive values of X14 from a
random start. All contexts of one quadruple share the seed words, as all contexts of a run of the algorithm do,
and the contexts of one pair differ in X14 only. Output:
evidence/rule_share_h8_layout_<QUADRUPLES>x<PAIRS>x<VALUES>_<seed>.txt.

In both forms all 524,288 members of the class are tried for every context in the order of the list, as the
algorithm does: seven consecutive members are one batch, and the last batch holds the last two members (its five
spare lanes repeat the last member and add no trial). For every trial the word h1, the second value of E3 on
message A, is computed with the formulas of the trial written here once more for arrays of 32-bit words (the
nineteen lines from Y8 to E3.h1 of research/h8/design/DESIGN.txt section 5). For each of the three rules of the
program (four, five and six conditions on h1) the tool counts the trials that satisfy it and the batches in which
at least one trial does, in all and per context.

Anchors: for some members of every context, h1 of this tool is compared with the h1 that the program's
reference() takes from its complete 2-round compression of the trial's real 55-byte message, and the three rules
on it with the program's rule functions. The tool stops if an anchor differs.

The output is also printed. Its first line holds the SHA-256 of the program and of this tool. The lines RULE give
the totals; the lines SPREAD give the share of the trials per context in units of 2^-n: mean, standard deviation
between contexts, smallest and largest (the extremes of this sample, not bounds), and in the second form the means
per pair and per quadruple.

What this does not measure: trials that satisfy rule A together with R = 0; the E1 test; a whole run of the
algorithm (2^83 contexts); and the order of the algorithm, which starts every pair at X14 = 0.
"""
import hashlib
import importlib.util
import math
import struct
import sys
import time
from pathlib import Path

import numpy as np

sys.dont_write_bytecode = True
TOOLS = Path(__file__).resolve().parent
PKG = TOOLS.parent
PROGRAM = PKG / "blake3-r2" / "experiments" / "halfsearch.py"
VD_BITS = 19                                                # vd below 2^19 in the algorithm at factor 2^25 (proof 6.4)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


hs = load(PROGRAM, "halfsearch_pkg6")
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


def shake_words(text, n):
    return struct.unpack("<%dI" % n, hashlib.shake_256(text).digest(4 * n))


def main():
    args = sys.argv[1:]
    layout = args[:1] == ["layout"]
    if layout:
        quads, pairs, values = int(args[1]), int(args[2]), int(args[3])
        contexts = quads * pairs * values
        rest = args[4:]
    else:
        contexts = int(args[0])
        rest = args[1:]
    seed = rest[0] if rest else "1"
    anchors = int(rest[1]) if len(rest) > 1 else 8
    if hs.CONTEXT_WORDS != ("C0.c1", "C0.d1", "S11", "S4", "X13", "X14", "w0"):
        raise SystemExit("the context words of the program are not in the order this tool assumes")

    def stream_of(c):
        """The seven words (vc, vd, S11, S4, X13, X14, w0) of context number c."""
        if not layout:
            return shake_words(b"rule share h8 %s %d" % (seed.encode(), c), 7)
        q, r = divmod(c, pairs * values)
        p, i = divmod(r, values)
        s11, s4, x13, w0 = shake_words(b"rule share h8 layout %s quadruple %d" % (seed.encode(), q), 4)
        vc, vd, start = shake_words(b"rule share h8 layout %s pair %d %d" % (seed.encode(), q, p), 3)
        return (vc, vd % (1 << VD_BITS), s11, s4, x13, (start + i) & 0xFFFFFFFF, w0)

    size, lanes, batches = hs.CLASS_SIZE, hs.LANES, hs.BATCHES
    full = size // lanes                                     # batches with seven different members
    # the members in the order of the list: e1 has the bits of k at the free positions, Y4 = e1 - Y3
    k = np.arange(size, dtype=np.uint32)
    e1 = np.full(size, hs.CLASS_VALUE, dtype=np.uint32)
    for j, i in enumerate(hs.CLASS_FREE):
        e1 |= ((k >> U(j)) & U(1)) << U(i)
    y4 = e1 - U(hs.Y3)
    probe = [0, 1, 6, 7, size - 2, size - 1, 12345, 300000]
    if [int(y4[i]) for i in probe] != [hs.class_member(i) for i in probe]:
        raise SystemExit("the members of this tool are not those of the program")
    rules = {n: hs.RULES[n] for n in sorted(hs.RULES)}
    per_pass = {n: np.zeros(contexts, dtype=np.int64) for n in rules}
    per_enter = {n: np.zeros(contexts, dtype=np.int64) for n in rules}
    checked = 0
    start = time.time()
    with np.errstate(over="ignore"):
        for c in range(contexts):
            X, S, w, (c0b, c0c, c0d) = hs.context(stream_of(c))
            # the nineteen lines from Y8 to E3.h1
            y8 = rol(y4, 7) ^ U(c0b)
            y12 = y8 - U(c0c)
            y0 = rol(y12, 8) ^ U(c0d)
            a1 = y0 - U(c0b) - U(w[6])
            x0 = a1 - U(X[4]) - U(w[2])
            x12 = U(hs.rol(c0d, 16)) ^ a1
            dd0 = U(hs.rol(hs.X15, 8)) ^ x0
            cd1 = U(hs.X11) - x12
            cd0 = U(S[10]) + dd0
            bd1 = ror(U(S[6]) ^ cd1, 12)
            x10 = cd0 + U(hs.X15)
            x6 = ror(bd1 ^ U(hs.X11), 7)
            ra = U(X[2]) + x6 + U(w[7])
            rd = ror(U(X[14]) ^ ra, 16)
            rc = x10 + rd
            rb = ror(x6 ^ rc, 12)
            y2 = ra + rb + U(w[0])
            y14 = ror(rd ^ y2, 8)
            h1 = ror(y14 ^ e1, 16)
            ok = np.ones(size, dtype=bool)
            done = 0
            for n, rule in rules.items():                    # each rule contains the one before it
                for mask, value in rule[done:]:
                    ok &= parity(h1, mask) == U(value)
                done = len(rule)
                per_pass[n][c] = int(ok.sum())
                per_enter[n][c] = int(ok[:full * lanes].reshape(full, lanes).any(axis=1).sum()) + int(ok[full * lanes:].any())
            for a in range(anchors):
                i = struct.unpack("<I", hashlib.shake_256(b"anchor %s %d %d" % (seed.encode(), c, a)).digest(4))[0] % size
                r = hs.reference(X, S, w, (c0b, c0c, c0d), int(y4[i]))
                right = r["h1"] == int(h1[i]) and r["y4"] == int(y4[i]) and r["half"] == 1 and r["words"] == 1
                for n, rule in rules.items():
                    on_h1 = all(bin(r["h1"] & mask).count("1") & 1 == value for mask, value in rule)
                    on_tool = all(int(parity(h1[i:i + 1], mask)[0]) == value for mask, value in rule)
                    right = right and on_h1 == on_tool
                if not right:
                    raise SystemExit(f"anchor differs: context {c}, member {i}")
                checked += 1
    trials, all_batches = contexts * size, contexts * batches
    sha = hashlib.sha256(PROGRAM.read_bytes()).hexdigest()
    own = hashlib.sha256(Path(__file__).read_bytes().replace(b"\r\n", b"\n")).hexdigest()
    lines = [f"PROGRAM sha256 {sha} TOOL rule_share_h8.py sha256 {own}",
             f"contexts {contexts} (seed text {seed}), members {size}, trials {trials}, batches {all_batches} "
             f"({batches} per context, the last with two members); anchors against the complete compression of message A: "
             f"{checked} of {checked} equal; {time.time() - start:.0f} s",
             "rule: conditions | trials that satisfy it | share of the trials | as a power of two | batches with such a trial | "
             "share of the batches | 7 * share of the trials | budget of the program | largest and smallest share of the batches "
             "of one context | largest share of the trials of one context"]
    for n in rules:
        passes, entered = int(per_pass[n].sum()), int(per_enter[n].sum())
        rate = passes / trials
        hi, lo = int(per_enter[n].argmax()), int(per_enter[n].argmin())
        lines.append(f"RULE {n} | {passes} | {rate:.8f} | 2^-{-np.log2(rate):.4f} | {entered} | {entered / all_batches:.6f} | "
                     f"{7 * rate:.6f} | 1/{2 ** (n - 3)} = {1 / 2 ** (n - 3):.6f} | {per_enter[n][hi] / batches:.6f} (context {hi}) "
                     f"{per_enter[n][lo] / batches:.6f} (context {lo}) | {per_pass[n].max() / size:.8f}")
    for n in rules:
        x = per_pass[n] / size * 2 ** n                      # share of the trials of a context in units of 2^-n
        line = (f"SPREAD {n} | share of the trials of one context over 2^-{n}: mean {x.mean():.5f} | standard deviation between "
                f"contexts {x.std(ddof=1):.5f} | smallest {x.min():.4f} largest {x.max():.4f}")
        if layout:
            pm = x.reshape(quads * pairs, values).mean(axis=1)
            qm = x.reshape(quads, pairs * values).mean(axis=1)
            line += (f" | pair means: {len(pm)}, smallest {pm.min():.5f} largest {pm.max():.5f}, standard error of the mean from "
                     f"their scatter {pm.std(ddof=1) / math.sqrt(len(pm)):.5f} | quadruple means: "
                     + " ".join(f"{v:.5f}" for v in qm))
        else:
            line += f" | standard error of the mean {x.std(ddof=1) / math.sqrt(contexts):.5f}"
        lines.append(line)
    if layout:
        lines.append(f"LAYOUT quadruples of seed words (S11, S4, X13, w0) {quads} | pairs (vc, vd) per quadruple {pairs}, vd below "
                     f"2^{VD_BITS} | consecutive values of X14 per pair {values}, from a random start")
    text = "\n".join(lines) + "\n"
    name = f"rule_share_h8_layout_{quads}x{pairs}x{values}_{seed}.txt" if layout else f"rule_share_h8_{contexts}_{seed}.txt"
    (PKG / "evidence" / name).write_bytes(text.encode("ascii"))
    print("\n".join(l[:200] for l in lines[1:2] + [l for l in lines if l.startswith("RULE 5")]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
