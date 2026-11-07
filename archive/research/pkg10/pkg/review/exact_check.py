#!/usr/bin/env python3
"""exact lens, pkg7 (draft): the exact part checked from the proof text.

The displays of Section 4 and Table C are READ FROM blake3-r2/proof.md (nothing of the package's code is used for
them); the two-level trial of 6.5 (lists, table build, stored words, batch with its two stages) is typed here
from the prose of 6.5; the hash is exact_blake3.py, written from the BLAKE3 specification.

    python -B exact_check.py text       displays, Table C, Lemma T2 (a) and (c) as structure
    python -B exact_check.py trials N   N outer steps, 252 lanes each, against the real 2-round hash
    python -B exact_check.py extra      any y, class outside the sub-class, blocks of the filed construction
    python -B exact_check.py program    lists, members, words and constants against the submitted program
Nothing in the package is written; the program is imported without byte code.
"""
import hashlib
import os
import re
import struct
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
PROOF = os.path.join(PKG, "blake3-r2", "proof.md")
sys.path.insert(0, HERE)
import exact_blake3 as B3  # noqa: E402

M = 0xFFFFFFFF
IV = B3.IV
# Section 3.2, typed from the text
X3, X7, X11, X15 = 0x29D4FA98, 0xBEE3AF28, 0x44036000, 0x40C58500
W4, W13 = 0x97475638, 0x0007C006
W4P = 0x97475640
Y3, Y3P, Y11, Y11P = 0x8127C181, 0x7EDF3E7E, 0x7AF77F38, 0x850000C3
DELTA = 0xFFFFFFF8
ETA = 0x830303CF
CLASS_MASK, SUB_MASK, CLASS_VAL = 0x03CF8303, 0x07EF8303, 0x030C0303
ALL = 0x4F010300
FAIL = []


def ror(x, r):
    return ((x >> r) | (x << (32 - r))) & M


def rol(x, r):
    return ror(x, 32 - r)


def note(ok, text):
    print(("ok   " if ok else "FAIL ") + text)
    if not ok:
        FAIL.append(text)


# ---------------------------------------------------------------- reading the displays
TOK = re.compile(r"\s*(ROR|ROL|XOR|[A-Za-z][A-Za-z0-9]*(?:\.[a-z][a-z0-9]*)?(?:\[\d+\])?|\d+|[()+\-,])")


class Parser:
    def __init__(self, text):
        self.t, pos, text = [], 0, text.strip()
        while pos < len(text):
            m = TOK.match(text, pos)
            if not m:
                raise ValueError("cannot read %r at %d" % (text, pos))
            self.t.append(m.group(1))
            pos = m.end()
        self.i, self.reads, self.mixed, self.numbers = 0, set(), False, []

    def peek(self):
        return self.t[self.i] if self.i < len(self.t) else None

    def eat(self, want=None):
        tok = self.peek()
        if tok is None or (want is not None and tok != want):
            raise ValueError("expected %r, found %r in %r" % (want, tok, self.t))
        self.i += 1
        return tok

    def expr(self):
        src, kinds = self.term(), set()
        while self.peek() in ("+", "-", "XOR"):
            op = self.eat()
            kinds.add("x" if op == "XOR" else "a")
            src = "((%s %s %s) & M)" % (src, {"+": "+", "-": "-", "XOR": "^"}[op], self.term())
        if len(kinds) > 1:
            self.mixed = True
        return src

    def term(self):
        tok = self.eat()
        if tok in ("ROR", "ROL"):
            self.eat("(")
            e = self.expr()
            self.eat(",")
            r = int(self.eat())
            self.eat(")")
            return "%s(%s, %d)" % (tok.lower(), e, r)
        if tok == "(":
            e = self.expr()
            self.eat(")")
            return e
        if tok.isdigit():
            self.numbers.append(int(tok))
            return tok
        self.reads.add(tok)
        return "n[%r]" % tok


MARKS = (("O", "**Step O"), ("M", "**Step M"), ("Y", "**Step Y"), ("T", "**Step T"), ("R", "*Round 1, forwards"))
EIGHT = ("C0.c1", "C0.d1", "D3.d1", "S15", "S9", "w5", "X2", "y")
SIX = EIGHT[:6]
CONST = {"IV[%d]" % i: IV[i] for i in range(8)}
CONST.update({"W4": W4, "W13": W13, "X3": X3, "X7": X7, "X11": X11, "X15": X15, "Y3": Y3, "Y11": Y11})


def read_displays():
    lines = open(PROOF, encoding="utf-8").read().split("\n")
    step, out, table = None, [], {}
    for no, line in enumerate(lines, 1):
        for name, mark in MARKS:
            if line.startswith(mark):
                step = name
        if line.startswith("These 24 lines define") or line.startswith("## 5."):
            step = None
        m = re.match(r"^\| ([KDC]\d) \|(.*)\|\s*$", line)
        if m:
            table[m.group(1)] = [c.strip() for c in m.group(2).split("|")]
        if step and line.startswith("        ") and "=" in line:
            for part in line.split(";"):
                left, right = part.split("=", 1)
                p = Parser(right)
                src = p.expr()
                if p.peek() is not None:
                    raise ValueError("line %d: text left over in %r" % (no, part))
                out.append(dict(step=step, no=no, name=left.strip(), src=src, reads=set(p.reads), mixed=p.mixed,
                                numbers=p.numbers, text=part.strip()))
    return out, table


