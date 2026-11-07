#!/usr/bin/env python3
"""rule_layout_review_h8.py -- rule A on real trials over whole contexts, with an implementation typed from the
proof text. Writes evidence/rule_layout_review_h8.txt.

Written by a reviewing helper agent of this package (lens "construction") as review/construction_layout.py and
copied to tools/rule_layout_review_h8.py by the agent that applied the review: the paths, the name of the output
file and this paragraph were changed, nothing else (SHA-256 of the reviewer's file, with LF line ends:
57b74e69c116e7580f4749e99e622de9f929969b7d30bdc2569212b55d897d8b). It imports the reviewer's implementation of the text, review/construction_impl.py, as it
is. Research helper, not submitted.

Rule A with all FIVE conditions, counted over every member of the class for whole contexts, with the reviewer's
text-only implementation (construction_impl.py: step S1 scalar; step T and C2 up to z typed from proof.md 6.5 with
numpy over the 524,288 members; rule A by Lemma A (c)). Two layouts:

  A. independent random contexts (seven random 32-bit words);
  B. the layout of step 2 of proof.md 6.4: the four seed words S11, S4, X13, w0 held, pairs (vc, vd) with
     vd < 2^19, X14 through consecutive values.

Layout B is what H3 is about and what the package says has not been measured for the fifth condition.
A sample of lanes is compared with rule A read off h1 of the complete compression of the real message A.

Usage: python -B tools/rule_layout_review_h8.py [independent=1024] [x14_per_pair=1024] [seed=20261006]. CPU, one thread.
"""
import os
import random
import sys
import time

import numpy as np

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "review"))
import construction_impl as ci  # noqa: E402

u32 = np.uint32
K = np.arange(1 << 19, dtype=np.uint32)
E1 = np.full(1 << 19, ci.CVALUE, dtype=np.uint32)
for _j, _pos in enumerate(ci.FREE):
    E1 |= ((K >> u32(_j)) & u32(1)) << u32(_pos)
YMEM = E1 - u32(ci.Y3)                         # member number k
U = (YMEM << u32(7)) | (YMEM >> u32(25))       # the list of 6.5: ROL(y, 7)


def rr(x, n):
    return (x >> u32(n)) | (x << u32(32 - n))


def stage_a(c, ctx):
    """z for all members of one context (proof.md 6.5, stage A, names of step T)."""
    Y8 = U ^ u32(c.vb)
    Y12 = Y8 - u32(c.vc)
    Y0 = rr(Y12, 24) ^ u32(c.vd)
    va = Y0 - u32(c.vb) - u32(c.w6)
    X0 = va - u32(c.X4) - u32(c.w2)
    X12 = va ^ u32(ci.rol(c.vd, 16))
    fd = X0 ^ u32(ci.rol(ci.X15, 8))
    X10 = fd + u32(c.S10) + u32(ci.X15)
    gc = u32(ci.X11) - X12
    gb = rr(gc ^ u32(c.S6), 12)
    X6 = rr(gb ^ u32(ci.X11), 7)
    a1 = X6 + u32(c.X2) + u32(c.w7)
    d1 = rr(a1 ^ u32(ctx[5]), 16)
    c1 = X10 + d1
    b1 = rr(X6 ^ c1, 12)
    a2 = a1 + b1 + u32(ctx[6])
    return a2 ^ d1


def counts(ctx):
    c = ci.step_S1(*ctx)
    z = stage_a(c, ctx)
    p5 = ((z ^ ((z >> u32(1)) & u32(0x04000000))) & u32(0x07000300)) == u32(0x06000300)
    p4 = (z & u32(0x03000300)) == u32(0x02000300)
    batches = int(np.count_nonzero(p5[:524286].reshape(74898, 7).any(axis=1))) + int(p5[524286:].any())
    return c, p5, int(np.count_nonzero(p4)), int(np.count_nonzero(p5)), batches


def validate(rng, ctx, c, p5, lanes):
    """Rule A from h1 of the complete compression of message A, for some members of this context."""
    right = 0
    for _ in range(lanes):
        k = rng.getrandbits(19)
        y = ci.member(k)
        t = ci.step_T(c, y)
        w = [ctx[6], c.w1, c.w2, c.w3, ci.W4, c.w5, c.w6, c.w7, t.w8, t.w9, t.w10, t.w11, c.w12, ci.W13, 0, 0]
        _, st, calls = ci.trace(w, 55)
        right += (st["Y"][4] == y == int(YMEM[k])) and ci.rule_a_h1(calls["E3"][2][1]) == bool(p5[k])
    return right


