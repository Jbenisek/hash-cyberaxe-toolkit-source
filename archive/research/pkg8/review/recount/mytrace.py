"""RECOUNT agent's OWN counter for the pkg8 cluster program. Research only; nothing is filed.

This file does NOT use halfsearch_cluster.Machine. It defines its own counter `Tr` straight from the
charging scheme given to the recount agent:

    load 1, store 1, add 1, subtract 1, AND 1, OR 1, XOR 1, NOT 1, shift 1;
    a rotation of every lane 5; a comparison and the branch on it 2;
    a word already in a register is not a load; 16 registers.

The arithmetic of each piece is re-transcribed line by line from the text of halfsearch_cluster.py
(packed_batch / partner_batch / gate_flags / dispatch / delta_uword / broadcast / mixed_middle_cache /
table_build / middle_step). Values are carried along so that every lane can be compared with the
program's own reference and so that the 36-bit lane occupancy can be checked under mixed X2.

halfsearch_cluster is imported for VALUES ONLY (memory builders, reference, constants) -- never for
its counter.

    python -B mytrace.py
"""
import sys, os, json

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "program"))
import halfsearch_cluster as H

LANES, LB = H.LANES, H.LANE_BITS            # 7 lanes of 36 bits
LANE = (1 << LB) - 1
WORD = (1 << 256) - 1
MASK32 = (1 << 32) - 1


def lanes(z):
    return [(z >> (LB * i)) & LANE for i in range(LANES)]


class Val:
    __slots__ = ("z", "born", "last", "tag")

    def __init__(self, z, born, tag=""):
        self.z, self.born, self.last, self.tag = z, born, born, tag


class Tr:
    """My own counter. Every charge goes through charge(); nothing is charged anywhere else."""

    UNIT = {"load": 1, "store": 1, "add": 1, "sub": 1, "and": 1, "or": 1, "xor": 1, "not": 1,
            "shift": 1, "rot": 5, "cmpbr": 2}

    def __init__(self, memory, resident=()):
        self.mem = memory
        self.part = None
        self.cost = {}                 # part -> {kind: count}
        self.order = []
        self.step = 0
        self.vals = []
        self.reg = {}                  # memory name -> Val held in a register
        self.maxlane = {}              # part -> largest lane of any sum
        self.rot_mask_loads = 0        # loads that exist only to feed a rotation
        for name in resident:          # the class-loop entry put these in registers; its loads are counted there
            self.reg[name] = self._mk(self.mem[name], "res:" + name)

    # ---- bookkeeping ----
    def at(self, part):
        self.part = part
        self.cost.setdefault(part, {})
        self.maxlane.setdefault(part, 0)
        self.order.append(part)

    def charge(self, kind, n=1):
        self.cost[self.part][kind] = self.cost[self.part].get(kind, 0) + n

    def _mk(self, z, tag="", *used):
        self.step += 1
        for u in used:
            u.last = self.step
        v = Val(z & WORD, self.step, tag)
        self.vals.append(v)
        return v

    def total(self, parts=None):
        parts = self.order if parts is None else parts
        seen, t = set(), 0
        for p in parts:
            if p in seen:
                continue
            seen.add(p)
            for kind, n in self.cost[p].items():
                t += self.UNIT[kind] * n
        return t

    def breakdown(self, parts=None):
        parts = self.order if parts is None else parts
        out = {}
        seen = set()
        for p in parts:
            if p in seen:
                continue
            seen.add(p)
            for kind, n in self.cost[p].items():
                out[kind] = out.get(kind, 0) + n
        return out

    def registers(self):
        """Peak number of values alive at one time, plus the two loop counters."""
        change = [0] * (self.step + 2)
        for v in self.vals:
            change[v.born] += 1
            change[v.last] -= 1
        held = peak = 0
        for d in change:
            held += d
            peak = max(peak, held)
        return peak + 2

    # ---- operands ----
    def k(self, name):
        """A memory word as an operand: free if it is already in a register, else one load."""
        if name in self.reg:
            return self.reg[name]
        self.charge("load")
        return self._mk(self.mem[name], "ld:" + name)

    def fetch(self, z, tag="word"):
        """A table word or a list word: one load."""
        self.charge("load")
        return self._mk(z, tag)

    def keep(self, *names):
        for n in names:
            if n not in self.reg:
                self.charge("load")
                self.reg[n] = self._mk(self.mem[n], "keep:" + n)

    def drop(self, *names):
        self.step += 1
        for n in names:
            if n in self.reg:
                self.reg.pop(n).last = self.step

    def store(self, v):
        self.charge("store")
        self.step += 1
        v.last = self.step
        return v.z

    # ---- operations ----
    def add(self, x, y):
        self.maxlane[self.part] = max([self.maxlane[self.part]] + [a + b for a, b in zip(lanes(x.z), lanes(y.z))])
        self.charge("add")
        return self._mk(x.z + y.z, "add", x, y)

    def xor(self, x, y):
        self.charge("xor")
        return self._mk(x.z ^ y.z, "xor", x, y)

    def band(self, x, y):
        self.charge("and")
        return self._mk(x.z & y.z, "and", x, y)

    def bor(self, x, y):
        self.charge("or")
        return self._mk(x.z | y.z, "or", x, y)

    def shl(self, x, r):
        self.charge("shift")
        return self._mk(x.z << r, "shl", x)

    def shr(self, x, r):
        self.charge("shift")
        return self._mk(x.z >> r, "shr", x)

    def cmpbr(self, x, y):
        self.charge("cmpbr")
        self.step += 1
        x.last = y.last = self.step
        return x.z != y.z

    def counter(self, pos):
        """The next value of a loop counter, in its own register: one addition."""
        self.charge("add")
        self.step += 1
        return Val(pos + 1, self.step, "counter")

    def rot(self, x, r):
        """Rotate every lane right by r. 5 units, and the two masks are memory words."""
        a, b = self.k("A%d" % r), self.k("B%d" % r)
        before = self.cost[self.part].get("load", 0)
        self.charge("rot")
        lo = x.z >> r
        hi = x.z << (32 - r)
        z = (lo & a.z) | (hi & b.z)
        if "A%d" % r not in self.reg:
            self.rot_mask_loads += 1
        if "B%d" % r not in self.reg:
            self.rot_mask_loads += 1
        del before
        return self._mk(z, "rot", x, a, b)

    def rol(self, x, r):
        return self.rot(x, 32 - r)