def compile_steps(disp):
    env = {"M": M, "ror": ror, "rol": rol}
    fns = {}
    for step in "OMYTR":
        body = "".join("    n[%r] = %s\n" % (d["name"], d["src"]) for d in disp if d["step"] == step)
        exec("def f_%s(n):\n%s" % (step, body), env)
        fns[step] = env["f_" + step]
    return fns


CALLS = {  # Section 1 and the paragraph after Table C: inputs (a, b, c, d), message words, outputs (a, b, c, d)
    "K0": (("IV[0]", "IV[4]", "IV[0]", 0), ("w0", "w1"), ("S0", "S4", "S8", "S12")),
    "K1": (("IV[1]", "IV[5]", "IV[1]", 0), ("w2", "w3"), ("S1", "S5", "S9", "S13")),
    "K2": (("IV[2]", "IV[6]", "IV[2]", 55), ("W4", "w5"), ("S2", "S6", "S10", "S14")),
    "K3": (("IV[3]", "IV[7]", "IV[3]", 11), ("w6", "w7"), ("S3", "S7", "S11", "S15")),
    "D0": (("S0", "S5", "S10", "S15"), ("w8", "w9"), ("X0", "X5", "X10", "X15")),
    "D1": (("S1", "S6", "S11", "S12"), ("w10", "w11"), ("X1", "X6", "X11", "X12")),
    "D2": (("S2", "S7", "S8", "S13"), ("w12", "W13"), ("X2", "X7", "X8", "X13")),
    "D3": (("S3", "S4", "S9", "S14"), (0, 0), ("X3", "X4", "X9", "X14")),
    "C0": (("X0", "X4", "X8", "X12"), ("w2", "w6"), ("Y0", "y", "Y8", "Y12")),
    "C1": (("X1", "X5", "X9", "X13"), ("w3", "w10"), ("Y1", "Y5", "Y9", "Y13")),
    "C2": (("X2", "X6", "X10", "X14"), ("w7", "w0"), ("Y2", "Y6", "Y10", "Y14")),
}


def assignment_terms(tag):
    (A, B, C, D), (x, y), (a2, b2, c2, d2) = CALLS[tag]
    a1, d1, c1, b1 = tag + ".a1", tag + ".d1", tag + ".c1", tag + ".b1"
    return [(a1, A, B, x), (d1, D, a1), (c1, C, d1), (b1, B, c1), (a2, a1, b1, y), (d2, d1, a2), (c2, c1, d2),
            (b2, b1, c2)]


def part_text():
    disp, table = read_displays()
    by = {}
    counts = {s: sum(1 for d in disp if d["step"] == s) for s in "OMYTR"}
    note([counts[s] for s in "OMYTR"] == [29, 21, 10, 12, 24], "lines per step O, M, Y, T, round 1: %s (text: 29, 21, "
         "10, 12, 24; 96)" % [counts[s] for s in "OMYTR"])
    note(not any(d["mixed"] for d in disp), "no line mixes + or - with XOR without brackets")
    seen, bad = {}, []
    stepnames = {s: set() for s in "OMYTR"}
    for d in disp:
        nm = d["name"]
        if nm in seen or nm in EIGHT or nm in CONST or nm == "Y4":
            bad.append("assigns twice or assigns a word or constant: " + nm)
        allowed = set(CONST) | set(seen)
        if d["step"] == "O":
            allowed = set(CONST) | set(SIX) | stepnames["O"]
        elif d["step"] == "M":
            allowed = set(CONST) | set(SIX) | {"X2"} | stepnames["O"] | stepnames["M"]
        elif d["step"] == "Y":
            allowed = set(CONST) | set(SIX) | {"y"} | stepnames["O"] | stepnames["Y"]
        else:
            allowed |= set(EIGHT) | {"Y4"}
        if not d["reads"] <= allowed:
            bad.append("line %d %s reads %s" % (d["no"], nm, sorted(d["reads"] - allowed)))
        seen[nm] = d
        stepnames[d["step"]].add(nm)
        by[nm] = d
    note(not bad, "Lemma T2 (a) and (c) as structure: every line assigns a new name and reads only what its level "
         "may read" + ("" if not bad else " -- " + "; ".join(bad[:4])))
    # Table C
    cells = [(tag, k, table[tag][k]) for tag in CALLS for k in range(8)] if set(table) == set(CALLS) else []
    names = [c[2] for c in cells]
    note(len(cells) == 88 and len(set(names)) == 88, "Table C: 88 cells, 88 different names")
    rest = set(by) - set(names)
    note(rest == {"E1.a1", "E1.d1", "E1.b1", "E1.a2", "E3.h1", "E3.g1", "E3.f1", "E3.e2"},
         "the lines outside Table C are the eight of E1 and E3: %s" % sorted(rest))
    wrong = []
    for tag, k, nm in cells:
        terms = set(t for t in assignment_terms(tag)[k] if not isinstance(t, int))
        nums = sorted(t for t in assignment_terms(tag)[k] if isinstance(t, int) and t)
        d = by.get(nm)
        if d is None:
            wrong.append("%s %d: no line %s" % (tag, k + 1, nm))
        elif d["reads"] | {nm} != terms or sorted(d["numbers"]) != nums:
            wrong.append("%s %d (%s): reads %s numbers %s, assignment has %s %s" % (
                tag, k + 1, nm, sorted(d["reads"]), d["numbers"], sorted(terms), nums))
    note(not wrong, "Table C: every cell's line reads exactly the other terms of that assignment of that call"
         + ("" if not wrong else " -- " + "; ".join(wrong[:3])))
    lev = {nm: d["step"] for nm, d in by.items()}
    note([lev["w%d" % i] for i in (6, 7, 0, 1, 2, 3, 12, 8, 9, 10, 11)] == list("OOMMMMMTTTT"),
         "levels of the message words: w6 w7 outer; w0 w1 w2 w3 w12 middle; w8..w11 trial")
    s_names = sorted(n for n in by if re.fullmatch(r"S\d+", n))
    x_names = sorted((n for n in by if re.fullmatch(r"X\d+", n)), key=lambda s: int(s[1:]))
    note(len(s_names) == 14 and "S9" not in s_names and "S15" not in s_names, "fourteen S words assigned")
    note(x_names == ["X0", "X1", "X4", "X5", "X6", "X8", "X9", "X10", "X12", "X13", "X14"],
         "X words assigned: %s" % " ".join(x_names))
    # the trial lines on which E3.h1 depends
    need, todo = set(), ["E3.h1"]
    while todo:
        nm = todo.pop()
        if nm in by and nm not in need:
            need.add(nm)
            todo += list(by[nm]["reads"])
    dep = [d["name"] for d in disp if d["name"] in need and d["step"] in "TR"]
    note(dep == ["X0", "D0.d1", "D0.c1", "X10", "C2.a1", "C2.d1", "C2.c1", "C2.b1", "Y2", "Y14", "E3.h1"],
         "trial lines under E3.h1: %d (%s)" % (len(dep), " ".join(dep)))
    return disp, table, by


