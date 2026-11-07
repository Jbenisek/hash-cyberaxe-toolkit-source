#!/usr/bin/env python3
"""count-cost reviewer: rule A and the listed betas on real trials in the RANGES OF THE ALGORITHM, on the processor.

    python -B count-cost_layout.py [scale, default 1.0]        (Windows Python with numpy; one thread)

Steps S1 and T are typed here from proof.md Section 4 (scalar S1, step T for arrays of members); round 1 is written
forwards from Section 1. Nothing of the package's program is imported. A sample of trials of every group is
rebuilt as real strings of 55 and 63 bytes and hashed with the organizer's verifier (hash-smash/verifier/blake3.py,
rounds = 2) and with a 2-round compression of my own: lengths, digest words 0, 2, 5, 7, Y4, h1, beta.

Groups of contexts (each context with all 524,288 members, in list order, batches of seven):
  A  seven independent random words                                   (what the package measured)
  B  the same, but vd below 2^19                                       (the range of step 2 of 6.4)
  C  layout: 16 sextuples with vd below 2^19, 128 consecutive X14 each
  D  like one run: 4 seed quadruples (S11, S4, X13, w0); for each 16 pairs (vc, vd < 2^19), 32 consecutive X14
  E  the first contexts of a run in the plainest fixed order: 2 seed quadruples, vc = 0..15, vd = 0, X14 = 0..15
Counted per context: the trials that satisfy the rule with 4, 5 and 6 conditions, the batches with a trial that
satisfies rule A (5 conditions), and the trials whose E1 has one of the 15 betas with k <= 14 that have a part
(probability 6 * 2^-11 + 9 * 2^-13 under the model).
Output: review/count-cost_layout.out and at most ten lines.
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
HERE = Path(__file__).resolve().parent
WORKSPACE = HERE.parents[2]
U = np.uint32
M = 0xFFFFFFFF
IV = (0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19)
PERM = (2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8)
X3, X7, X11, X15, W4, W13 = 0x29D4FA98, 0xBEE3AF28, 0x44036000, 0x40C58500, 0x97475638, 0x0007C006
K = (IV[2] + IV[6]) & M
W4B = ((((K + W4) & M) ^ 8) - K) & M
DELTA = (W4 - W4B) & M
ETA = 0x830303CF
QMASK, QVALUE = 0x03CF8303, 0x030C0303
RULES = {4: [(0x1, 0), (0x2, 1), (0x10000, 0), (0x20000, 0)]}
RULES[5] = RULES[4] + [(0xC, 1)]
RULES[6] = RULES[5] + [(0x180, 1)]
LISTED = [0x18B0E098, 0x18D0E098, 0x18B1A098, 0x18D1A098, 0x18B3E098, 0x18D3E098, 0x18D1A398, 0x19F1A098, 0x18D16398,
          0x18F1E098, 0x19F0E098, 0x19B1E098, 0x19D1E098, 0x19B0A098, 0x19D0A098]


def ror(v, n):
    return ((v >> n) | (v << (32 - n))) & M


def rol(v, n):
    return ror(v, 32 - n)


def g(a, b, c, d, x, y):
    a = (a + b + x) & M; d = ror(d ^ a, 16); c = (c + d) & M; b = ror(b ^ c, 12)
    a = (a + b + y) & M; d = ror(d ^ a, 8); c = (c + d) & M; b = ror(b ^ c, 7)
    return a, b, c, d


Y3, _, Y11, _ = g(X3, X7, X11, X15, W4, W13)
Y3B, _, Y11B, _ = g(X3, X7, X11, X15, W4B, W13)
CALLS = ((0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15), (0, 5, 10, 15), (1, 6, 11, 12), (2, 7, 8, 13), (3, 4, 9, 14))


def hash2(message):
    """Section 1: digest words, the state X after round 0 and the state Y after the column calls of round 1."""
    n = len(message)
    w = list(struct.unpack("<16I", message + bytes(64 - n)))
    v = list(IV) + list(IV[:4]) + [0, 0, n, 11]
    s, x, y = list(w), None, None
    for r in range(2):
        for i, (a, b, c, d) in enumerate(CALLS):
            if r == 1 and i == 4:
                y = list(v)
            v[a], v[b], v[c], v[d] = g(v[a], v[b], v[c], v[d], s[2 * i], s[2 * i + 1])
        if r == 0:
            x = list(v)
        s = [s[p] for p in PERM]
    return [v[i] ^ v[i + 8] for i in range(8)], x, y, w


def step_s1(vc, vd, S11, S4, X13, X14, w0):
    """Step S1, line by line as in proof.md Section 4."""
    ka = (IV[0] + IV[4] + w0) & M; kd = ror(ka, 16); kc = (IV[0] + kd) & M
    kb = ror(IV[4] ^ kc, 12)
    S8 = rol(S4, 7) ^ kb; S12 = (S8 - kc) & M; S0 = rol(S12, 8) ^ kd
    w1 = (S0 - ka - kb) & M
    X8 = (vc - vd) & M; tc = (X8 - X13) & M; td = (tc - S8) & M; tb = rol(X7, 7) ^ X8
    S7 = rol(tb, 12) ^ tc; X2 = rol(X13, 8) ^ td
    ta = (X2 - tb - W13) & M; S13 = rol(td, 16) ^ ta
    mb = rol(S7, 7) ^ S11; mc = rol(mb, 12) ^ IV[7]; md = (mc - IV[3]) & M
    S15 = (S11 - mc) & M; S3 = rol(S15, 8) ^ md; ma = rol(md, 16) ^ 11
    w6 = (ma - IV[3] - IV[7]) & M; w7 = (S3 - ma - mb) & M
    p = (K + W4) & M; q = ror(p ^ 55, 16); r = (IV[2] + q) & M
    u = ror(IV[6] ^ r, 12)
    ea = (S3 + S4) & M; eb = (X3 - ea) & M; ec = rol(eb, 12) ^ S4
    ed = rol(X14, 8) ^ X3; S9 = (ec - ed) & M; S14 = rol(ed, 16) ^ ea
    X9 = (ec + X14) & M; X4 = ror(eb ^ X9, 7)
    S10 = (r + S14) & M; S6 = ror(u ^ S10, 7); S2 = rol(S14, 8) ^ q
    w5 = (S2 - p - u) & M
    w12 = (ta - S2 - S7) & M
    nc = (S9 - S13) & M; nd = (nc - IV[1]) & M; na = rol(nd, 16)
    nb = ror(IV[5] ^ nc, 12); S1 = rol(S13, 8) ^ nd
    S5 = ror(nb ^ S9, 7); w2 = (na - IV[1] - IV[5]) & M; w3 = (S1 - na - nb) & M
    vb = ror(X4 ^ vc, 12)
    return dict(vc=vc, vd=vd, vb=vb, S0=S0, S1=S1, S2=S2, S3=S3, S4=S4, S5=S5, S6=S6, S7=S7, S8=S8, S9=S9, S10=S10, S11=S11,
                S12=S12, S13=S13, S14=S14, S15=S15, X2=X2, X4=X4, X8=X8, X9=X9, X13=X13, X14=X14,
                w=[w0, w1, w2, w3, W4, w5, w6, w7, 0, 0, 0, 0, w12, W13, 0, 0])


def aror(v, n):
    return (v >> U(n)) | (v << U(32 - n))


def arol(v, n):
    return aror(v, 32 - n)


def step_t(c, y):
    """Step T for an array y of members, as in proof.md Section 4; and round 1 forwards as far as needed."""
    w = c["w"]
    Y8 = arol(y, 7) ^ U(c["vb"]); Y12 = Y8 - U(c["vc"]); Y0 = arol(Y12, 8) ^ U(c["vd"])
    va = Y0 - U(c["vb"]) - U(w[6]); X0 = va - U(c["X4"]) - U(w[2]); X12 = U(rol(c["vd"], 16)) ^ va
    fd = U(rol(X15, 8)) ^ X0; fc = U(c["S10"]) + fd; X10 = fc + U(X15)
    fb = aror(U(c["S5"]) ^ fc, 12); X5 = aror(fb ^ X10, 7)
    fa = arol(fd, 16) ^ U(c["S15"]); w8 = fa - U(c["S0"]) - U(c["S5"]); w9 = X0 - fa - fb
    gc = U(X11) - X12; gb = aror(U(c["S6"]) ^ gc, 12); X6 = aror(gb ^ U(X11), 7)
    gd = gc - U(c["S11"]); X1 = arol(X12, 8) ^ gd
    ga = arol(gd, 16) ^ U(c["S12"]); w10 = ga - U(c["S1"]) - U(c["S6"]); w11 = X1 - ga - gb
    # round 1 forwards: C1 to its a output, C2 complete, then E3's second value and E1's beta
    qa = X1 + X5 + U(w[3]); qd = aror(U(c["X13"]) ^ qa, 16); qc = U(c["X9"]) + qd; qb = aror(X5 ^ qc, 12)
    Y1 = qa + qb + w10
    ra = U(c["X2"]) + X6 + U(w[7]); rd = aror(U(c["X14"]) ^ ra, 16); rc = X10 + rd; rb = aror(X6 ^ rc, 12)
    a2 = ra + rb + U(w[0]); Y14 = aror(rd ^ a2, 8); Y6 = aror(rb ^ (rc + Y14), 7)
    h1 = aror(Y14 ^ (U(Y3) + y), 16)
    a1 = Y1 + Y6 + U(w[12]); d1 = aror(Y12 ^ a1, 16)
    beta = aror((U(Y11) + d1) ^ (U(Y11B) + d1), 12)
    return dict(w8=w8, w9=w9, w10=w10, w11=w11, h1=h1, beta=beta)


def parity(h1, mask):
    out = np.zeros(h1.shape, dtype=np.uint32)
    for i in range(32):
        if mask >> i & 1:
            out ^= h1 >> U(i)
    return (out & U(1)).astype(bool)


def draw(tag, n):
    return list(struct.unpack("<%dI" % n, hashlib.shake_256(("count-cost layout " + tag).encode()).digest(4 * n)))


def check_trial(c, t, y, i, org):
    """One trial as real strings against the organizer's verifier and my own compression. Returns the number of failures."""
    w = list(c["w"])
    w[8], w[9], w[10], w[11] = int(t["w8"][i]), int(t["w9"][i]), int(t["w10"][i]), int(t["w11"][i])
    wb = list(w)
    wb[4], wb[5] = W4B, (w[5] + DELTA) & M
    A, B = struct.pack("<16I", *w)[:55], struct.pack("<16I", *wb)[:63]
    da, xa, ya, wa = hash2(A)
    db, xb, yb, _ = hash2(B)
    bad = 0
    bad += int(wa != w or B[55:] != bytes(8) or len(A) != 55 or len(B) != 63)
    bad += int(org(A, 2) != struct.pack("<8I", *da) or org(B, 2) != struct.pack("<8I", *db))
    bad += int(any(da[k] != db[k] for k in (0, 2, 5, 7)) or xa != xb)
    bad += int((xa[3], xa[7], xa[11], xa[15]) != (X3, X7, X11, X15))
    bad += int(ya[4] != int(y[i]) or yb[4] != int(y[i]) or ((Y3 + ya[4]) & QMASK) != QVALUE)
    bad += int(ror(ya[14] ^ ((ya[3] + ya[4]) & M), 16) != int(t["h1"][i]))
    ea = (ya[1] + ya[6] + wa[12]) & M
    ca, cb = (ya[11] + ror(ya[12] ^ ea, 16)) & M, (yb[11] + ror(yb[12] ^ ea, 16)) & M
    bad += int(ror(ca ^ cb, 12) != int(t["beta"][i]) or ya[11] != Y11 or yb[11] != Y11B or ya[3] != Y3 or yb[3] != Y3B)
    return bad


