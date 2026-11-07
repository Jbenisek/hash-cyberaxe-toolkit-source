#!/usr/bin/env python3
"""judge7 (hostile-judge lens, review of the pkg7 draft): the share of the batches that enter stage 2 (rule A, eight
conditions, sub-class) IN THE RANGES OF THE ALGORITHM of proof.md 6.4, which the package says was never measured:
four seed words fixed for a "run", C0.d1 at the bottom and the top of 0..1,424,468, w5 and X2 at the bottom and the
top of 0..2^32-1, consecutive. One thread, numpy, CPU. Nothing of the package is written.

    python -B judge7_entry_ranges.py SEEDS [anchors per context, default 2]

Formulas: those of work/tools/entry_share.py (copied), anchored here again against the program's reference()
(complete 2-round compression of the real 55-byte message) on some members of every context.
Output: judge7_entry_ranges.txt beside this file.
"""
import hashlib
import importlib.util
import struct
import sys
import time
from pathlib import Path

import numpy as np

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
PROGRAM = HERE.parent.parent / "blake3-r2" / "experiments" / "halfsearch.py"
spec = importlib.util.spec_from_file_location("halfsearch_judge7", PROGRAM)
hs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hs)
U = np.uint32
ND = 1424469


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
    seeds = int(sys.argv[1])
    anchors = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    size, lanes, batches = hs.CLASS_SIZE, hs.LANES, hs.BATCHES
    full = size // lanes
    k = np.arange(size, dtype=np.uint32)
    e1 = np.full(size, hs.CLASS_VALUE, dtype=np.uint32)
    for j, i in enumerate(hs.CLASS_FREE):
        e1 |= ((k >> U(j)) & U(1)) << U(i)
    y4 = e1 - U(hs.Y3)
    rule = hs.RULES[8]
    d1s = list(range(8)) + list(range(ND - 8, ND))
    w5s = list(range(4)) + [0xFFFFFFFC + i for i in range(4)]
    x2s = list(range(8)) + [0xFFFFFFF8 + i for i in range(8)]
    lines = [f"PROGRAM sha256 {hashlib.sha256(PROGRAM.read_bytes()).hexdigest()}",
             f"per seed: 16 values of C0.d1 (0..7 and {ND - 8}..{ND - 1}) x 8 of w5 (0..3, 2^32-4..2^32-1) x 16 of X2 "
             f"(0..7, 2^32-8..2^32-1) = 2048 contexts, {2048 * size} trials; budget 1/32 = 0.031250; independent 0.026990"]
    tot_e = tot_p = tot_c = 0
    start = time.time()
    checked = 0
    with np.errstate(over="ignore"):
        for s in range(seeds):
            c0c, d3d, s15, s9 = struct.unpack("<4I", hashlib.shake_256(b"judge7 ranges %d" % s).digest(16))
            ent = pas = 0
            per_outer, per_ctx = [], []
            by_d1 = {}
            for d1 in d1s:
                for w5 in w5s:
                    o = hs.outer((c0c, d1, d3d, s15, s9, w5))
                    y12 = (rol(y4, 7) ^ U(o["C0.b1"])) - U(o["C0.c1"])
                    a1 = (rol(y12, 8) ^ U(o["C0.d1"])) - U(o["C0.b1"]) - U(o["w6"])
                    x12 = U(hs.rol(o["C0.d1"], 16)) ^ a1
                    x6 = ror(ror(U(o["S6"]) ^ (U(hs.X11) - x12), 12) ^ U(hs.X11), 7)
                    xa = a1 - U(o["X4"])
                    here = 0
                    for x2 in x2s:
                        v = hs.middle(o, x2)
                        x0 = xa - U(v["w2"])
                        x10 = U(v["S10"]) + (U(hs.rol(hs.X15, 8)) ^ x0) + U(hs.X15)
                        ra = U(x2) + x6 + U(v["w7"])
                        rd = ror(U(v["X14"]) ^ ra, 16)
                        rc = x10 + rd
                        rb = ror(x6 ^ rc, 12)
                        y14 = ror(rd ^ (ra + rb + U(v["w0"])), 8)
                        h1 = ror(y14 ^ e1, 16)
                        ok = np.ones(size, dtype=bool)
                        for mask, value in rule:
                            ok &= parity(h1, mask) == U(value)
                        inb = int(ok[:full * lanes].reshape(full, lanes).any(axis=1).sum()) + int(ok[full * lanes:].any())
                        pas += int(ok.sum())
                        ent += inb
                        here += inb
                        per_ctx.append(inb / batches)
                        for a in range(anchors):
                            i = struct.unpack("<I", hashlib.shake_256(b"judge7 anchor %d %d %d %d %d" % (s, d1, w5, x2, a)).digest(4))[0] % size
                            r = hs.reference(v, int(y4[i]))
                            on_h1 = all(bin(r["h1"] & mask).count("1") & 1 == value for mask, value in rule)
                            if not (r["h1"] == int(h1[i]) and r["y4"] == int(y4[i]) and r["half"] == 1 and r["words"] == 1
                                    and on_h1 == bool(ok[i]) and on_h1 == bool(hs.rule_a(r["h1"]))):
                                raise SystemExit(f"anchor differs: seed {s} d1 {d1} w5 {w5} x2 {x2} member {i}")
                            checked += 1
                    per_outer.append(here / (len(x2s) * batches))
                    by_d1.setdefault(d1 < 8, []).append(here / (len(x2s) * batches))
            n_ctx = len(per_ctx)
            lines.append(f"seed {s}: contexts {n_ctx}; trials with rule A share 2^-{-np.log2(pas / (n_ctx * size)):.4f}; batches entering "
                         f"{ent / (n_ctx * batches):.6f}; outer steps min {min(per_outer):.6f} max {max(per_outer):.6f}; contexts min "
                         f"{min(per_ctx):.6f} max {max(per_ctx):.6f}; contexts above 1/32: {sum(x > 1 / 32 for x in per_ctx)}; "
                         f"C0.d1 low {np.mean(by_d1[True]):.6f} high {np.mean(by_d1[False]):.6f}")
            tot_e, tot_p, tot_c = tot_e + ent, tot_p + pas, tot_c + n_ctx
    lines.append(f"ALL: seeds {seeds}, contexts {tot_c}, trials {tot_c * size} (2^{np.log2(tot_c * size):.2f}); rule A share of trials "
                 f"2^-{-np.log2(tot_p / (tot_c * size)):.4f}; batches entering {tot_e / (tot_c * batches):.6f} against budget 0.031250; "
                 f"anchors {checked} of {checked} equal; {time.time() - start:.0f} s")
    (HERE / "rerun_entry_ranges.txt").write_text("\n".join(lines) + "\n", encoding="ascii")
    print("\n".join(line[:300] for line in lines[2:]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