# ---------------------------------------------------------------- the real compression, by name
TAGS = {(0, 0): "K", (0, 1): "D", (1, 0): "C", (1, 1): "E"}
STATE = {"K": "S", "D": "X", "C": "Y", "E": "Z"}


def forward(words, n):
    out, rec = B3.trace(words, n, 2)
    f = {"w%d" % i: words[i] for i in range(16)}
    for (r, half), t in TAGS.items():
        for i in range(4):
            c = rec[(r, half, i)]
            tag, (a, b, cc, d) = "%s%d" % (t, i), c["idx"]
            v = c["vals"]
            f[tag + ".a1"], f[tag + ".d1"], f[tag + ".c1"], f[tag + ".b1"] = v[:4]
            f[tag + ".a2"], f[tag + ".d2"], f[tag + ".c2"], f[tag + ".b2"] = v[4:]
            s = STATE[t]
            f["%s%d" % (s, a)], f["%s%d" % (s, d)], f["%s%d" % (s, cc)], f["%s%d" % (s, b)] = v[4:]
            f[tag + ".xy"] = c["xy"]
    f["E3.h1"], f["E3.g1"], f["E3.f1"], f["E3.e2"] = f["E3.d1"], f["E3.c1"], f["E3.b1"], f["E3.a2"]
    f["states"] = (rec[("state", 0, 0)], rec[("state", 0, 1)], rec[("state", 1, 0)])
    return out, f


SCHED = {"K0": (0, 1), "K1": (2, 3), "K2": (4, 5), "K3": (6, 7), "D0": (8, 9), "D1": (10, 11), "D2": (12, 13),
         "D3": (14, 15), "C0": (2, 6), "C1": (3, 10), "C2": (7, 0), "C3": (4, 13), "E0": (1, 11), "E1": (12, 5),
         "E2": (9, 14), "E3": (15, 8)}
RULE = ((0x00000001, 0), (0x00000002, 1), (0x00010000, 0), (0x00020000, 0), (0x00000404, 1), (0x00000808, 1),
        (0x01001008, 0), (0x02002040, 0))  # 6.3 as written: the bits of each condition and its right side


def rule_a(h1):
    return all(bin(h1 & m).count("1") & 1 == v for m, v in RULE)


def bit(x, i):
    return x >> i & 1


def rule_on_z(z, e1):
    """Lemma A (b) as written"""
    return (bit(z, 24) == 0 and bit(z, 25) == 1 and bit(z, 8) == 1 and bit(z, 9) == 1
            and bit(z, 26) ^ bit(z, 2) == 0 and bit(z, 27) ^ bit(z, 3) == bit(e1, 27)
            and bit(z, 27) ^ bit(z, 4) ^ bit(z, 16) == bit(e1, 28)
            and bit(z, 30) ^ bit(z, 5) ^ bit(z, 17) == 1 ^ bit(e1, 29))


def v_word(y4):
    """Lemma A (c): the word v of a member"""
    e = (Y3 + y4) & M
    return (1 << 24) | (1 << 26) | ((1 ^ bit(e, 27)) << 27) | ((1 ^ bit(e, 27) ^ bit(e, 28)) << 16) | (bit(e, 29) << 30)