# =================================================================================================
# My transcription of the two-stage batch (packed_batch / partner_batch -- identical call sequence).
# =================================================================================================
RESIDENT = H.RESIDENT          # the nine kept words (data, not a count)
EVICT = H.EVICT


def my_batch(c, row, vword, j, entered=0):
    tr = Tr(c, RESIDENT)

    def drop(*names):
        tr.drop(*[n for n in names if n not in RESIDENT])

    k = tr.k
    # ---------------- stage A ----------------
    tr.at("loop")
    tr.cmpbr(tr.counter(j), k("end of list"))
    tr.at("X0 to X10")
    dd0 = tr.xor(tr.add(tr.fetch(row["XA"], "row XA"), k("-w2")), k("ROL(X15,8)"))
    x10 = tr.add(dd0, k("S10+X15"))
    tr.at("C2 to z")
    x6 = tr.fetch(row["X6"], "row X6")
    ra = tr.add(x6, k("X2+w7"))
    rd = tr.rot(tr.xor(ra, k("X14")), 16)
    rc = tr.add(x10, rd)
    rb = tr.rot(tr.xor(x6, rc), 12)
    z = tr.xor(rd, tr.add(tr.add(ra, rb), k("w0")))
    tr.at("rule A")
    y, s, n = z, None, 0
    for step in H.A_STEPS:
        if isinstance(step, tuple):
            n, d = n + 1, step[0]
            s = tr.band(tr.shl(y, d) if d > 0 else tr.shr(y, -d), k("A mask %d" % n))
        else:
            s = tr.shl(s, step) if step > 0 else tr.shr(s, -step)
        y = tr.xor(y, s)
    sa = tr.add(tr.band(tr.xor(y, tr.fetch(vword, "list V")), k("A all")), k("A carry"))
    taken_a = tr.cmpbr(tr.bor(sa, k("not bit 32")), k("not bit 32"))
    flags_a = [1 - (sa.z >> (LB * i + 32) & 1) for i in range(LANES)]
    stage_a_parts = list(dict.fromkeys(tr.order))
    # ---------------- stage 2 ----------------
    tr.at("entry count")
    tr.drop(*EVICT)
    tr.cmpbr(tr.counter(entered), k("stage-2 budget"))
    tr.at("C2, rest")
    if H.Z_AGAIN:
        z = tr.xor(rd, tr.add(tr.add(tr.add(tr.fetch(row["X6"], "row X6"), k("X2+w7")), rb), k("w0")))
    if H.RC_AGAIN:
        rc = tr.add(x10, rd)
    tr.keep("A8", "B8")
    y14 = tr.rot(z, 8)
    tr.keep("A7", "B7")
    y6 = tr.rot(tr.xor(tr.add(rc, y14), rb), 7)
    tr.at("C1 to Y1")
    bd0 = tr.rot(tr.xor(tr.add(x10, k("-X15")), k("S5")), 12)
    x5 = tr.rot(tr.xor(bd0, x10), 7)
    drop("A7", "B7")
    qa = tr.add(tr.add(x5, tr.fetch(row["X1"], "row X1")), k("w3"))
    qd = tr.rot(tr.xor(qa, k("X13")), 16)
    qc = tr.add(qd, k("X9"))
    qb = tr.rot(tr.xor(x5, qc), 12)
    y1 = tr.add(tr.add(qa, qb), tr.xor(tr.fetch(row["R"], "row R"), k("S12")))
    tr.at("E1, A and B")
    a1 = tr.add(tr.add(y1, y6), k("w12-S1-S6"))
    d1 = tr.rot(tr.xor(a1, tr.fetch(row["Y12"], "row Y12")), 16)
    c1 = tr.add(d1, k("Y11"))
    b1 = tr.rot(tr.xor(c1, y6), 12)
    a2 = tr.add(tr.add(k("w5"), a1), b1)
    c2 = tr.add(c1, tr.rot(tr.xor(a2, d1), 8))
    c1b = tr.add(d1, k("Y11'"))
    b1b = tr.rot(tr.xor(c1b, y6), 12)
    a2b = tr.add(tr.add(k("w5+delta"), a1), b1b)
    beta = tr.xor(b1, b1b)
    c2b = tr.add(c1b, tr.rot(tr.xor(a2b, d1), 8))
    drop("A8", "B8")
    tr.at("E1 test")
    eps = tr.xor(c2, c2b)
    x = tr.xor(beta, eps)
    rotx = tr.bor(tr.band(tr.shr(x, 31), k("A31")), tr.shl(x, 1))     # ROL(x,1), 4 units not 5
    tr.keep("M", "bit 32")
    word = tr.band(tr.xor(tr.xor(rotx, eps), k("eta")), k("M"))
    fl = tr.band(tr.add(word, k("M")), k("bit 32"))
    taken = tr.cmpbr(fl, k("bit 32"))
    flags = [(fl.z >> (LB * i + 32)) & 1 for i in range(LANES)]
    drop("M", "bit 32")
    if EVICT:
        tr.at("restore")
        tr.keep(*EVICT)
    all_parts = list(dict.fromkeys(tr.order))
    stage_2_parts = [p for p in all_parts if p not in stage_a_parts]
    return tr, stage_a_parts, stage_2_parts, lanes(word.z), flags, taken, flags_a, taken_a