def main():
    scale = float(sys.argv[1]) if len(sys.argv) > 1 else 1.0
    spec = importlib.util.spec_from_file_location("organizer_blake3", WORKSPACE / "hash-smash" / "verifier" / "blake3.py")
    org_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(org_module)
    org = org_module.blake3
    free = [i for i in range(32) if not QMASK >> i & 1]
    size = 1 << len(free)
    k = np.arange(size, dtype=np.uint32)
    e1 = np.full(size, QVALUE, dtype=np.uint32)
    for j, i in enumerate(free):
        e1 |= ((k >> U(j)) & U(1)) << U(i)
    y = e1 - U(Y3)
    full = size // 7
    batches = full + (1 if size % 7 else 0)
    listed = np.array(LISTED, dtype=np.uint32)
    p_listed = 6 / 2 ** 11 + 9 / 2 ** 13

    def n_of(x):
        return max(1, int(round(x * scale)))

    groups = {}
    groups["A random, vd any"] = [(tuple(draw("A %d" % i, 7)), 0) for i in range(n_of(512))]
    groups["B random, vd < 2^19"] = [(tuple(v if j != 1 else v & 0x7FFFF for j, v in enumerate(draw("B %d" % i, 7))), 0) for i in range(n_of(512))]
    c_list = []
    for s in range(16):
        v = draw("C %d" % s, 7)
        v[1] &= 0x7FFFF
        c_list += [((v[0], v[1], v[2], v[3], v[4], (v[5] + i) & M, v[6]), s) for i in range(n_of(128))]
    groups["C layout, vd < 2^19, consecutive X14"] = c_list
    d_list, e_list = [], []
    for s in range(4):
        q = draw("D seed %d" % s, 4)
        for pair in range(16):
            v = draw("D %d %d" % (s, pair), 3)
            d_list += [((v[0], v[1] & 0x7FFFF, q[0], q[1], q[2], (v[2] + i) & M, q[3]), s) for i in range(n_of(32))]
    groups["D four seed quadruples, 16 pairs each, vd < 2^19"] = d_list
    for s in range(2):
        q = draw("E seed %d" % s, 4)
        e_list += [((vc, 0, q[0], q[1], q[2], x14, q[3]), s) for vc in range(16) for x14 in range(n_of(16))]
    groups["E start of a run: vc 0..15, vd 0, X14 from 0"] = e_list

    out, summary, start = [], [], time.time()
    checked = failures = 0
    with np.errstate(over="ignore"):
        for name, contexts in groups.items():
            rows = []
            for index, (seven, sub) in enumerate(contexts):
                c = step_s1(*seven)
                t = step_t(c, y)
                ok = np.ones(size, dtype=bool)
                counts, done = [], 0
                for n in (4, 5, 6):
                    for mask, value in RULES[n][done:]:
                        ok &= parity(t["h1"], mask) == bool(value)
                    done = len(RULES[n])
                    counts.append(int(ok.sum()))
                    if n == 5:
                        entered = int(ok[:full * 7].reshape(full, 7).any(axis=1).sum()) + int(ok[full * 7:].any())
                rows.append((sub, counts[0], counts[1], counts[2], entered, int(np.isin(t["beta"], listed).sum())))
                if index % max(1, len(contexts) // 6) == 0:
                    for i in (0, size - 1, int(draw("pick %s %d" % (name[0], index), 1)[0]) % size):
                        failures += check_trial(c, t, y, i, org)
                        checked += 1
            a = np.array(rows, dtype=np.float64)
            n_ctx = len(rows)
            ratio = [a[:, 1 + j] / size * 2 ** (4 + j) for j in range(3)]
            se5 = ratio[1].std(ddof=1) / math.sqrt(n_ctx)
            share = a[:, 4] / batches
            beta_sum, beta_exp = a[:, 5].sum(), n_ctx * size * p_listed
            z_beta = (beta_sum - beta_exp) / math.sqrt(beta_exp * (1 - p_listed))
            subs = sorted(set(int(x) for x in a[:, 0]))
            by_sub = [float(ratio[1][a[:, 0] == s].mean()) for s in subs]
            line = (f"{name}: contexts {n_ctx}, trials 2^{math.log2(n_ctx * size):.2f}; rule 4 / 2^-4 = {ratio[0].mean():.4f}; rule 5 / 2^-5 = "
                    f"{ratio[1].mean():.4f} (standard error between contexts {se5:.4f}; one context {ratio[1].min():.3f} to {ratio[1].max():.3f}); "
                    f"rule 6 / 2^-6 = {ratio[2].mean():.4f}; batches entering stage 2 {share.mean():.4f} (one context up to {share.max():.4f}); "
                    f"listed beta {int(beta_sum)} against {beta_exp:.0f} ({z_beta:+.2f} sd)")
            if len(subs) > 1:
                line += "; rule 5 / 2^-5 per outer choice: " + " ".join(f"{v:.3f}" for v in by_sub)
            out.append(line)
            summary.append(f"{name[:1]}: n={n_ctx} r5={ratio[1].mean():.4f}+-{se5:.4f} max={ratio[1].max():.3f} r4={ratio[0].mean():.4f} "
                           f"r6={ratio[2].mean():.4f} st2={share.mean():.4f}/{share.max():.4f} beta {z_beta:+.2f}sd"
                           + (" per outer " + "/".join(f"{v:.3f}" for v in by_sub[:4]) + ("..(%.3f to %.3f)" % (min(by_sub), max(by_sub)) if len(by_sub) > 4 else "") if len(subs) > 1 else ""))
    head = (f"count-cost_layout.py scale {scale}: Y3 {Y3:08x} Y3' {Y3B:08x} Y11 {Y11:08x} Y11' {Y11B:08x} W4' {W4B:08x}; members {size}, "
            f"batches {batches}; trials rebuilt as real strings and hashed with the organizer's verifier and my own compression: "
            f"{checked}, failed checks {failures}; {time.time() - start:.0f} s")
    (HERE / "count-cost_layout.out").write_text("\n".join([head] + out) + "\n", encoding="ascii", newline="\n")
    print(head[:330])
    for line in summary:
        print(line[:330])
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