FREE = [i for i in range(32) if not SUB_MASK >> i & 1]


def member(k):
    e1 = CLASS_VAL
    for j, i in enumerate(FREE):
        e1 |= (k >> j & 1) << i
    return (e1 - Y3) & M


class Counter(dict):
    def add(self, key, ok=True):
        t = self.setdefault(key, [0, 0])
        t[0] += 1
        t[1] += 0 if ok else 1


def check_trial(n, names, eight, C, in_class, in_sub):
    """n: the names of the lines for the eight words. Compares with the real hash of A and of B."""
    y = eight[7]
    words = [n["w0"], n["w1"], n["w2"], n["w3"], W4, n["w5"], n["w6"], n["w7"], n["w8"], n["w9"], n["w10"],
             n["w11"], n["w12"], W13, 0, 0]
    wb = list(words)
    wb[4], wb[5] = W4P, (n["w5"] + W4 - W4P) & M
    blka, blkb = struct.pack("<16I", *words), struct.pack("<16I", *wb)
    A, Bm = blka[:55], blkb[:63]
    C.add("bytes 55..63 of both blocks zero", blka[55:] == bytes(9) and blkb[55:] == bytes(9))
    oa, fa = forward(words, 55)
    ob, fb = forward(wb, 63)
    da, db = B3.hash(A, 2), B3.hash(Bm, 2)
    C.add("H from the bytes = the traced compression", da == struct.pack("<8I", *oa[:8])
          and db == struct.pack("<8I", *ob[:8]))
    C.add("digest words 0, 2, 5, 7 agree (Theorem of Section 5)", all(oa[i] == ob[i] for i in (0, 2, 5, 7)))
    C.add("every name of the 96 lines = its value in the compression of A (T2 b)",
          all(n[nm] == fa[nm] for nm in names))
    C.add("schedule of Section 1", all(fa[t + ".xy"] == (words[i], words[j]) for t, (i, j) in SCHED.items()))
    C.add("block admissible: w4 w13 w14 w15 and X3 X7 X11 X15", (fa["X3"], fa["X7"], fa["X11"], fa["X15"])
          == (X3, X7, X11, X15))
    C.add("the eight words read back from the compression (T2 d, injective)",
          (fa["C0.c1"], fa["C0.d1"], fa["D3.d1"], fa["S15"], fa["S9"], fa["w5"], fa["X2"], fa["Y4"]) == tuple(eight))
    sa, sb = fa["states"], fb["states"]
    C.add("B: same S and same X as A (Lemma L)", sa[0] == sb[0] and sa[1] == sb[1])
    C.add("B: Y differs from A in Y3 and Y11 only, values of Fact P", all(
        (sa[2][i] == sb[2][i]) for i in range(16) if i not in (3, 11))
        and (sa[2][3], sb[2][3], sa[2][11], sb[2][11]) == (Y3, Y3P, Y11, Y11P))
    C.add("Y4 = y in A and in B", fa["Y4"] == y and fb["Y4"] == y)
    eta = fa["E3.d1"] ^ fb["E3.d1"]
    C.add("eta = 830303cf exactly for the members of the class (Lemma Q / T)", (eta == ETA) == in_class)
    C.add("class membership by the mask of Lemma Q", (((Y3 + y) & CLASS_MASK) == CLASS_VAL) == in_class)
    beta, eps = fa["E1.b1"] ^ fb["E1.b1"], fa["E1.c2"] ^ fb["E1.c2"]
    ntrue = eps ^ rol(beta ^ eps, 1) ^ eta
    d3, d6 = oa[3] ^ ob[3], oa[6] ^ ob[6]
    C.add("Lemma N: n = D3 XOR ROL(D6, 8) (with the trial's own eta)", ntrue == d3 ^ rol(d6, 8))
    h1, z, e1 = fa["E3.d1"], n["C2.d1"] ^ n["Y2"], (Y3 + y) & M
    C.add("Lemma A (a): ROL(h1, 24) = z XOR ROL(e1, 8)", rol(h1, 24) == z ^ rol(e1, 8) and e1 == fa["E3.a1"])
    ra = rule_a(h1)
    if in_sub:
        C.add("Lemma A (b): rule A on h1 = the conditions on z", ra == rule_on_z(z, e1))
    R = (oa[1] ^ ob[1], oa[3] ^ ob[3], oa[4] ^ ob[4], oa[6] ^ ob[6])
    if R == (0, 0, 0, 0):
        print("!!! R = 0 for", [hex(x) for x in eight])
    return dict(A=A, words=words, rule=ra, n=ntrue if in_class else None, h1=h1, z=z, R=R)


# ---------------------------------------------------------------- the packed word of 6.5
LB, NL = 36, 7
WORD = (1 << 256) - 1
LANE = (1 << LB) - 1


def pack(vals):
    return sum((v & LANE) << (LB * i) for i, v in enumerate(vals))


def rep(v):
    return pack([v & M] * NL)


def lanes(w):
    return [(w >> (LB * i)) & LANE for i in range(NL)]


