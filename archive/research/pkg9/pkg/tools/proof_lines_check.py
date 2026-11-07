#!/usr/bin/env python3
"""Steps S1 and T typed again from the text of proof.md Section 4, with the names of the text, against the
experiment program and against a forward compression. Research helper, not submitted.

    python -B tools/proof_lines_check.py [trials, default 20000]

The lines below are copied from the two displays of Section 4 (step S1, step T), one Python line per line of the
text and in the same order, so that a slip in the text (a wrong sign, a wrong name, a line that uses a name before
it is assigned) shows here. For every trial it checks, with the 2-round compression of the experiment program
(compress2, written out from Section 1) and with the eight assignments of Section 2:
  - the sixteen words equal those of the program's context() and trial();
  - Lemma S: K0, K1, K2 (length 55), K3, D2, D3 map the stated inputs to the stated outputs;
  - Lemma F: D0 and D1; Lemma Y: C0 has first-half values (va, vd, vc, vb) and outputs (Y0, y, Y8, Y12);
  - the theorem of Section 5: lengths 55 and 63, the zero bytes, digest words 0, 2, 5, 7 equal, Y4 = y in A and B.
Every fourth trial has extreme context words (0 or 2^32 - 1). Writes evidence/proof_lines_check.txt.
"""
import hashlib
import importlib.util
import random
import struct
import sys
from pathlib import Path

sys.dont_write_bytecode = True
TOOLS = Path(__file__).resolve().parent
PKG = TOOLS.parent
PROGRAM = PKG / "blake3-r2" / "experiments" / "halfsearch.py"
spec = importlib.util.spec_from_file_location("halfsearch_pkg6", PROGRAM)
hs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hs)

M = 0xFFFFFFFF
IV = hs.IV
K = (IV[2] + IV[6]) & M
X3, X7, X11, X15, W4, W13 = hs.X3, hs.X7, hs.X11, hs.X15, hs.W4, hs.W13


def ROR(v, n):
    return ((v >> n) | (v << (32 - n))) & M


def ROL(v, n):
    return ROR(v, 32 - n)


def steps(A, B, C, D, x, y):
    """The eight assignments of Section 2: (a1, d1, c1, b1, a2, d2, c2, b2)."""
    a1 = (A + B + x) & M; d1 = ROR(D ^ a1, 16); c1 = (C + d1) & M; b1 = ROR(B ^ c1, 12)
    a2 = (a1 + b1 + y) & M; d2 = ROR(d1 ^ a2, 8); c2 = (c1 + d2) & M; b2 = ROR(b1 ^ c2, 7)
    return a1, d1, c1, b1, a2, d2, c2, b2


def step_s1(vc, vd, S11, S4, X13, X14, w0):
    """Step S1 as displayed in Section 4."""
    # K0, forwards from w0 and backwards from S4
    ka = (IV[0] + IV[4] + w0) & M;   kd = ROR(ka, 16);   kc = (IV[0] + kd) & M
    kb = ROR(IV[4] ^ kc, 12)
    S8 = ROL(S4, 7) ^ kb;   S12 = (S8 - kc) & M;   S0 = ROL(S12, 8) ^ kd
    w1 = (S0 - ka - kb) & M
    # D2, backwards from its outputs X7, X8, X13
    X8 = (vc - vd) & M;   tc = (X8 - X13) & M;   td = (tc - S8) & M;   tb = ROL(X7, 7) ^ X8
    S7 = ROL(tb, 12) ^ tc;   X2 = ROL(X13, 8) ^ td
    ta = (X2 - tb - W13) & M;   S13 = ROL(td, 16) ^ ta
    # K3, backwards from its outputs S7, S11
    mb = ROL(S7, 7) ^ S11;   mc = ROL(mb, 12) ^ IV[7];   md = (mc - IV[3]) & M
    S15 = (S11 - mc) & M;   S3 = ROL(S15, 8) ^ md;   ma = ROL(md, 16) ^ 11
    w6 = (ma - IV[3] - IV[7]) & M;   w7 = (S3 - ma - mb) & M
    # K2, its first four values
    p = (K + W4) & M;   q = ROR(p ^ 55, 16);   r = (IV[2] + q) & M
    u = ROR(IV[6] ^ r, 12)
    # D3 with w14 = w15 = 0, the lines that do not read X14
    ea = (S3 + S4) & M;   eb = (X3 - ea) & M;   ec = ROL(eb, 12) ^ S4
    # D3, the lines that read X14
    ed = ROL(X14, 8) ^ X3;   S9 = (ec - ed) & M;   S14 = ROL(ed, 16) ^ ea
    X9 = (ec + X14) & M;   X4 = ROR(eb ^ X9, 7)
    # K2, rest
    S10 = (r + S14) & M;   S6 = ROR(u ^ S10, 7);   S2 = ROL(S14, 8) ^ q
    w5 = (S2 - p - u) & M
    # D2, its first word
    w12 = (ta - S2 - S7) & M
    # K1, backwards from its outputs S9, S13
    nc = (S9 - S13) & M;   nd = (nc - IV[1]) & M;   na = ROL(nd, 16)
    nb = ROR(IV[5] ^ nc, 12);   S1 = ROL(S13, 8) ^ nd
    S5 = ROR(nb ^ S9, 7);   w2 = (na - IV[1] - IV[5]) & M;   w3 = (S1 - na - nb) & M
    # C0, its fourth value
    vb = ROR(X4 ^ vc, 12)
    return dict(locals())


