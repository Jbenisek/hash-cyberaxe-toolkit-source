#!/usr/bin/env python3
"""Reviewer, lens mathematics and cost: the C program math_rule_share.c against the real hash.

Reads lines "nine words, alpha, k, z, pass" from stdin. For each, the trial is built with the package's program,
its 60-byte message is compressed by the traced compression of math_batch.py (whose digest must be the
organizer's), and z = fifth XOR second value of C2 and rule A on the real h1 are compared with the C program's.
"""
import struct
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import math_batch as mb  # noqa: E402

n = good = passes = 0
for line in sys.stdin:
    t = line.split()
    nine, alpha, k, z, p = [int(x, 16) for x in t[:9]], int(t[9], 16), int(t[10]), int(t[11], 16), int(t[12])
    X, S, w = mb.hs.context(nine)
    y4 = mb.hs.class_member(k)
    A, B = mb.hs.messages(mb.hs.trial(X, S, w, alpha, y4)[0])
    wa, ca, da = mb.trace(A)
    ok = da == struct.unpack("<8I", mb.org.blake3(A, 2)) and ca[8]["b2"] == y4
    zr = ca[10]["a2"] ^ ca[10]["d1"]
    h1 = ca[15]["d1"]
    ok = ok and zr == z and mb.rule_a_text(h1) == bool(p)
    n += 1; good += int(ok); passes += p
print("vectors %d, the C program's z and rule A equal those of the real compression in %d; satisfy rule A %d" % (n, good, passes))