MM = rep(M)
AR = {r: rep((1 << (32 - r)) - 1) for r in (1, 7, 8, 12, 16, 20, 24, 25, 31)}
BR = {r: rep(((1 << r) - 1) << (32 - r)) for r in AR}


def pror(z, r):
    return ((z >> r) & AR[r]) | (((z << (32 - r)) & WORD) & BR[r])


def prol(z, r):
    return pror(z, 32 - r)


PEAK = {}


def trk(key, w):
    m = max(lanes(w))
    if m > PEAK.get(key, 0):
        PEAK[key] = m
    return w


def list_word(j):
    ys = [member(min(7 * j + i, 131071)) for i in range(NL)]
    return ys, pack(rol(y, 7) for y in ys), pack(v_word(y) for y in ys)


def build(o, U):
    """the table build of 6.5 for one list word; o: names of step O (and the six words)"""
    Y8 = U ^ rep(o["C0.b1"])
    Y12 = trk("build Y12 <2", Y8 + rep(-o["C0.c1"]))
    Y0 = prol(Y12, 8) ^ rep(o["C0.d1"])
    a1 = trk("build C0.a1 <2", Y0 + rep(-o["C0.b1"] - o["w6"]))
    XA = trk("build XA <3", a1 + rep(-o["X4"]))
    X12 = a1 ^ rep(rol(o["C0.d1"], 16))
    c1 = trk("build D1.c1 <3", (X12 ^ MM) + rep(X11 + 1))
    b1 = pror(c1 ^ rep(o["S6"]), 12)
    X6 = pror(b1 ^ rep(X11), 7)
    d1 = trk("build D1.d1 <4", c1 + rep(-o["S11"]))
    X1 = trk("build X1 <4", prol(X12, 8) ^ d1)
    return dict(Y12=Y12 & MM, XA=XA & MM, X6=X6, X1=X1 & MM, R=prol(d1, 16))


def lemma_a_word(Z):
    s = ((Z << 12) & WORD) & rep(0x0003C000)
    y = Z ^ s
    s = (s << 12) & WORD
    y = y ^ s
    s = ((y << 13) & WORD) & rep(0x40010000)
    return y ^ s


def batch(o, m, row, V):
    """6.5: stage A and stage 2 for one list word. o: names of step O; m: names after step M; row: table words."""
    X0 = trk("A X0 <2", row["XA"] + rep(-m["w2"]))
    D0d1 = X0 ^ rep(rol(X15, 8))
    X10 = trk("A X10 <3", D0d1 + rep(o["S10"] + X15))
    C2a1 = trk("A C2.a1 <2", row["X6"] + rep(m["X2"] + o["w7"]))
    C2d1 = pror(C2a1 ^ rep(o["X14"]), 16)
    C2c1 = trk("A C2.c1 <4", X10 + C2d1)
    C2b1 = pror(row["X6"] ^ C2c1, 12)
    Y2 = trk("A C2 fifth <4", C2a1 + C2b1 + rep(m["w0"]))
    z = trk("A z <4", Y2 ^ C2d1)
    yw = lemma_a_word(z)
    u = (yw ^ V) & rep(ALL)
    sm = trk("A rule sum <=1", u + rep((1 << 32) - ALL))
    flags = [w >> 32 & 1 for w in lanes(sm)]
    # stage 2
    Y14 = pror(z, 8)
    Y10 = trk("2 sum for Y6 <5", C2c1 + Y14)
    Y6 = pror(C2b1 ^ Y10, 7)
    D0c1 = trk("2 X10-X15 <4", X10 + rep(-X15))
    D0b1 = pror(D0c1 ^ rep(m["S5"]), 12)
    X5 = pror(D0b1 ^ X10, 7)
    C1a1 = trk("2 C1.a1 <3", X5 + row["X1"] + rep(m["w3"]))
    C1d1 = pror(C1a1 ^ rep(o["X13"]), 16)
    C1c1 = trk("2 C1.c1 <2", rep(o["X9"]) + C1d1)
    C1b1 = pror(X5 ^ C1c1, 12)
    D1a1 = row["R"] ^ rep(m["S12"])
    s3 = trk("2 Y1+S1+S6 <5", C1a1 + C1b1 + D1a1)
    a1 = trk("2 E1.a1 <7", s3 + Y6 + rep(m["w12"] - m["S1"] - o["S6"]))
    d1 = pror(a1 ^ row["Y12"], 16)
    c1, c1p = trk("2 E1.c1 <2", rep(Y11) + d1), trk("2 E1.c1 <2", rep(Y11P) + d1)
    b1, b1p = pror(Y6 ^ c1, 12), pror(Y6 ^ c1p, 12)
    a2 = trk("2 E1.a2 <9", a1 + b1 + rep(o["w5"]))
    a2p = trk("2 E1.a2 <9", a1 + b1p + rep(o["w5"] + DELTA))
    d2, d2p = pror(d1 ^ a2, 8), pror(d1 ^ a2p, 8)
    c2, c2p = trk("2 E1.c2 <3", c1 + d2), trk("2 E1.c2 <3", c1p + d2p)
    eps = c2 ^ c2p
    t = trk("2 beta^eps <4", b1 ^ b1p ^ eps)
    nw = (eps ^ prol(t, 1) ^ rep(ETA)) & MM
    return flags, lanes(nw), lanes(z)