# ---- the other new pieces, transcribed ----------------------------------------------------------
def my_gate(c, zval):
    tr = Tr(c, ("not bit 32",))
    tr.at("gate")
    z = tr._mk(zval, "z live from stage A")
    s = tr.add(tr.band(tr.xor(z, tr.k("gate V")), tr.k("gate all")), tr.k("gate carry"))
    tr.cmpbr(tr.bor(s, tr.k("not bit 32")), tr.k("not bit 32"))
    return tr, [(s.z >> (LB * i + 32)) & 1 for i in range(LANES)]


def my_dispatch(c, gword):
    tr = Tr(c)
    tr.at("dispatch")
    g = tr._mk(gword, "saved gate word")
    zero = tr.k("zero")
    out = []
    for i in range(LANES):
        out.append(tr.cmpbr(tr.band(g, tr.k("lane %d" % i)), zero))
    return tr, out


def my_delta(c):
    tr = Tr(c)
    tr.at("delta")
    tr.band(tr.add(tr.k("U word"), tr.k("D word")), tr.k("M"))
    return tr


def my_broadcast(c):
    tr = Tr(c)
    tr.at("broadcast")
    u = tr.k("scalar")
    a = tr.bor(u, tr.shl(u, LB))
    b = tr.bor(a, tr.shl(a, 2 * LB))
    tr.bor(b, tr.shl(b, 4 * LB))
    return tr


