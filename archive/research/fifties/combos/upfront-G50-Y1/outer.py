#!/usr/bin/env python3
"""outer.py - executable reference of the outer counter search of proof.md 9.1-9.3 and 9.6 (pkg21, blake3-r2).

What it implements, exactly on 32-bit words:
  * the whole-class sampler of 9.1 step 1: eight fresh uniform 256-bit words R_0..R_7 per batch, lane i = bits
    36i..36i+35; the random word of outer step 7b+i is the low 32 bits of lane i of each R_k; its eighth word W gives
    e1 = 030c0303 + (W AND fc307cfc), y = e1 - Y3 (the member of the class, 19 free bits);
  * the lines of step CO (the program's ctr_outer, copied line for line) as a scalar reference, and the packed batch
    of 9.6 compiled from the same lines: only the lines that reach Y9 or omega = Y3 + y + w8, x - z formed as
    x + (z XOR M) + 1, PROR rotations of five operations, constant additions kept pending until read by an XOR, OR,
    shift, rotation or table index, an AND with M wherever a lane bound could reach 2^36 (static interval bounds);
  * the exact outer filter of Section 8: the two carry automata of the program (ctr_automaton, copied) for the seven
    outcomes with their last tables ANDed with S = 5f, automaton (2) on omega in all seven lanes, then the lean
    Q path (E count, automaton (1) on Y9, AND, test) in increasing lane order;
  * the operation counter: every primitive the compiler emits is charged one unit (operations and table loads; every
    constant an immediate, 64 registers, Section 11 machine), plus the parts 9.6 charges without giving their code
    (the batch count 3, the last-batch test/cursor/dispatch 16, the E count 16, the passing lane 512).
Not implemented (outside 9.1-9.3/9.6 as briefed): the pre-check of 9.7 (VMASK, nu, the solver count), the joint
solver of 9.4 and the certificate of step 3. A passing outer step is yielded with every name of step CO.

Python 3 standard library only.  Usage:
  python outer.py --selftest
  python outer.py --run STEPS [--seed S] [--procs P] [--verify] [--passes FILE] [--json FILE]
"""
import argparse
import hashlib
import importlib.util
import json
import os
import sys
import time

MASK = 0xFFFFFFFF
IV = (0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A,
      0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19)
K = (IV[2] + IV[6]) & MASK
LEN_A, LEN_B = 55, 63
X3, X7, X11, X15 = 0x29D4FA98, 0xBEE3AF28, 0x44036000, 0x40C58500
W4, W13 = 0x97475638, 0x0007C006
W4B = (((W4 + K) & MASK) ^ LEN_A ^ LEN_B) - K & MASK
ETA = 0x830303CF
CTR_FLAGS = 3


def ror(v, n):
    return ((v >> n) | (v << (32 - n))) & MASK


def rol(v, n):
    return ((v << n) | (v >> (32 - n))) & MASK


def g(a, b, c, d, x, y):
    a = (a + b + x) & MASK; d = ror(d ^ a, 16); c = (c + d) & MASK; b = ror(b ^ c, 12)
    a = (a + b + y) & MASK; d = ror(d ^ a, 8); c = (c + d) & MASK; b = ror(b ^ c, 7)
    return a, b, c, d


Y3, _, Y11, _ = g(X3, X7, X11, X15, W4, W13)
Y3B, _, Y11B, _ = g(X3, X7, X11, X15, W4B, W13)
DY3 = (Y3B - Y3) & MASK
K2A = (K + W4) & MASK
K2D = ror(K2A ^ LEN_A, 16)
K2C = (IV[2] + K2D) & MASK
K2B = ror(IV[6] ^ K2C, 12)

# ---- the class (Lemma Q, Section 8): 13 fixed bits of e1, 19 free bits -------------------------------------------
CLASS_MASK, CLASS_VALUE, FREE_MASK = 0x03CF8303, 0x030C0303, 0xFC307CFC
CLASS_FREE = tuple(i for i in range(32) if FREE_MASK >> i & 1)
Y_PEND = (CLASS_VALUE - Y3) & MASK          # the pending constant of y = (W AND fc307cfc) + (030c0303 - Y3)