def step_t(v, y):
    """Step T as displayed in Section 4; v holds the names of step S1."""
    vb, vc, vd, w6, X4, w2 = v["vb"], v["vc"], v["vd"], v["w6"], v["X4"], v["w2"]
    S0, S1, S5, S6, S10, S11, S12, S15 = (v[n] for n in ("S0", "S1", "S5", "S6", "S10", "S11", "S12", "S15"))
    # C0, backwards from its b output y
    Y8 = ROL(y, 7) ^ vb;   Y12 = (Y8 - vc) & M;   Y0 = ROL(Y12, 8) ^ vd
    va = (Y0 - vb - w6) & M;   X0 = (va - X4 - w2) & M;   X12 = ROL(vd, 16) ^ va
    # D0, backwards from its outputs X0, X15
    fd = ROL(X15, 8) ^ X0;   fc = (S10 + fd) & M;   X10 = (fc + X15) & M
    fb = ROR(S5 ^ fc, 12);   X5 = ROR(fb ^ X10, 7)
    fa = ROL(fd, 16) ^ S15;   w8 = (fa - S0 - S5) & M;   w9 = (X0 - fa - fb) & M
    # D1, backwards from its outputs X11, X12
    gc = (X11 - X12) & M;   gb = ROR(S6 ^ gc, 12);   X6 = ROR(gb ^ X11, 7)
    gd = (gc - S11) & M;   X1 = ROL(X12, 8) ^ gd
    ga = ROL(gd, 16) ^ S12;   w10 = (ga - S1 - S6) & M;   w11 = (X1 - ga - gb) & M
    return dict(locals())