def stat(v):
    a = np.array(v, dtype=np.float64)
    return a.mean(), a.std(ddof=1), a.min(), a.max()


def main():
    n_ind = int(sys.argv[1]) if len(sys.argv) > 1 else 1024
    n_x14 = int(sys.argv[2]) if len(sys.argv) > 2 else 1024
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 20261006
    rng = random.Random(seed)
    N = 524288
    out = ["rule_layout_review_h8.py: rule A (five conditions) over whole contexts, reviewer's implementation; seed %d"
           % seed]
    t0 = time.time()
    checked = right = 0
    s4, s5, sb = [], [], []
    for i in range(n_ind):
        ctx = tuple(rng.getrandbits(32) for _ in range(7))
        c, p5, n4, n5, nb = counts(ctx)
        s4.append(n4 / N * 16)
        s5.append(n5 / N * 32)
        sb.append(nb / 74899)
        if i < 40:
            right += validate(rng, ctx, c, p5, 250)
            checked += 250
    m4, d4, lo4, hi4 = stat(s4)
    m5, d5, lo5, hi5 = stat(s5)
    mb, db, lob, hib = stat(sb)
    out.append("lanes compared with rule A on h1 of the complete compression of the real message A: %d of %d right"
               % (right, checked))
    out.append("A. %d independent contexts, all 524,288 members each (%d trials):" % (n_ind, n_ind * N))
    out.append("   four conditions: mean share %.5f x 2^-4, per context sd %.2f%% of the mean, range %.3f to %.3f "
               "x 2^-4 (package, graphics card, 4,096 contexts: sd 6.3%%, 0.66 to 1.38)"
               % (m4, 100 * d4 / m4, lo4, hi4))
    out.append("   five conditions: mean share %.5f x 2^-5 (2^%.4f), per context sd %.2f%% of the mean, range %.3f to "
               "%.3f x 2^-5 (package, processor, 2,048 contexts: 2^-5.0030, up to 1.31)"
               % (m5, np.log2(m5 / 32), 100 * d5 / m5, lo5, hi5))
    out.append("   batches that hold a trial satisfying rule A: mean share %.4f, range %.4f to %.4f (package: 0.1216, "
               "0.0731 to 0.1654); budget 0.25" % (mb, lob, hib))
    # B. the layout of step 2 of 6.4
    out.append("B. layout of 6.4: seed words held, vd < 2^19, %d consecutive values of X14 per pair (vc, vd):" % n_x14)
    means5, means4 = [], []
    for s in range(2):
        seeds = tuple(rng.getrandbits(32) for _ in range(4))        # S11, S4, X13, w0
        for p in range(3):
            vc, vd, x0 = rng.getrandbits(32), rng.getrandbits(19), rng.getrandbits(32)
            r4, r5, rb = [], [], []
            for i in range(n_x14):
                ctx = (vc, vd, seeds[0], seeds[1], seeds[2], (x0 + i) & 0xFFFFFFFF, seeds[3])
                c, p5, n4, n5, nb = counts(ctx)
                r4.append(n4 / N * 16)
                r5.append(n5 / N * 32)
                rb.append(nb / 74899)
            a4, a5, ab = stat(r4), stat(r5), stat(rb)
            means4.append(a4[0])
            means5.append(a5[0])
            out.append("   seed set %d pair %d: five conditions mean %.5f x 2^-5 (sd between contexts %.2f%%, range "
                       "%.3f to %.3f); four conditions mean %.5f x 2^-4; batches entering stage 2 %.4f (max %.4f)"
                       % (s + 1, p + 1, a5[0], 100 * a5[1] / a5[0], a5[2], a5[3], a4[0], ab[0], ab[3]))
    g5 = stat(means5)
    out.append("   the six pair means, five conditions: %.5f to %.5f x 2^-5, sd %.3f%%; expected from the "
               "between-context sd of part A over %d contexts: %.3f%%; H3 budget 1.142 x 2^-5"
               % (g5[2], g5[3], 100 * g5[1] / g5[0], n_x14, 100 * d5 / m5 / np.sqrt(n_x14)))
    out.append("seconds %.0f; trials in all %d" % (time.time() - t0, (n_ind + 6 * n_x14) * N))
    with open(os.path.join(os.path.dirname(HERE), "evidence", "rule_layout_review_h8.txt"), "w", encoding="ascii", newline="\n") as f:
        f.write("\n".join(out) + "\n")
    print("\n".join(o[:330] for o in out[1:6] + out[-2:]))


if __name__ == "__main__":
    main()