def shake_words(tag, count):
    raw = hashlib.shake_256(tag.encode()).digest(4 * count)
    return list(struct.unpack("<%dI" % count, raw))


def part_trials(n_outer):
    disp, table, by = part_text()
    fn = compile_steps(disp)
    names = [d["name"] for d in disp]
    C = Counter()
    seenA, tuples = {}, set()
    lanes_done = rule_lanes = stage2_batches = batches = 0
    run4 = None
    for oi in range(n_outer):
        r = shake_words("exact outer %d" % oi, 40)
        mode = oi % 20
        if mode < 12:  # laid out as a run of 6.4: four words fixed, C0.d1 small, w5 consecutive
            if oi % 60 < 20 or run4 is None:
                if mode == 0:
                    run4 = r[:4]
            c0d1 = (0, 1, 2, 1424468, 1424467)[mode] if mode < 5 else r[5] % 1424469
            w5 = (0, 1, M, M - 1, 7, 8)[mode % 6] if mode < 6 else (r[6] if mode % 2 else (oi * 3) & M)
            six = [run4[0], c0d1, run4[1], run4[2], run4[3], w5]
        elif mode < 17:
            six = r[:6]
        else:
            six = [(0, M, r[i])[r[10 + i] % 3] for i in range(6)]
        o = dict(CONST)
        o.update(zip(SIX, six))
        fn["O"](o)
        js = list(dict.fromkeys([0, 18724] + [x % 18725 for x in r[20:30]]))
        rows, ynames = {}, {}
        for j in js:
            ys, U, V = list_word(j)
            rows[j] = (ys, build(o, U), V)
            for i, y in enumerate(ys):
                ny = dict(o)
                ny["y"] = ny["Y4"] = y
                fn["Y"](ny)
                ynames[(j, i)] = {k: ny[k] for k in ("y", "Y4") + tuple(d["name"] for d in disp if d["step"] == "Y")}
                want = (ny["Y12"], (ny["C0.a1"] - ny["X4"]) & M, ny["X6"], ny["X1"], rol(ny["D1.d1"], 16))
                got = tuple(lanes(rows[j][1][k])[i] for k in ("Y12", "XA", "X6", "X1", "R"))
                C.add("Lemma T4 (a): the five table words of a lane, each below 2^32", got == want)
        for xi, x2 in enumerate(((0, M, 1, r[30])[oi % 4], r[31], (M, 0, r[32], M - 1)[oi % 4])):
            m = dict(o)
            m["X2"] = x2
            fn["M"](m)
            for j in js:
                ys, row, V = rows[j]
                flags, nl, zl = batch(o, m, row, V)
                batches += 1
                infos = []
                for i, y in enumerate(ys):
                    n = dict(m)
                    n.update(ynames[(j, i)])
                    fn["T"](n)
                    fn["R"](n)
                    eight = tuple(six) + (x2, y)
                    info = check_trial(n, names, eight, C, True, True)
                    infos.append(info)
                    lanes_done += 1
                    C.add("stage A flag of the lane = rule A on the real h1", bool(flags[i]) == info["rule"])
                    C.add("stage 2 word of the lane = n of the real messages", nl[i] == info["n"])
                    C.add("z of the lane (low 32 bits) = C2.d1 XOR Y2", zl[i] & M == info["z"])
                    rule_lanes += info["rule"]
                    if info["A"] in seenA and seenA[info["A"]] != eight:
                        C.add("Lemma T3: different words, different A", False)
                    seenA[info["A"]] = eight
                    tuples.add(eight)
                stage2_batches += any(flags)
                C.add("T2 (c): the trials of a context differ at most in w8..w11", all(
                    [w for k, w in enumerate(f["words"]) if not 8 <= k <= 11]
                    == [w for k, w in enumerate(infos[0]["words"]) if not 8 <= k <= 11] for f in infos))
    print("outer steps %d, lanes %d, different trials %d, different messages A %d" % (
        n_outer, lanes_done, len(tuples), len(seenA)))
    note(len(tuples) == len(seenA), "Lemma T3 on the sample: as many messages A as tuples of eight words")
    for key, (cnt, wrong) in C.items():
        note(wrong == 0, "%-78s %7d cases, wrong %d" % (key, cnt, wrong))
    print("lanes that satisfy rule A: %d of %d (share %.5f, 2^-8 = %.5f); batches with one: %d of %d (%.4f)" % (
        rule_lanes, lanes_done, rule_lanes / lanes_done, 1 / 256, stage2_batches, batches, stage2_batches / batches))
    for key in sorted(PEAK):
        bound = float(key.split("<")[1].lstrip("="))
        v = PEAK[key] / 2 ** 32
        note(v <= bound if "=" in key else v < bound, "largest lane, %-22s %.4f * 2^32" % (key, v))