def my_cache(c):
    tr = Tr(c)
    tr.at("cache")
    for p in range(6):
        mask = tr.k("L%d" % p)
        for f in range(7):
            a, b = tr.k("fieldA"), tr.k("fieldB")
            tr.store(tr.xor(tr.band(tr.xor(a, b), mask), b))
    return tr


def my_table_build(c, uword, j):
    """table_build, transcribed. Five stored words per list word of seven members."""
    tr = Tr(c)
    k = tr.k
    tr.at("build loop")
    tr.cmpbr(tr.counter(j), k("end of list"))
    tr.at("build C0")
    y12 = tr.band(tr.add(tr.xor(tr.fetch(uword, "list U"), k("C0.b1")), k("-C0.c1")), k("M"))
    tr.store(y12)
    ca = tr.add(tr.xor(tr.rol(y12, 8), k("C0.d1")), k("-C0.b1-w6"))
    tr.store(tr.band(tr.add(ca, k("-X4")), k("M")))
    x12 = tr.xor(ca, k("ROL(C0.d1,16)"))
    tr.at("build D1")
    cd1 = tr.add(tr.xor(x12, k("M")), k("X11+1"))
    bd1 = tr.rot(tr.xor(cd1, k("S6")), 12)
    tr.store(tr.rot(tr.xor(bd1, k("X11")), 7))
    dd1 = tr.add(cd1, k("-S11"))
    tr.store(tr.band(tr.xor(tr.rol(x12, 8), dd1), k("M")))
    tr.store(tr.rol(dd1, 16))
    return tr


def my_middle_step(c):
    """middle_step, transcribed, including the class-loop entry that loads the nine resident words."""
    tr = Tr(c)
    k = tr.k

    def put(name, v):
        tr.store(v)

    def low(v):
        return tr.band(v, k("M"))

    def neg(v, plus="1"):
        return tr.add(tr.xor(v, k("M")), k(plus))

    tr.at("next X2")
    tr.keep("M", "1", "A16", "B16")
    x2 = low(tr.add(k("X2"), k("1")))
    tr.cmpbr(x2, k("X2 end"))
    put("X2", x2)
    put("X2+w7", low(tr.add(x2, k("w7"))))
    tr.at("D2 and K1")
    d2a = tr.add(x2, k("-D2.b1-W13"))
    d2d = tr.xor(x2, k("ROL(X13,8)"))
    s13 = tr.xor(tr.rol(d2d, 16), d2a)
    k1c = neg(s13, "S9+1")
    k1d = tr.add(k1c, k("-IV1"))
    s1 = tr.xor(tr.rol(s13, 8), k1d)
    put("w12-S1-S6", low(tr.add(tr.add(d2a, k("-S2-S7")), neg(s1, "1-S6"))))
    k1a = tr.rol(k1d, 16)
    put("-w2", low(neg(k1a, "IV1+IV5+1")))
    k1b = tr.rot(tr.xor(k1c, k("IV5")), 12)
    put("w3", low(tr.add(s1, neg(tr.add(k1a, k1b)))))
    put("S5", tr.rot(tr.xor(k1b, k("S9")), 7))
    tr.at("K0")
    s8 = neg(d2d, "D2.c1+1")
    k0b = tr.xor(s8, k("ROL(S4,7)"))
    k0c = tr.xor(tr.rol(k0b, 12), k("IV4"))
    s12 = low(tr.add(s8, neg(k0c)))
    put("S12", s12)
    k0d = tr.add(k0c, k("-IV0"))
    k0a = tr.rol(k0d, 16)
    put("w0", low(tr.add(k0a, k("-IV0-IV4"))))
    s0 = tr.xor(tr.rol(s12, 8), k0d)
    put("w1", low(tr.add(s0, neg(tr.add(k0a, k0b)))))
    tr.at("class loop entry")
    tr.drop(*list(tr.reg))
    tr.keep(*RESIDENT)
    return tr