def main():
    trials = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
    rng = random.Random(20261006)
    names = ("words equal the program's", "Lemma S: K0", "Lemma S: K1", "Lemma S: K2", "Lemma S: K3", "Lemma S: D2", "Lemma S: D3",
             "Lemma F: D0", "Lemma F: D1", "Lemma Y: C0", "theorem: lengths and zero bytes", "theorem: digest words 0, 2, 5, 7",
             "theorem: Y4 = y in A and in B", "round 0 forwards gives S and X of the text")
    good = dict.fromkeys(names, 0)
    for n in range(trials):
        seven = [rng.getrandbits(32) for _ in range(7)]
        if n % 4 == 3:
            seven = [rng.choice((0, M, x)) for x in seven]
        y = rng.getrandbits(32) if n % 2 else hs.class_member(rng.randrange(hs.CLASS_SIZE))
        v = step_s1(*seven)
        t = step_t(v, y)
        w = [v["w0"], v["w1"], v["w2"], v["w3"], W4, v["w5"], v["w6"], v["w7"], t["w8"], t["w9"], t["w10"], t["w11"],
             v["w12"], W13, 0, 0]
        S = [v[f"S{i}"] if f"S{i}" in v else seven[{11: 2, 4: 3}[i]] for i in range(16)]
        X = {2: v["X2"], 3: X3, 4: v["X4"], 7: X7, 8: v["X8"], 9: v["X9"], 11: X11, 13: seven[4], 14: seven[5], 15: X15,
             0: t["X0"], 1: t["X1"], 5: t["X5"], 6: t["X6"], 10: t["X10"], 12: t["X12"]}
        Xp, Sp, wp, c0 = hs.context(seven)
        good[names[0]] += hs.trial(Xp, Sp, wp, c0, y)[0] == w
        good[names[1]] += steps(IV[0], IV[4], IV[0], 0, w[0], w[1]) == (v["ka"], v["kd"], v["kc"], v["kb"], S[0], S[12], S[8], S[4])
        good[names[2]] += steps(IV[1], IV[5], IV[1], 0, w[2], w[3]) == (v["na"], v["nd"], v["nc"], v["nb"], S[1], S[13], S[9], S[5])
        good[names[3]] += steps(IV[2], IV[6], IV[2], 55, w[4], w[5]) == (v["p"], v["q"], v["r"], v["u"], S[2], S[14], S[10], S[6])
        good[names[4]] += steps(IV[3], IV[7], IV[3], 11, w[6], w[7]) == (v["ma"], v["md"], v["mc"], v["mb"], S[3], S[15], S[11], S[7])
        good[names[5]] += steps(S[2], S[7], S[8], S[13], w[12], w[13]) == (v["ta"], v["td"], v["tc"], v["tb"], X[2], X[13], X[8], X[7])
        good[names[6]] += steps(S[3], S[4], S[9], S[14], w[14], w[15]) == (v["ea"], v["ed"], v["ec"], v["eb"], X[3], X[14], X[9], X[4])
        good[names[7]] += steps(S[0], S[5], S[10], S[15], w[8], w[9]) == (t["fa"], t["fd"], t["fc"], t["fb"], X[0], X[15], X[10], X[5])
        good[names[8]] += steps(S[1], S[6], S[11], S[12], w[10], w[11]) == (t["ga"], t["gd"], t["gc"], t["gb"], X[1], X[12], X[11], X[6])
        good[names[9]] += steps(X[0], X[4], X[8], X[12], w[2], w[6]) == (t["va"], v["vd"], v["vc"], v["vb"], t["Y0"], t["Y12"], t["Y8"], y)
        A, B = hs.messages(w)
        (wa, da, ya), (wb, db, yb) = hs.compress2(A), hs.compress2(B)
        good[names[10]] += (len(A), len(B)) == (55, 63) and B[55:] == bytes(8) and wa == w \
            and [i for i in range(16) if wa[i] != wb[i]] == [4, 5]
        good[names[11]] += all(da[i] == db[i] for i in (0, 2, 5, 7))
        good[names[12]] += ya[4] == y == yb[4]
        # round 0 forwards, written here: columns then diagonals on the words of A with length 55
        st = list(IV) + list(IV[:4]) + [0, 0, 55, 11]
        for i, (a, b, c, d) in enumerate(((0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15))):
            st[a], st[b], st[c], st[d] = hs.g(st[a], st[b], st[c], st[d], w[2 * i], w[2 * i + 1])
        column = list(st)
        for i, (a, b, c, d) in enumerate(((0, 5, 10, 15), (1, 6, 11, 12), (2, 7, 8, 13), (3, 4, 9, 14))):
            st[a], st[b], st[c], st[d] = hs.g(st[a], st[b], st[c], st[d], w[8 + 2 * i], w[9 + 2 * i])
        good[names[13]] += column == S and st == [X[i] for i in range(16)]
    sha = hashlib.sha256(PROGRAM.read_bytes()).hexdigest()
    proof = hashlib.sha256((PKG / "src" / "proof_head.md").read_bytes()).hexdigest()
    lines = [f"PROGRAM sha256 {sha}; src/proof_head.md sha256 {proof}; python -B tools/proof_lines_check.py {trials}",
             f"steps S1 and T typed from the displays of Section 4, {trials} trials (every fourth with extreme context words, "
             f"every second with y outside the class at random):"]
    lines += [f"  {name}: {good[name]} of {trials}" for name in names]
    ok = all(good[name] == trials for name in names)
    lines.append("RESULT: " + ("all hold" if ok else "FAILED"))
    (PKG / "evidence" / "proof_lines_check.txt").write_text("\n".join(lines) + "\n", encoding="ascii", newline="\n")
    print("\n".join(lines[1:2] + [l for l in lines[2:-1] if not l.endswith(f"{trials} of {trials}")] + lines[-1:]))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