def part_pass(tag):
    """one complete pass of 6.4 (c) for one value of X2: the table for all 18,725 list words, then every batch"""
    disp, table = read_displays()
    fn = compile_steps(disp)
    names = [d["name"] for d in disp]
    r = shake_words("exact pass " + tag, 8)
    six = [r[0], r[1] % 1424469, r[2], r[3], r[4], r[5]]
    x2 = r[6]
    o = dict(CONST)
    o.update(zip(SIX, six))
    fn["O"](o)
    tab = []
    for j in range(18725):  # (b): the table of the outer step, before any value of X2 is known
        ys, U, V = list_word(j)
        tab.append((ys, build(o, U), V))
    m = dict(o)
    m["X2"] = x2
    fn["M"](m)
    C = Counter()
    seen, rule_lanes, entered, zero_n = set(), 0, 0, 0
    for j in range(18725):
        ys, row, V = tab[j]
        flags, nl, zl = batch(o, m, row, V)
        entered += any(flags)
        for i, y in enumerate(ys):
            n = dict(m)
            n["y"] = n["Y4"] = y
            for s in "YTR":
                fn[s](n)
            info = check_trial(n, names, tuple(six) + (x2, y), C, True, True)
            C.add("stage A flag of the lane = rule A on the real h1", bool(flags[i]) == info["rule"])
            C.add("stage 2 word of the lane = n of the real messages", nl[i] == info["n"])
            if 7 * j + i < 131072:
                seen.add(info["A"])
                rule_lanes += info["rule"]
                zero_n += info["n"] == 0
    print("context %s, X2 %08x" % (" ".join("%08x" % x for x in six), x2))
    note(len(seen) == 131072, "one pass: 18,725 batches, %d different messages A (131,072 members)" % len(seen))
    for key, (cnt, wrong) in C.items():
        note(wrong == 0, "%-78s %7d cases, wrong %d" % (key, cnt, wrong))
    print("members that satisfy rule A: %d (131,072 / 256 = 512); batches that run stage 2: %d of 18,725 = %.5f "
          "(budget 0.03125); members with n = 0: %d" % (rule_lanes, entered, entered / 18725, zero_n))


def part_extra():
    disp, table, by = part_text()
    fn = compile_steps(disp)
    names = [d["name"] for d in disp]
    C = Counter()

    def run(eight, in_class, in_sub):
        n = dict(CONST)
        n.update(zip(EIGHT, eight))
        n["Y4"] = eight[7]
        for s in "OMYTR":
            fn[s](n)
        return n, check_trial(n, names, tuple(eight), C, in_class, in_sub)

    cnt = [0, 0, 0]
    for t in range(20000):  # any eight words, extremes included: the theorem of Section 5 for all 2^256
        r = shake_words("exact any %d" % t, 16)
        eight = r[:8] if t % 4 else [(0, M, r[i], 1)[r[8 + i] % 4] for i in range(8)]
        e1 = (Y3 + eight[7]) & M
        run(eight, e1 & CLASS_MASK == CLASS_VAL, e1 & SUB_MASK == CLASS_VAL)
        cnt[0] += 1
    for t in range(12000):  # members of the class, most of them outside the sub-class
        r = shake_words("exact class %d" % t, 9)
        e1 = (r[7] & ~CLASS_MASK | CLASS_VAL) & M
        run(r[:7] + [(e1 - Y3) & M], True, e1 & SUB_MASK == CLASS_VAL)
        cnt[1] += 1
        cnt[2] += e1 & SUB_MASK == CLASS_VAL
    print("any eight words: %d; members of the class: %d (of them in the sub-class %d)" % tuple(cnt))
    for key, (c, wrong) in C.items():
        note(wrong == 0, "%-78s %7d cases, wrong %d" % (key, c, wrong))
    # onto: admissible blocks made by the FILED construction (other eight words) come back from the lines
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "filed", os.path.join(os.path.dirname(PKG), "pkg6", "blake3-r2", "experiments", "halfsearch.py"))
    filed = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(filed)
    same = total = 0
    for t in range(3000):
        r = shake_words("exact filed %d" % t, 8)
        ctx = filed.context(r[:7])
        words = filed.trial(*ctx, r[7])[0]
        out, f = forward(words, 55)
        if not ((f["X3"], f["X7"], f["X11"], f["X15"]) == (X3, X7, X11, X15) and words[4] == W4 and words[13] == W13
                and words[14] == words[15] == 0):
            continue
        eight = (f["C0.c1"], f["C0.d1"], f["D3.d1"], f["S15"], f["S9"], f["w5"], f["X2"], f["Y4"])
        n = dict(CONST)
        n.update(zip(EIGHT, eight))
        n["Y4"] = eight[7]
        for s in "OMYTR":
            fn[s](n)
        mine = [n["w0"], n["w1"], n["w2"], n["w3"], W4, n["w5"], n["w6"], n["w7"], n["w8"], n["w9"], n["w10"],
                n["w11"], n["w12"], W13, 0, 0]
        total += 1
        same += mine == list(words)
    note(total == 3000 and same == total, "T2 (d), onto: %d admissible blocks of the filed construction, read as "
         "eight words and rebuilt by the lines: %d the same block" % (total, same))