# ---- outcomes, S, and the constants of 9.1 ------------------------------------------------------------------------
TAUS = (0x175020A0, 0x185020A0, 0x275020A0, 0x285020A0, 0x385020A0, 0x675020A0, 0x685020A0)
EPS = 0x6E21BE55
S_MASK = 0x5F                                # S = {1,2,3,4,5,7}, bit j-1 for outcome j
SHARE = 18289159183466496
E_COUNT = 233715456
V_COUNT = 558140844222
FACTOR = 5 * 138512695296 // 7
RUN_STEPS = -(-(12419 << 128) // (25000 * FACTOR * ((1 << 21) - 1)))
E_BUDGET = -(-(17 * RUN_STEPS * E_COUNT) >> 36)
PASS_BUDGET = -(-(17 * RUN_STEPS * SHARE) >> 68)
SOLVER_BUDGET = -(-(17 * RUN_STEPS * V_COUNT) >> 55)
RUN_BATCHES = -(-RUN_STEPS // 7)
TEXT_CONSTANTS = {"FACTOR": 98937639497, "RUN_STEPS": 814694561164316144946,
                  "E_BUDGET": 47103299361697960684, "PASS_BUDGET": 858218304486124116,
                  "SOLVER_BUDGET": 214554576121531029, "RUN_BATCHES": 116384937309188020707}

# ---- packed words (6.5 / 9.6) --------------------------------------------------------------------------------------
LANES, LANE_BITS = 7, 36
ONES = sum(1 << (LANE_BITS * i) for i in range(LANES))
M_ALL = MASK * ONES                          # M: the low 32 bits of every lane
F_ALL = FREE_MASK * ONES
LIMIT = 1 << LANE_BITS
CHARGED_BATCH = 424                          # Section 11 charge per batch (9.6: 400 + 7 + 16 = 423, charged 424)
CHARGE_E_LANE = 35                           # Q path 19 + E count 16 (9.6, answer AT 4)
CHARGE_PASS = 512                            # a passing lane outside steps 2 and 3, pre-check included (9.6)
CHARGE_BATCH_COUNT = 3                       # advance of the batch count, compare with RUN_BATCHES, branch
CHARGE_DISPATCH = 16                         # test of the last batch, cursor, dispatch to the lanes (answer AT 4)
OUTER_WORDS = ("C0.d1", "D2.a1", "D2.b1", "S11", "S4", "X9", "w6")


# ---- the lines of step CO (the program's ctr_outer, same order) ----------------------------------------------------
def Sum(*t):
    return ("sum", t)


def Neg(x):
    return ("neg", x)


def X(a, b):
    return ("xor", a, b)


def R(a, r):
    return ("ror", a, r)


def L(a, r):
    return ("ror", a, 32 - r)


LINES = [
    ("X2", Sum("D2.a1", "D2.b1", W13)),
    ("X8", X(rol(X7, 7), "D2.b1")),
    ("C0.c1", Sum("X8", "C0.d1")),
    ("K3.a1", Sum((IV[3] + IV[7]) & MASK, "w6")),
    ("K3.d1", R(X("K3.a1", CTR_FLAGS), 16)),
    ("K3.c1", Sum(IV[3], "K3.d1")),
    ("S15", Sum("S11", Neg("K3.c1"))),
    ("S3", X(L("S15", 8), "K3.d1")),
    ("K3.b1", R(X(IV[7], "K3.c1"), 12)),
    ("D3.a1", Sum("S3", "S4")),
    ("S7", R(X("K3.b1", "S11"), 7)),
    ("D3.b1", Sum(X3, Neg("D3.a1"))),
    ("D2.c1", X(L("D2.b1", 12), "S7")),
    ("D3.c1", X(L("D3.b1", 12), "S4")),
    ("X4", R(X("D3.b1", "X9"), 7)),
    ("X13", Sum("X8", Neg("D2.c1"))),
    ("X14", Sum("X9", Neg("D3.c1"))),
    ("C0.b1", R(X("X4", "C0.c1"), 12)),
    ("D2.d1", X(L("X13", 8), "X2")),
    ("D3.d1", X(L("X14", 8), X3)),
    ("Y8", X(L("Y4", 7), "C0.b1")),
    ("S13", X(L("D2.d1", 16), "D2.a1")),
    ("S9", Sum("D3.c1", Neg("D3.d1"))),
    ("Y12", Sum("Y8", Neg("C0.c1"))),
    ("K1.c1", Sum("S9", Neg("S13"))),
    ("Y0", X(L("Y12", 8), "C0.d1")),
    ("K1.d1", Sum("K1.c1", Neg(IV[1]))),
    ("C0.a1", Sum("Y0", Neg("C0.b1"), Neg("w6"))),
    ("K1.a1", L("K1.d1", 16)),
    ("w2", Sum("K1.a1", Neg(IV[1]), Neg(IV[5]))),
    ("X0", Sum("C0.a1", Neg("X4"), Neg("w2"))),
    ("S14", X(L("D3.d1", 16), "D3.a1")),
    ("K1.b1", R(X(IV[5], "K1.c1"), 12)),
    ("S10", Sum(K2C, "S14")),
    ("D0.d1", X(rol(X15, 8), "X0")),
    ("S5", R(X("K1.b1", "S9"), 7)),
    ("D0.c1", Sum("S10", "D0.d1")),
    ("D0.b1", R(X("S5", "D0.c1"), 12)),
    ("X10", Sum("D0.c1", X15)),
    ("X5", R(X("D0.b1", "X10"), 7)),
    ("S1", X(L("S13", 8), "K1.d1")),
    ("w3", Sum("S1", Neg("K1.a1"), Neg("K1.b1"))),
    ("X12", X(L("C0.d1", 16), "C0.a1")),
    ("D1.c1", Sum(X11, Neg("X12"))),
    ("D1.d1", Sum("D1.c1", Neg("S11"))),
    ("S8", Sum("D2.c1", Neg("D2.d1"))),
    ("K0.b1", X(L("S4", 7), "S8")),
    ("S2", X(L("S14", 8), K2D)),
    ("S6", R(X(K2B, "S10"), 7)),
    ("X1", X(L("X12", 8), "D1.d1")),
    ("K0.c1", X(L("K0.b1", 12), IV[4])),
    ("D1.b1", R(X("S6", "D1.c1"), 12)),
    ("C1.a1", Sum("X1", "X5", "w3")),
    ("S12", Sum("S8", Neg("K0.c1"))),
    ("w7", Sum("S3", Neg("K3.a1"), Neg("K3.b1"))),
    ("X6", R(X("D1.b1", X11), 7)),
    ("C1.d1", R(X("X13", "C1.a1"), 16)),
    ("D1.a1", X(L("D1.d1", 16), "S12")),
    ("C1.c1", Sum("X9", "C1.d1")),
    ("C2.a1", Sum("X2", "X6", "w7")),
    ("w10", Sum("D1.a1", Neg("S1"), Neg("S6"))),
    ("C1.b1", R(X("X5", "C1.c1"), 12)),
    ("C2.d1", R(X("X14", "C2.a1"), 16)),
    ("w12", Sum("D2.a1", Neg("S2"), Neg("S7"))),
    ("Y1", Sum("C1.a1", "C1.b1", "w10")),
    ("C2.c1", Sum("X10", "C2.d1")),
    ("Y13", R(X("C1.d1", "Y1"), 8)),
    ("C2.b1", R(X("X6", "C2.c1"), 12)),
    ("K0.d1", Sum("K0.c1", Neg(IV[0]))),
    ("Y9", Sum("C1.c1", "Y13")),
    ("S0", X(L("S12", 8), "K0.d1")),
    ("D0.a1", X(L("D0.d1", 16), "S15")),
    ("w8", Sum("D0.a1", Neg("S0"), Neg("S5"))),
    ("w5", Sum("S2", Neg(K2A), Neg(K2B))),
    ("w9", Sum("X0", Neg("D0.a1"), Neg("D0.b1"))),
    ("w11", Sum("X1", Neg("D1.a1"), Neg("D1.b1"))),
    ("Y5", R(X("C1.b1", "Y9"), 7)),
]


def ev(e, v):
    'Scalar value of an expression of LINES on the dict v.'
    if isinstance(e, int):
        return e
    if isinstance(e, str):
        return v[e]
    k = e[0]
    if k == "sum":
        s = 0
        for t in e[1]:
            s += -ev(t[1], v) if isinstance(t, tuple) and t[0] == "neg" else ev(t, v)
        return s & MASK
    if k == "xor":
        return ev(e[1], v) ^ ev(e[2], v)
    if k == "ror":
        return ror(ev(e[1], v), e[2])
    raise ValueError(k)


def member_y(w):
    'e1 = 030c0303 + (W AND fc307cfc) (an OR: disjoint bits), y = e1 - Y3; member number = the 19 free bits in order.'
    e1 = CLASS_VALUE | (w & FREE_MASK)
    num = sum((w >> i & 1) << n for n, i in enumerate(CLASS_FREE))
    return (e1 - Y3) & MASK, e1, num


def scalar_outer(eight):
    'Step CO on scalar words for the eight words of an outer step (7 outer words, W): every name, plus y, e1, omega.'
    v = dict(zip(OUTER_WORDS, eight[:7]))
    v["Y4"], v["e1"], v["member"] = member_y(eight[7])
    for name, e in LINES:
        v[name] = ev(e, v)
    v["omega"] = (Y3 + v["Y4"] + v["w8"]) & MASK
    return v


def deps(e, out):
    if isinstance(e, str):
        out.add(e)
    elif isinstance(e, tuple):
        if e[0] == "sum":
            for t in e[1]:
                deps(t, out)
        elif e[0] in ("neg", "ror"):
            deps(e[1], out)
        elif e[0] == "xor":
            deps(e[1], out)
            deps(e[2], out)


def slice_lines(targets=("Y9", "w8")):
    'The lines of step CO whose values reach Y9 or omega (= Y3 + y + w8).'
    need, keep = set(targets), []
    for name, e in reversed(LINES):
        if name in need:
            keep.append((name, e))
            d = set()
            deps(e, d)
            need |= d
    return list(reversed(keep))


# ---- the carry automata (the program's ctr_automaton, copied) ------------------------------------------------------
def ctr_g(tau):
    return rol(tau ^ ror(tau, 1), 12)


def ctr_automaton(targets, dy, n=32):
    layer, trans = [(0, (1,) * len(targets))], []
    for i in range(n):
        ids, rows, e = {}, [], dy >> i & 1
        for k, sets in layer:
            row = []
            for a in (0, 1):
                b, new = a ^ e ^ k, []
                for m, (dz, out) in zip(sets, targets):
                    d, r = dz >> i & 1, 0
                    for c in range(4):
                        if m >> c & 1 and (c >> 1) ^ (c & 1) == (out >> i & 1) ^ a ^ b ^ d:
                            for v in (0, 1):
                                r |= 1 << ((a + v + (c >> 1)) >> 1) * 2 + ((b + (v ^ d) + (c & 1)) >> 1)
                    new.append(r)
                state = ((a + e + k) >> 1, tuple(new)) if any(new) else (0, (0,) * len(new))
                row.append(ids.setdefault(state, len(ids)))
            rows.append(row)
        trans.append(rows)
        layer = list(ids)
    final, tables = [sum(1 << j for j, m in enumerate(sets) if m) for _, sets in layer], []
    for p in range(0, n, 8):
        table = []
        for s in range(len(trans[p])):
            row = [s]
            for j in range(min(8, n - p)):
                row = [trans[p + j][row[x & (1 << j) - 1]][x >> j] for x in range(2 << j)]
            table += [final[row[x % len(row)]] if p + 8 >= n else row[x % len(row)] << 8 for x in range(256)]
        tables.append(table)
    return tables


def build_tables():
    'Automaton (1) on Q (dy 0, dz eta, out theta_j) and (2) on E (dy DY3, dz sigma_j, out eps), last tables AND S.'
    th = [ctr_g(t) for t in TAUS]
    t1 = ctr_automaton([(ETA, x) for x in th], 0)
    t2 = ctr_automaton([(ror(x, 12), EPS) for x in th], DY3)
    raw = (t1, t2)
    t1 = t1[:3] + [[m & S_MASK for m in t1[3]]]
    t2 = t2[:3] + [[m & S_MASK for m in t2[3]]]
    return raw, t1, t2


def look(tables, x):
    'Scalar automaton on x, a byte at a time (the program\'s ctr_look).'
    s = 0
    for p, t in enumerate(tables):
        b = x >> 8 * p & 255
        s = t[s + b if p else b]
    return s


def flatten(tables):
    'One array per automaton; a non-last entry holds the base address of the next table plus its state times 256.'
    bases, flat = [], []
    for t in tables:
        bases.append(len(flat))
        flat += t
    for p in range(3):
        lo, hi = bases[p], bases[p] + len(tables[p])
        for i in range(lo, hi):
            flat[i] += bases[p + 1]
    return flat, bases[0]


def pattern_counts(tables):
    'Exact count of 32-bit words per final pattern (DP over the byte tables).'
    cur = {}
    for b in range(256):
        s = tables[0][b]
        cur[s] = cur.get(s, 0) + 1
    for t in tables[1:]:
        nxt = {}
        for s, c in cur.items():
            for b in range(256):
                v = t[s + b]
                nxt[v] = nxt.get(v, 0) + c
        cur = nxt
    return cur


# ---- the packed compiler with the operation counter ---------------------------------------------------------------
class Val:
    __slots__ = ("var", "bound", "pend")

    def __init__(self, var, bound, pend=0):
        self.var, self.bound, self.pend = var, bound, pend


class Packed:
    """Compiles expressions to straight-line code on 256-bit packed words, charging one unit per emitted operation or
    load, and tracking the static upper bound of every lane (the interval bound of 9.6, from lines and constants)."""

    def __init__(self):
        self.code, self.n, self.units, self.part = [], 0, {}, None
        self.vals, self.bounds, self.maxbound = {}, {}, 0
        self.consts = {}

    def at(self, part):
        self.part = part
        self.units.setdefault(part, 0)

    def emit(self, src, bound, cost):
        v = "t%d" % self.n
        self.n += 1
        self.code.append("%s = %s" % (v, src))
        self.units[self.part] += cost
        self.bounds[v] = bound
        self.maxbound = max(self.maxbound, bound)
        assert bound < LIMIT
        return v

    def const(self, c):
        name = "C%08x" % c
        self.consts[name] = c * ONES
        return name

    def reduce(self, a):
        'AND with M (charged), keeps the pending constant.'
        return Val(self.emit("%s & M_ALL" % a.var, MASK, 1), MASK, a.pend)

    def mat(self, a):
        'Form the pending constant addition (charged) before a read by XOR, OR, shift, rotation or table index.'
        if not a.pend:
            return a
        if a.bound + a.pend >= LIMIT:
            a = self.reduce(a)
        return Val(self.emit("%s + %s" % (a.var, self.const(a.pend)), a.bound + a.pend, 1), a.bound + a.pend)

    def add(self, a, b):
        while a.bound + b.bound >= LIMIT:
            if a.bound >= b.bound:
                a = self.reduce(a)
            else:
                b = self.reduce(b)
        return Val(self.emit("%s + %s" % (a.var, b.var), a.bound + b.bound, 1), a.bound + b.bound,
                   (a.pend + b.pend) & MASK)

    def name(self, n):
        return self.vals[n]

    def operand(self, e):
        if isinstance(e, str):
            a = self.mat(self.vals[e])
            self.vals[e] = a              # the register now holds the formed value
            return a
        return self.comp(e, read=True)

    def comp(self, e, read=False):
        if isinstance(e, str):
            return self.operand(e) if read else self.vals[e]
        k = e[0]
        if k == "sum":
            acc, pend = None, 0
            for t in e[1]:
                neg = isinstance(t, tuple) and t[0] == "neg"
                x = t[1] if neg else t
                if isinstance(x, int):
                    pend += -x if neg else x
                    continue
                if neg:                   # x - z = x + (z XOR M) + 1, z read by an XOR
                    z = self.operand(x)
                    b = (1 << max(32, z.bound.bit_length())) - 1
                    v = Val(self.emit("%s ^ M_ALL" % z.var, b, 1), b, 1)
                else:
                    v = self.comp(x)
                acc = v if acc is None else self.add(acc, v)
            acc = Val(acc.var, acc.bound, (acc.pend + pend) & MASK)
            return self.mat(acc) if read else acc
        if k == "xor":
            a, b = e[1], e[2]
            if isinstance(a, int):
                a, b = b, a
            x = self.operand(a)
            if isinstance(b, int):
                return Val(self.emit("%s ^ %s" % (x.var, self.const(b)), (1 << max(32, x.bound.bit_length())) - 1, 1),
                           (1 << max(32, x.bound.bit_length())) - 1)
            y = self.operand(b)
            bd = (1 << max(x.bound.bit_length(), y.bound.bit_length(), 32)) - 1
            return Val(self.emit("%s ^ %s" % (x.var, y.var), bd, 1), bd)
        if k == "ror":
            x = self.operand(e[1])
            r = e[2]
            src = "((%s >> %d) & A%d) | ((%s << %d) & B%d)" % (x.var, r, r, x.var, 32 - r, r)
            return Val(self.emit(src, MASK, 5), MASK)
        raise ValueError(k)


def rot_masks():
    ns = {}
    for r in range(1, 32):
        ns["A%d" % r] = ((1 << (32 - r)) - 1) * ONES
        ns["B%d" % r] = (((1 << r) - 1) << (32 - r)) * ONES
    return ns


def compile_batch(fe_base):
    """The packed batch of 9.6 as Python source. Returns (source, units by part, name map, bounds, maxbound, live)."""
    P = Packed()
    P.at("random words")
    args = ["R%d" % k for k in range(8)]
    for k in range(7):                   # draw (one operation, charged here; the draw itself is the argument) + AND M
        P.units["random words"] += 1
        v = P.emit("R%d & M_ALL" % k, MASK, 1)
        P.vals[OUTER_WORDS[k]] = Val(v, MASK)
    P.units["random words"] += 1
    v = P.emit("R7 & F_ALL", FREE_MASK, 1)
    P.vals["Y4"] = Val(v, FREE_MASK, Y_PEND)     # y: a pending constant addition
    P.at("CO lines to Y9 and omega")
    for name, e in slice_lines():
        P.vals[name] = P.comp(e)
    P.vals["Y9"] = P.operand("Y9")       # Y9 is read by table index (Q path)
    P.at("omega")
    om = P.comp(Sum("Y4", "w8", Y3), read=True)
    P.vals["omega"] = om
    P.at("automaton (2), 7 lanes")
    masks = []
    for i in range(LANES):
        s = None
        for p in range(4):
            sh = 36 * i + 8 * p
            if sh:
                b = P.emit("(%s >> %d) & 255" % (om.var, sh), 255, 2)
            else:
                b = P.emit("%s & 255" % om.var, 255, 1)
            if p == 0:
                s = P.emit("FE[%s + %d]" % (b, fe_base), 0, 2)     # base addition + table load (bound 0: scalar)
            else:
                s = P.emit("FE[%s + %s]" % (s, b), 0, 2)           # state addition + table load (bound 0: scalar)
        P.units[P.part] += 2                                        # test of the mask against zero, branch
        masks.append(s)
    P.code.append("return %s, %s, (%s,)" % (P.vals["Y9"].var, om.var, ", ".join(masks)))
    body = "\n    ".join(P.code)
    src = "def batch(%s):\n    %s\n" % (", ".join(args), body)
    # liveness: largest number of packed values live at once (inputs counted while still to be read)
    last = {}
    for idx, line in enumerate(P.code):
        for tok in line.replace("(", " ").replace(")", " ").replace(",", " ").replace("[", " ").replace("]", " ").split():
            if (tok.startswith("t") and tok[1:].isdigit()) or (tok.startswith("R") and tok[1:].isdigit()):
                last[tok] = idx
    live, cur = 0, set(a for a in args)
    for idx, line in enumerate(P.code):
        d = line.split(" = ")[0] if " = " in line else None
        if d:
            cur.add(d)
        live = max(live, len(cur))
        cur = {x for x in cur if last.get(x, -1) > idx}
    return src, dict(P.units), P.vals, P.bounds, P.maxbound, live, P.consts


class Search:
    'Tables, the compiled batch, the counters and the budgets of one run (or one worker).'

    def __init__(self, check_bounds=False):
        self.raw, self.t1, self.t2 = build_tables()
        self.fe, fe_base = flatten(self.t2)
        self.fq, self.fq_base = flatten(self.t1)
        src, self.units, self.vals, self.bounds, self.maxbound, self.live, consts = compile_batch(fe_base)
        ns = dict(rot_masks(), M_ALL=M_ALL, F_ALL=F_ALL, FE=self.fe, **consts)
        exec(src, ns)
        self.batch, self.src = ns["batch"], src
        if check_bounds:                 # a variant that returns every temporary, for the lane-bound check
            src2 = src.replace("\n    return ", "\n    return locals(), ")
            exec(src2, ns)
            self.batch_all = ns["batch"]
            ns["batch"] = self.batch
        computed = sum(self.units.values())
        self.batch_units = computed + CHARGE_BATCH_COUNT + CHARGE_DISPATCH

    def q_path(self, y9_lane):
        'Automaton (1) on the Y9 of one lane (4 shifts, 4 byte masks, base + 3 state additions, 4 loads).'
        fq = self.fq
        s = fq[(y9_lane & 255) + self.fq_base]
        s = fq[s + (y9_lane >> 8 & 255)]
        s = fq[s + (y9_lane >> 16 & 255)]
        return fq[s + (y9_lane >> 24 & 255)]


def draw(seed, b):
    'The eight fresh uniform 256-bit words of batch b (SHAKE-256 of a label, the seed and the batch number).'
    buf = hashlib.shake_256(b"outer.py batch" + seed.to_bytes(8, "little") + b.to_bytes(8, "little")).digest(256)
    return [int.from_bytes(buf[32 * k:32 * k + 32], "little") for k in range(8)]


def lane(x, i):
    return x >> (36 * i) & MASK


class Halt(Exception):
    pass


def iter_passes(seed, b_start, b_end, total_steps=RUN_STEPS, search=None, counts=None, verify=False,
                e_budget=E_BUDGET, pass_budget=PASS_BUDGET):
    """Run batches b_start..b_end-1 (9.1 step 1 with the lean lanes of 9.6) and yield every passing outer step as a
    dict with all names of step CO (rebuilt on scalar words from the lane's eight words) and the filter masks.
    counts (a dict) receives the counters: batches, steps, E count, passes, charged units, per-outcome masks.
    Raises Halt when a budget is exceeded (9.1)."""
    S = search or Search(check_bounds=verify)
    c = counts if counts is not None else {}
    for key in ("batches", "steps", "e_count", "passes", "units", "verified_lanes", "verify_fail", "bound_fail"):
        c.setdefault(key, 0)
    c.setdefault("m2_outcome", [0] * 7)
    c.setdefault("x_outcome", [0] * 7)
    for b in range(b_start, b_end):
        Rw = draw(seed, b)
        if verify:
            env, y9p, omp, masks = S.batch_all(*Rw)
            for v, bd in S.bounds.items():
                if not bd:                         # a table load: a scalar state, not a packed word
                    continue
                x = env[v]
                for i in range(LANES):
                    if (x >> 36 * i) & (LIMIT - 1) > bd:
                        c["bound_fail"] += 1
        else:
            y9p, omp, masks = S.batch(*Rw)
        c["batches"] += 1
        c["units"] += S.batch_units
        used = min(LANES, total_steps - 7 * b)
        c["steps"] += used
        for i in range(used):
            m2 = masks[i]
            if verify:
                eight = [lane(Rw[k], i) for k in range(8)]
                v = scalar_outer(eight)
                ok = (lane(y9p, i) == v["Y9"] and lane(omp, i) == v["omega"]
                      and m2 == look(S.t2, v["omega"]))
                for name, val in S.vals.items():
                    if name in v and (lane(env[val.var], i) + val.pend) & MASK != v[name]:
                        ok = False
                if m2 and S.q_path(v["Y9"]) != look(S.t1, v["Y9"]):
                    ok = False
                c["verified_lanes"] += 1
                c["verify_fail"] += not ok
            if not m2:
                continue
            for j in range(7):
                c["m2_outcome"][j] += m2 >> j & 1
            c["e_count"] += 1                      # the E count and its test
            c["units"] += CHARGE_E_LANE
            if c["e_count"] > e_budget:
                raise Halt("E count exceeds E_BUDGET")
            x = S.q_path(lane(y9p, i)) & m2
            if not x:
                continue
            c["passes"] += 1                       # the pass count and its test
            c["units"] += CHARGE_PASS
            for j in range(7):
                c["x_outcome"][j] += x >> j & 1
            if c["passes"] > pass_budget:
                raise Halt("pass count exceeds PASS_BUDGET")
            eight = [lane(Rw[k], i) for k in range(8)]
            v = scalar_outer(eight)                # the scalar rebuild of step CO for steps 2 and 3
            if v["Y9"] != lane(y9p, i) or v["omega"] != lane(omp, i):
                c["verify_fail"] += 1
            yield {"step": 7 * b + i, "batch": b, "lane": i, "seed": seed,
                   "eight": ["%08x" % w for w in eight], "W": "%08x" % eight[7], "member": v["member"],
                   "e1": "%08x" % v["e1"], "y": "%08x" % v["Y4"], "omega": "%08x" % v["omega"],
                   "Y9": "%08x" % v["Y9"], "mask1": "%02x" % (S.q_path(v["Y9"])), "mask2": "%02x" % m2,
                   "X": "%02x" % x, "outcomes": [j + 1 for j in range(7) if x >> j & 1],
                   "names": {k: "%08x" % val for k, val in v.items() if k not in ("member",)}}


def worker(job):
    seed, b0, b1, verify, keep = job
    c = {}
    out = []
    t = time.time()
    for rec in iter_passes(seed, b0, b1, counts=c, verify=verify):
        if keep:
            out.append(rec)
    c["seconds"] = time.time() - t
    return c, out


# ---- self-test ------------------------------------------------------------------------------------------------------
def brute_masks(n, targets, dy, x):
    'Brute force at width n: bit t set when some v gives (x + v) ^ (x + dy + (v ^ dz)) = out modulo 2^n.'
    m, mk = 0, (1 << n) - 1
    for t, (dz, out) in enumerate(targets):
        for v in range(1 << n):
            if ((x + v) ^ (x + dy + (v ^ dz))) & mk == out & mk:
                m |= 1 << t
                break
    return m


def look_n(tables, x, n):
    s = 0
    for p, t in enumerate(tables):
        b = x >> 8 * p & ((1 << min(8, n - 8 * p)) - 1)
        s = t[s + b if p else b]
    return s


def selftest(halfsearch_path):
    res, ok = {}, True
    cons = {k: globals()[k] for k in TEXT_CONSTANTS}
    res["constants"] = {k: (cons[k], TEXT_CONSTANTS[k], cons[k] == TEXT_CONSTANTS[k]) for k in TEXT_CONSTANTS}
    ok &= all(x[2] for x in res["constants"].values())
    res["V_COUNT_vs_2SHARE/2^16"] = (V_COUNT, 2 * SHARE / 65536)
    x = rol(ETA, 16)
    vv = (Y3B - Y3 + x) & MASK
    res["class"] = (x & 0x7FFFFFFF == CLASS_MASK and ~(vv >> 1) & CLASS_MASK & MASK == CLASS_VALUE
                    and CLASS_MASK ^ FREE_MASK == MASK and DY3 == 0xFDB77CFD)
    ok &= res["class"]
    # (a) brute force of the automata at width 8, real targets truncated and random targets
    import random
    rnd = random.Random(1)
    th = [ctr_g(t) for t in TAUS]
    right = total = 0
    for case in range(8):
        n = 8
        if case % 2 == 0:
            tq = [(ETA, t) for t in th]
            te = [(ror(t, 12), EPS) for t in th]
            dy = DY3
        else:
            tq = [(rnd.getrandbits(32), rnd.getrandbits(32)) for _ in range(7)]
            te = [(rnd.getrandbits(32), rnd.getrandbits(32)) for _ in range(7)]
            dy = rnd.getrandbits(32)
        a1 = ctr_automaton([(d & 255, o & 255) for d, o in tq], 0, n)
        a2 = ctr_automaton([(d & 255, o & 255) for d, o in te], dy & 255, n)
        for xx in range(256):
            total += 2
            right += look_n(a1, xx, n) == brute_masks(n, tq, 0, xx)
            right += look_n(a2, xx, n) == brute_masks(n, te, dy, xx)
    res["automaton_bruteforce_w8"] = "%d of %d" % (right, total)
    ok &= right == total
    S = Search(check_bounds=True)
    # (b) exact counts from the tables
    n1, n2 = pattern_counts(S.t1), pattern_counts(S.t2)
    share = sum(c1 * c2 for p, c1 in n1.items() for q, c2 in n2.items() if p & q & S_MASK)
    ecount = sum(c2 for q, c2 in n2.items() if q & S_MASK)
    res["SHARE_from_tables"] = (share, SHARE, share == SHARE)
    res["E_COUNT_from_tables"] = (ecount, E_COUNT, ecount == E_COUNT)
    ok &= share == SHARE and ecount == E_COUNT
    # (c) tables equal to the program's, and scalar step CO equal to the program's ctr_outer
    if halfsearch_path and os.path.exists(halfsearch_path):
        spec = importlib.util.spec_from_file_location("halfsearch", halfsearch_path)
        hs = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(hs)
        same_tables = [list(a) for a in hs.ctr_tables()[0]] == S.raw[0] and \
                      [list(a) for a in hs.ctr_tables()[1]] == S.raw[1]
        res["tables_equal_program"] = same_tables
        agree = 0
        for k in range(2000):
            buf = hashlib.shake_256(b"outer.py co check" + k.to_bytes(4, "little")).digest(32)
            eight = list(int.from_bytes(buf[4 * i:4 * i + 4], "little") for i in range(8))
            ref = hs.ctr_outer(eight)
            v = dict(zip(OUTER_WORDS, eight[:7]))
            v["Y4"] = ref["Y4"]
            for name, e in LINES:
                v[name] = ev(e, v)
            agree += all(v[nm] == ref[nm] for nm in ref)
        res["ctr_outer_equal_program"] = "%d of 2000" % agree
        ok &= same_tables and agree == 2000
    else:
        res["tables_equal_program"] = "halfsearch.py not found, skipped"
    # (d) packed batch against scalar step CO and the scalar filter, every lane, with the lane-bound check
    c = {}
    passes = list(iter_passes(7, 0, 4096, search=S, counts=c, verify=True))
    res["packed_vs_scalar"] = {"lanes": c["verified_lanes"], "fail": c["verify_fail"], "bound_fail": c["bound_fail"],
                               "passes": len(passes), "e_count": c["e_count"]}
    ok &= c["verify_fail"] == 0 and c["bound_fail"] == 0
    # (e) last batch: lanes 4 to 6 unused
    c2 = {}
    list(iter_passes(7, 0, 1, total_steps=4, search=S, counts=c2))
    res["last_batch_steps"] = c2["steps"]
    ok &= c2["steps"] == 4 and (RUN_STEPS - 7 * (RUN_BATCHES - 1)) == 4
    # (f) budget halts: pass budget 2 halts at the third pass; E budget 5 halts at the sixth E lane
    c3, seen = {}, 0
    try:
        for _ in iter_passes(7, 0, 4096, search=S, counts=c3, pass_budget=2):
            seen += 1
        halted = False
    except Halt:
        halted = True
    res["pass_budget_halt"] = halted and seen == 2 and c3["passes"] == 3
    c4 = {}
    try:
        list(iter_passes(7, 0, 4096, search=S, counts=c4, e_budget=5))
        h4 = False
    except Halt:
        h4 = True
    res["e_budget_halt"] = h4 and c4["e_count"] == 6
    ok &= res["pass_budget_halt"] and res["e_budget_halt"]
    res["batch_units"] = S.units
    res["batch_units_total"] = S.batch_units
    res["max_lane_bound_bits"] = S.maxbound.bit_length()
    res["max_live_packed"] = S.live
    res["ok"] = bool(ok)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--halfsearch", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pkg21",
                                                         "pkg", "blake3-r2", "experiments", "halfsearch.py"))
    ap.add_argument("--run", type=int, default=0, help="number of outer steps")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--procs", type=int, default=8)
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--passes", default="")
    ap.add_argument("--json", default="")
    a = ap.parse_args()
    if a.selftest:
        r = selftest(a.halfsearch)
        print(json.dumps(r, indent=1, default=str))
        if a.json:
            with open(a.json, "w") as f:
                json.dump(r, f, indent=1, default=str)
        sys.exit(0 if r["ok"] else 1)
    if a.run:
        from multiprocessing import Pool
        nb = -(-a.run // 7)
        chunk = max(1, -(-nb // (a.procs * 8)))
        jobs = [(a.seed, b, min(nb, b + chunk), a.verify, bool(a.passes)) for b in range(0, nb, chunk)]
        t = time.time()
        tot, recs = {}, []
        with Pool(a.procs) as pool:
            for c, out in pool.imap(worker, jobs):
                for k, v in c.items():
                    if isinstance(v, list):
                        tot[k] = [x + y for x, y in zip(tot.get(k, [0] * len(v)), v)]
                    else:
                        tot[k] = tot.get(k, 0) + v
                recs += out
        tot["wall_seconds"] = time.time() - t
        S = Search()
        steps = tot["steps"]
        pi = SHARE / 2 ** 64
        pe = E_COUNT / 2 ** 32
        meas = tot["passes"] / steps
        se = (pi * (1 - pi) / steps) ** 0.5
        tot.update({
            "seed": a.seed, "outer_steps_requested": a.run, "verify_all_lanes": a.verify,
            "pass_share_measured": meas, "pass_share_exact_SHARE/2^64": pi, "pass_z": (meas - pi) / se,
            "pass_ratio_measured/exact": meas / pi,
            "e_share_measured": tot["e_count"] / steps, "e_share_exact_E_COUNT/2^32": pe,
            "e_z": (tot["e_count"] / steps - pe) / (pe * (1 - pe) / steps) ** 0.5,
            "batch_units_computed_by_part": S.units, "batch_units_charged_per_batch_here": S.batch_units,
            "batch_units_proof": {"computed": 400, "with_AT4": 423, "charged": CHARGED_BATCH},
            "units_per_step_charged_here": tot["units"] / steps,
            "units_per_step_with_424": (tot["batches"] * CHARGED_BATCH + tot["e_count"] * CHARGE_E_LANE
                                        + tot["passes"] * CHARGE_PASS) / steps,
            "max_lane_bound_bits": S.maxbound.bit_length(), "max_live_packed": S.live,
        })
        recs.sort(key=lambda r: r["step"])
        if a.passes:
            with open(a.passes, "w") as f:
                for r in recs:
                    f.write(json.dumps(r) + "\n")
        if a.json:
            with open(a.json, "w") as f:
                json.dump(tot, f, indent=1)
        print(json.dumps(tot, indent=1))


if __name__ == "__main__":
    main()