def part_program():
    import importlib.util
    spec = importlib.util.spec_from_file_location("prog", os.path.join(PKG, "blake3-r2", "experiments", "halfsearch.py"))
    hs = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(hs)
    note((hs.X3, hs.X7, hs.X11, hs.X15, hs.W4, hs.W13, hs.W4B, hs.DELTA5, hs.ETA) == (
        X3, X7, X11, X15, W4, W13, W4P, DELTA, ETA), "program: the six constants, W4', delta, eta of the text")
    note((hs.CLASS_MASK, hs.CLASS_VALUE, hs.CLASS_SIZE, hs.BATCHES) == (SUB_MASK, CLASS_VAL, 131072, 18725),
         "program: sub-class mask %08x value %08x, %d members, %d list words" % (
             hs.CLASS_MASK, hs.CLASS_VALUE, hs.CLASS_SIZE, hs.BATCHES))
    note(tuple(hs.RULE_A) == RULE, "program: RULE_A = the eight conditions of 6.3")
    note(all(hs.class_member(k) == member(k) for k in range(131072)), "program: class_member(k) = member number k of "
         "the text, all 131,072")
    bad = 0
    for j in range(18725):
        ys, U, V = list_word(j)
        pu, pm, pv = hs.list_words(j)
        bad += (pu, list(pm), pv) != (U, ys, V)
    note(bad == 0, "program: U[j], V[j] and the members of every list word = the lists typed from the text (18,725)")
    note(all(hs.rule_word(member(k)) == v_word(member(k)) for k in range(0, 131072, 7)), "program: rule_word = v")
    disp, table = read_displays()
    fn = compile_steps(disp)
    diff = 0
    for t in range(4000):
        r = shake_words("exact prog %d" % t, 8)
        y = member(r[7] % 131072)
        n = dict(CONST)
        n.update(zip(EIGHT, r[:7] + [y]))
        n["Y4"] = y
        for s in "OMYTR":
            fn[s](n)
        mine = [n["w0"], n["w1"], n["w2"], n["w3"], W4, n["w5"], n["w6"], n["w7"], n["w8"], n["w9"], n["w10"],
                n["w11"], n["w12"], W13, 0, 0]
        v = hs.context(r[:7])
        words, tv = hs.trial(v, y)
        diff += list(words) != mine or any(v[k] != n[k] for k in v) or any(tv[k] != n[k] for k in tv)
        a, b = hs.messages(words)
        diff += hs.compress2(a)[1] != list(struct.unpack("<8I", B3.hash(a, 2)))
        diff += hs.compress2(b)[1] != list(struct.unpack("<8I", B3.hash(b, 2)))
    note(diff == 0, "program: outer, middle, member, trial, messages, compress2 = the lines of the text and my hash, "
         "4,000 trials")
    # ranges and budgets, integer arithmetic
    F = 49400000
    P = -(-(1 << 110) // F)
    E = 18725 * P // 32
    vals = -(-(1 << 46) // F)
    note(vals == 1424469, "ceil(2^46 / 49,400,000) = %d (text 1,424,469)" % vals)
    note(hs.FACTOR == F and hs.RUN_PAIRS == P and hs.STAGE_2_BUDGET == E, "program: RUN_PAIRS = ceil(2^110 / F) and "
         "STAGE_2_BUDGET = floor(18,725 P / 32)")
    note(1424469 << 64 >= P and (1424468 << 64) < P, "1,424,469 * 2^64 >= P > 1,424,468 * 2^64")
    note(32 * E < 18725 * (1424469 << 64), "E is less than one part in 32 of the batches of a run")
    N = 1424469 << 81
    note(N * F >= 1 << 127 and (N - (1 << 81)) * F < 1 << 127, "N = 1,424,469 * 2^81 >= 2^127 / F; one value of "
         "C0.d1 fewer would not be")
    import math
    print("     log2 N = %.6f; log2 F = %.6f; 127 - log2 F = %.6f; N F / 2^128 = %.9f" % (
        math.log2(N), math.log2(F), 127 - math.log2(F), N * F / 2 ** 128))
    print("     log2(7.7 N / 430) = %.6f; + log2(1 + 2^-7) = %.6f (text: 95.638660 and below 95.6499)" % (
        math.log2(7.7 * N / 430), math.log2(7.7 * N / 430) + math.log2(1 + 2 ** -7)))
    Pc = 18725 * 47 + 18725 * 135 / 32 + 134 + 1 + (18725 * 74 + 260 + 8) / 2 ** 32 + 16 / 2 ** 64
    print("     work per value of X2 = %.4f, per trial %.6f (text 959,206.0941 and 7.3182); build per X2 would add "
          "%.4f per trial (text 10.58)" % (Pc, Pc / 131072, 18725 * 74 / 131072))
    src = open(os.path.join(PKG, "blake3-r2", "experiments", "halfsearch.py"), encoding="utf-8").read()
    print("     in the program text: 'for ' loops over a context range: looked for the words 1424469, '2 ** 84', "
          "'1 << 84': %s" % [w for w in ("1424469", "1,424,469", "2 ** 84", "1 << 84") if w in src])


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "text"
    if what == "text":
        part_text()
    elif what == "trials":
        part_trials(int(sys.argv[2]) if len(sys.argv) > 2 else 420)
    elif what == "extra":
        part_extra()
    elif what == "pass":
        part_pass(sys.argv[2] if len(sys.argv) > 2 else "1")
    elif what == "program":
        part_program()
    print("FAILED: %d" % len(FAIL) if FAIL else "all checks of this part hold")
    sys.exit(1 if FAIL else 0)
