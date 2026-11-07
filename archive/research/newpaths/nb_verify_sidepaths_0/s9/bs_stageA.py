"""S9 skeptic check: stage A of the filed search (pkg10 proof.md 6.5) in BITSLICED form, 256 trials per 256-bit word.

What it does (COMPUTED when run):
1. Real trials: for a random context (Cc1, Cd1, D3d1, S15, S9, w5, X2 with bits 14,30,31 zero) and 256 representative
   members (one bitsliced word: member bits 0..7 vary, bits 8..14 fixed, bits 10,15,16 zero), the 55-byte message A is
   built by the filed construction (fam55_copy = research/newpaths/sidepaths/fam55.py, unchanged copy) and compressed
   in full; h1 of E3 is read from the real compression, and the gate (4 conditions) and rule A (8 conditions) are
   evaluated on it.
2. Bitsliced program: one straight-line program over 256-bit slices computes X0, X10, C2 (a1, d1, c1, b1, a2), z and
   the gate and rule-A lane masks from the table slices XA[0..31], X6[0..31]. Every AND/OR/XOR on 256-bit words is one
   operation; rotations are free (renaming). Three designs:
     J  per-X2 code specialisation (JIT): all run-time constants folded into the code, slice polarities tracked,
        so XOR with a constant costs nothing and a constant addition costs 1-2 ops per bit.
     D  static code, constant additions dispatched per 8-bit chunk (computed jump, 2 units per chunk), every slice
        normalised to true polarity at the end of each chunk adder (one XOR with ONES per inverted slice).
     G  generic: constant bits are loaded slices (all-0 / all-1 words, precomputed per X2), no specialisation.
3. Register model: R registers for the program's values (filed machine: 16, two kept for list position and count,
   so R = 14). Loads/stores are counted by Belady's furthest-next-use eviction over the fixed instruction order
   (a computed value evicted while still needed is stored once; every fetch of a memory value is one load).
4. Every lane's gate and rule-A bit from the bitsliced program is compared with the real h1 of the real message.
Writes nothing outside this folder."""
import os
import random
import struct
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fam55_copy as F  # noqa: E402

M = F.M
FULL = (1 << 256) - 1
ror, rol = F.ror, F.rol
FREE = [i for i in range(32) if not F.SUB_AND >> i & 1]          # 17 free positions of e1 in the sub-class
ZBITS = (2, 3, 4, 5, 8, 9, 16, 17, 24, 25, 26, 27, 30)          # bits of z that rule A reads (Lemma A)


# ----------------------------------------------------------------------------------------------- real trials
def build_full(Cc1, Cd1, D3d1, S15, S9, w5, X2, y):
    """fam55.build with the intermediate names returned (same lines)."""
    IV, W4, W13, X3, X7, X11, X15 = F.IV, F.W4, F.W13, F.X3, F.X7, F.X11, F.X15
    K2a1 = (IV[2] + IV[6] + W4) & M; K2d1 = ror(55 ^ K2a1, 16)
    K2c1 = (IV[2] + K2d1) & M; K2b1 = ror(IV[6] ^ K2c1, 12)
    S2 = (K2a1 + K2b1 + w5) & M; S14 = ror(K2d1 ^ S2, 8)
    S10 = (K2c1 + S14) & M; S6 = ror(K2b1 ^ S10, 7)
    D3a1 = rol(D3d1, 16) ^ S14; D3c1 = (S9 + D3d1) & M
    D3b1 = (X3 - D3a1) & M; S4 = rol(D3b1, 12) ^ D3c1
    S3 = (D3a1 - S4) & M; X14 = ror(D3d1 ^ X3, 8)
    X9 = (D3c1 + X14) & M; X4 = ror(D3b1 ^ X9, 7)
    K3d1 = rol(S15, 8) ^ S3; K3c1 = (IV[3] + K3d1) & M
    K3b1 = ror(IV[7] ^ K3c1, 12); S11 = (K3c1 + S15) & M
    S7 = ror(K3b1 ^ S11, 7); K3a1 = rol(K3d1, 16) ^ 11
    w6 = (K3a1 - IV[3] - IV[7]) & M; w7 = (S3 - K3a1 - K3b1) & M
    X8 = (Cc1 - Cd1) & M; C0b1 = ror(X4 ^ Cc1, 12)
    D2b1 = rol(X7, 7) ^ X8; D2c1 = rol(D2b1, 12) ^ S7
    X13 = (X8 - D2c1) & M
    D2a1 = (X2 - D2b1 - W13) & M; D2d1 = rol(X13, 8) ^ X2
    S13 = rol(D2d1, 16) ^ D2a1; S8 = (D2c1 - D2d1) & M
    K1c1 = (S9 - S13) & M; K1d1 = (K1c1 - IV[1]) & M
    K1a1 = rol(K1d1, 16)
    w2 = (K1a1 - IV[1] - IV[5]) & M
    K0b1 = rol(S4, 7) ^ S8; K0c1 = rol(K0b1, 12) ^ IV[4]
    K0d1 = (K0c1 - IV[0]) & M; K0a1 = rol(K0d1, 16)
    w0 = (K0a1 - IV[0] - IV[4]) & M
    Y8 = rol(y, 7) ^ C0b1; Y12 = (Y8 - Cc1) & M
    Y0 = rol(Y12, 8) ^ Cd1; C0a1 = (Y0 - C0b1 - w6) & M
    X12 = rol(Cd1, 16) ^ C0a1
    D1c1 = (X11 - X12) & M; D1b1 = ror(S6 ^ D1c1, 12)
    X6 = ror(D1b1 ^ X11, 7)
    return dict(S10=S10, X14=X14, X4=X4, w7=w7, w2=w2, w0=w0, C0a1=C0a1, X6=X6)


def real_h1(words):
    """h1 of E3 on message A (55 bytes) from the full 2-round compression, and the digest (for a cross-check)."""
    v = list(F.IV) + list(F.IV[:4]) + [0, 0, 55, 11]
    s = list(words)
    cols = ((0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15))
    diags = ((0, 5, 10, 15), (1, 6, 11, 12), (2, 7, 8, 13), (3, 4, 9, 14))
    for r in range(2):
        for i, (a, b, c, d) in enumerate(cols):
            v[a], v[b], v[c], v[d] = F.G(v[a], v[b], v[c], v[d], s[2 * i], s[2 * i + 1])
        if r == 1:
            Y = list(v)
            e1 = (Y[3] + Y[4] + s[14]) & M
            h1 = ror(Y[14] ^ e1, 16)
        for i, (a, b, c, d) in enumerate(diags):
            v[a], v[b], v[c], v[d] = F.G(v[a], v[b], v[c], v[d], s[8 + 2 * i], s[8 + 2 * i + 1])
        s = [s[p] for p in F.PERM]
    digest = struct.pack("<8I", *(v[i] ^ v[i + 8] for i in range(8)))
    return h1, Y[4], digest


def rule_on_h1(h):
    b = [h >> i & 1 for i in range(32)]
    gate = b[0] == 0 and b[1] == 1 and b[16] == 0 and b[17] == 0
    rule = gate and b[2] ^ b[10] == 1 and b[3] ^ b[11] == 1 and b[3] ^ b[12] ^ b[24] == 0 and b[6] ^ b[13] ^ b[25] == 0
    return gate, rule


def member_y(k):
    e1 = F.CLASS_VAL
    for j, p in enumerate(FREE):
        if k >> j & 1:
            e1 |= 1 << p
    return (e1 - F.Y3A) & M, e1


# ----------------------------------------------------------------------------------------------- slice program
class Node:
    __slots__ = ("kind", "op", "srcs", "val", "name")

    def __init__(self, kind, op, srcs, val, name=""):
        self.kind, self.op, self.srcs, self.val, self.name = kind, op, srcs, val, name


class Lit:
    """A slice: physical node (None = the zero word) and a polarity (true value = phys XOR (ONES if pol))."""
    __slots__ = ("node", "pol")

    def __init__(self, node, pol):
        self.node, self.pol = node, pol


class Prog:
    def __init__(self, normalise_ones_in_register=True):
        self.nodes = []
        self.instr = []          # emitted operation nodes, in order
        self.extra_ops = 0       # operations not on slices (tests, branches, loop control, dispatch)
        self.extra_loads = 0

    def mem(self, val, name):
        n = Node("mem", None, (), val, name)
        self.nodes.append(n)
        return Lit(n, 0)

    @staticmethod
    def const(b):
        return Lit(None, b & 1)

    def emit(self, op, a, b):
        va, vb = a.val, b.val
        val = va ^ vb if op == "xor" else va & vb if op == "and" else va | vb
        n = Node("op", op, (a, b), val)
        self.nodes.append(n)
        self.instr.append(n)
        return n

    def value(self, x):
        return (x.node.val if x.node is not None else 0) ^ (FULL if x.pol else 0)

    @staticmethod
    def inv(x):
        return Lit(x.node, x.pol ^ 1)

    def xor(self, x, y):
        if x.node is None:
            return Lit(y.node, y.pol ^ x.pol)
        if y.node is None:
            return Lit(x.node, x.pol ^ y.pol)
        if x.node is y.node:
            return self.const(x.pol ^ y.pol)
        return Lit(self.emit("xor", x.node, y.node), x.pol ^ y.pol)

    def and_(self, x, y):
        if x.node is None:
            return y if x.pol else self.const(0)
        if y.node is None:
            return x if y.pol else self.const(0)
        if x.node is y.node:
            return x if x.pol == y.pol else self.const(0)
        if x.pol == y.pol == 0:
            return Lit(self.emit("and", x.node, y.node), 0)
        if x.pol == y.pol == 1:
            return Lit(self.emit("or", x.node, y.node), 1)
        a, b = (x.node, y.node) if x.pol == 1 else (y.node, x.node)      # ~a & b = (a & b) ^ b
        t = self.emit("and", a, b)
        return Lit(self.emit("xor", t, b), 0)

    def or_(self, x, y):
        return self.inv(self.and_(self.inv(x), self.inv(y)))

    def normalise(self, x):
        """Bring a slice to true polarity: one XOR with the ONES word (kept in a register) when inverted."""
        if x.node is None or x.pol == 0:
            return x
        ones = self.ones
        return Lit(self.emit("xor", x.node, ones.node), 0)

    # --- adders -------------------------------------------------------------------------------------------
    def step_const(self, a, k, c, need_sum=True, need_carry=True):
        """a + k (k a code constant bit) with carry-in c: returns (sum or None, carry or None)."""
        s = self.xor(self.xor(a, c), self.const(k)) if need_sum else None
        cy = (self.or_(a, c) if k else self.and_(a, c)) if need_carry else None
        return s, cy

    def step_var(self, a, b, c, need_sum=True, need_carry=True):
        """Full adder on three slices; majority as ((x^z)&(y^z))^z with z chosen so that the AND's inputs have
        equal polarity (1 operation)."""
        if c.node is None and c.pol == 0:
            s = self.xor(a, b) if need_sum else None
            cy = self.and_(a, b) if need_carry else None
            return s, cy
        la = [a, b, c]
        p = [t.pol for t in la]
        if p[0] == p[1]:
            zi = 2
        elif p[0] == p[2]:
            zi = 1
        else:
            zi = 0
        z = la[zi]
        x, y = [la[i] for i in range(3) if i != zi]
        xz = self.xor(x, z)
        s = self.xor(xz, y) if need_sum else None
        cy = None
        if need_carry:
            yz = self.xor(y, z)
            cy = self.xor(self.and_(xz, yz), z)
        return s, cy


def ctx_constants(ctx):
    """Run-time constants of stage A for a context (outer step + X2)."""
    d = build_full(*ctx, y=0)
    K0 = (-d["w2"]) & M
    K1 = (ctx[6] + d["w7"]) & M
    K2 = (d["S10"] + F.X15) & M
    K3 = (K1 + d["w0"]) & M
    return dict(K0=K0, K1=K1, K2=K2, K3=K3, X14=d["X14"], C15=rol(F.X15, 8), X4=d["X4"])


def build_program(design, consts, XA_sl, X6_sl, e27, e28, e29):
    """Emit the bitsliced stage A. XA_sl, X6_sl: 32 slice values each (bit b of every lane). Returns (prog, gate Lit,
    pass Lit, dispatch units)."""
    P = Prog()
    P.ones = P.mem(FULL, "ONES") if design in ("D",) else None
    XA = [P.mem(XA_sl[b], "XA%d" % b) for b in range(32)]
    X6 = [P.mem(X6_sl[b], "X6%d" % b) for b in range(32)]
    dispatch = 0
    if design == "G":
        Ksl = {name: [P.mem(FULL if consts[name] >> b & 1 else 0, "%s%d" % (name, b)) for b in range(32)]
               for name in ("K0", "K1", "K2", "K3", "X14")}

    def cadd_step(a, name, i, c, need_sum=True, need_carry=True):
        k = consts[name] >> i & 1
        if design == "G":
            return P.step_var(a, Ksl[name][i], c, need_sum, need_carry)
        return P.step_const(a, k, c, need_sum, need_carry)

    def norm(x):
        return P.normalise(x) if design == "D" else x

    def cxor(a, name, i):
        """XOR with a run-time constant (X14, per outer step)."""
        if design == "G":
            return P.xor(a, Ksl[name][i])
        return P.xor(a, P.const(consts[name] >> i & 1))

    # Phase 1: a1 = X6 + K1 (32 bits); d1 = ROR(a1 ^ X14, 16)
    a1 = [None] * 32
    c = P.const(0)
    for i in range(32):
        s, c = cadd_step(X6[i], "K1", i, c, True, i < 31)
        a1[i] = s
        if design == "D" and i % 8 == 7:
            a1[i - 7:i + 1] = [norm(t) for t in a1[i - 7:i + 1]]
            if c is not None:
                c = norm(c)
    if design == "D":
        dispatch += 2 * 4
    ax = [cxor(a1[i], "X14", i) for i in range(32)]
    if design == "D":
        ax = [norm(t) for t in ax]
    d1 = [ax[(i + 16) % 32] for i in range(32)]

    # Phase 2: X0 = XA + K0; D0.d1 = X0 ^ ROL(X15,8) (pinned: compile-time); X10 = D0.d1 + K2; c1 = X10 + d1
    c1 = [None] * 32
    cx0 = cx10 = cc1 = P.const(0)
    for i in range(32):
        x0, cx0 = cadd_step(XA[i], "K0", i, cx0, True, i < 31)
        if design == "D" and True:
            pass
        dd = P.xor(x0, P.const(consts["C15"] >> i & 1))
        x10, cx10 = cadd_step(dd, "K2", i, cx10, True, i < 31)
        if design == "D":
            x10 = norm(x10)
            if i % 8 == 7 and cx10 is not None:
                cx10 = norm(cx10)
                cx0 = norm(cx0) if cx0 is not None else None
        s, cc1 = P.step_var(x10, d1[i], cc1, i != 11, i < 31)
        c1[i] = s
    if design == "D":
        dispatch += 2 * 4 * 2       # K0 and K2 adders: 4 chunks each
    # Phase 3: A = X6 + K3 (= a1 + w0); b1 = ROR(X6 ^ c1, 12); a2 = A + b1 (bits 0..30); z = a2 ^ d1
    z = {}
    cA = ca2 = P.const(0)
    for i in range(31):
        A, cA = cadd_step(X6[i], "K3", i, cA, True, i < 30)
        if design == "D":
            A = norm(A)
            if i % 8 == 7 and cA is not None:
                cA = norm(cA)
        b1 = P.xor(X6[(i + 12) % 32], c1[(i + 12) % 32])
        s, ca2 = P.step_var(A, b1, ca2, i in ZBITS, i < 30)
        if i in ZBITS:
            z[i] = P.xor(s, d1[i])
    if design == "D":
        dispatch += 2 * 4
    # Phase 4: gate and rule A (Lemma A (b)); e27..e29 are fixed per word (code variant per word group)
    gate = P.and_(P.and_(P.inv(z[24]), z[25]), P.and_(z[8], z[9]))
    t1 = P.inv(P.xor(z[26], z[2]))                                   # z26 ^ z2 = 0
    t2 = P.xor(P.xor(z[27], z[3]), P.const(1 ^ e27))                 # z27 ^ z3 = e27
    t3 = P.xor(P.xor(P.xor(z[27], z[4]), z[16]), P.const(1 ^ e28))   # z27 ^ z4 ^ z16 = e28
    t4 = P.xor(P.xor(P.xor(z[30], z[5]), z[17]), P.const(e29))       # z30 ^ z5 ^ z17 = 1 ^ e29
    rest = P.and_(P.and_(t1, t2), P.and_(t3, t4))
    passed = P.and_(gate, rest)
    return P, gate, passed, dispatch


def belady(prog, outputs, R):
    """Loads and stores of the instruction sequence with R registers, Belady (furthest next use) eviction.
    Sources must be in registers; the result may take the register of a source used for the last time here."""
    seq = prog.instr
    uses = {}
    for t, n in enumerate(seq):
        for s in n.srcs:
            uses.setdefault(id(s), []).append(t)
    for o in outputs:
        if o.node is not None:
            uses.setdefault(id(o.node), []).append(len(seq))
    ptr = {k: 0 for k in uses}

    def next_use(nid, t):
        lst = uses.get(nid, [])
        i = ptr.get(nid, 0)
        while i < len(lst) and lst[i] <= t:
            i += 1
        ptr[nid] = i
        return lst[i] if i < len(lst) else None

    inreg = {}           # id -> node
    stored = set()       # computed nodes already in memory
    loads = stores = 0
    peak = 0

    def evict(t, protect):
        nonlocal stores
        best, bestd = None, -1
        for nid, n in inreg.items():
            if nid in protect:
                continue
            nu = next_use(nid, t - 1)
            d = 10 ** 9 if nu is None else nu
            if d > bestd:
                best, bestd = nid, d
        n = inreg.pop(best)
        if n.kind == "op" and bestd < 10 ** 9 and best not in stored:
            stores += 1
            stored.add(best)

    for t, n in enumerate(seq):
        protect = {id(s) for s in n.srcs}
        for s in n.srcs:
            if id(s) not in inreg:
                while len(inreg) >= R:
                    evict(t, protect)
                inreg[id(s)] = s
                loads += 1
        # free sources whose last use is now
        for s in n.srcs:
            if id(s) in inreg and next_use(id(s), t) is None:
                inreg.pop(id(s))
        while len(inreg) >= R:
            evict(t, set())
        inreg[id(n)] = n
        peak = max(peak, len(inreg))
        # drop dead values
        for nid in [k for k in inreg if next_use(k, t) is None]:
            inreg.pop(nid)
    for o in outputs:                      # the two tests read the masks: a load if a mask was spilled
        if o.node is not None and id(o.node) not in inreg:
            loads += 1
    return loads, stores


def run(design, ctx, word_bits, R, check=True):
    """One bitsliced word: 256 representatives (member bits 0..7 = lane, bits 8,9,11,12,13,14 = word_bits)."""
    consts = ctx_constants(ctx)
    lanes = []
    for lane in range(256):
        k = lane | word_bits
        y, e1 = member_y(k)
        lanes.append((k, y, e1))
    e27, e28, e29 = (lanes[0][2] >> 27 & 1, lanes[0][2] >> 28 & 1, lanes[0][2] >> 29 & 1)
    assert all((e >> 27 & 7) == (lanes[0][2] >> 27 & 7) for _, _, e in lanes)
    XA = [0] * 32
    X6 = [0] * 32
    real = []
    for L, (k, y, e1) in enumerate(lanes):
        d = build_full(*ctx, y=y)
        xa = (d["C0a1"] - d["X4"]) & M
        for b in range(32):
            XA[b] |= (xa >> b & 1) << L
            X6[b] |= (d["X6"] >> b & 1) << L
        if check:
            words = F.build(*ctx, y)
            h1, y4, digest = real_h1(words)
            assert y4 == y
            A, _ = F.pair(words)
            assert digest == F.hash2(A)
            real.append(rule_on_h1(h1))
    P, gate, passed, dispatch = build_program(design, consts, XA, X6, e27, e28, e29)
    ops = len(P.instr)
    loads, stores = belady(P, [gate, passed], R)
    right = 0
    if check:
        gv, pv = P.value(gate), P.value(passed)
        for L in range(256):
            right += int(((gv >> L & 1) == real[L][0]) and ((pv >> L & 1) == real[L][1]))
        n_gate = sum(r[0] for r in real)
        n_pass = sum(r[1] for r in real)
    else:
        n_gate = n_pass = None
    # tests and loop control: two tests (compare+branch each), loop 3 ops + 1 load (as the filed "loop" part)
    tail = 2 + 2 + 3 + 1
    return dict(ops=ops, loads=loads, stores=stores, dispatch=dispatch, tail=tail,
                total=ops + loads + stores + dispatch + tail, right=right, n_gate=n_gate, n_pass=n_pass)


def rand_ctx(rng):
    ctx = [rng.randrange(1 << 32) for _ in range(7)]
    ctx[6] &= ~((1 << 14) | (1 << 30) | (1 << 31)) & M    # representative X2
    return ctx


def rand_word_bits(rng):
    wb = 0
    for j in (8, 9, 11, 12, 13, 14):
        if rng.randrange(2):
            wb |= 1 << j
    return wb


def extreme(rng, n, R):
    """Upper end of the count over run-time constants: K0, K1, K2, K3, X14 drawn from extreme patterns."""
    pats = (0, M, 0x55555555, 0xAAAAAAAA, 0x0F0F0F0F, 0xF0F0F0F0, 0x00FF00FF, 0xFF00FF00, 0x80000000, 0x7FFFFFFF, 1)
    dummy = [0] * 32
    out = {}
    for design in ("J", "D", "G"):
        worst = 0
        for _ in range(n):
            consts = {name: (rng.choice(pats) if rng.random() < 0.8 else rng.randrange(1 << 32))
                      for name in ("K0", "K1", "K2", "K3", "X14")}
            consts["C15"] = rol(F.X15, 8)
            e = [rng.randrange(2) for _ in range(3)]
            P, g, p, disp = build_program(design, consts, dummy, dummy, *e)
            lo, st = belady(P, [g, p], R)
            worst = max(worst, len(P.instr) + lo + st + disp + 8)
        out[design] = worst
    return out


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "extreme":
        rng = random.Random(int(sys.argv[2]))
        for R in (14, 16):
            w = extreme(rng, int(sys.argv[3]), R)
            print("R=%d worst total over extreme constants: %s  (per trial: %s)" % (
                R, w, {k: round(v / 256, 3) for k, v in w.items()}))
        sys.exit(0)
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    n_ctx = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    n_cnt = int(sys.argv[3]) if len(sys.argv) > 3 else 200
    rng = random.Random(seed)
    print("S9 bitsliced stage A, seed %d" % seed)
    # correctness on real messages
    tot_right = tot_lanes = tot_gate = tot_pass = 0
    for c in range(n_ctx):
        ctx, wb = rand_ctx(rng), rand_word_bits(rng)
        for design in ("J", "D", "G"):
            r = run(design, ctx, wb, 14, check=True)
            tot_right += r["right"]
            tot_lanes += 256
            if design == "J":
                tot_gate += r["n_gate"]
                tot_pass += r["n_pass"]
    print("correctness: %d of %d lanes right (gate and rule A vs real h1 of the real message); "
          "real gate opens %d, rule A passes %d in %d lanes" % (tot_right, tot_lanes, tot_gate, tot_pass,
                                                                  tot_lanes // 3))
    # counts over many contexts (no message check: counts depend on constants only)
    for R in (14, 16, 12):
        for design in ("J", "D", "G"):
            rows = []
            for c in range(n_cnt):
                ctx, wb = rand_ctx(rng), rand_word_bits(rng)
                rows.append(run(design, ctx, wb, R, check=False))
            def stat(key):
                v = [r[key] for r in rows]
                return sum(v) / len(v), min(v), max(v)
            o, l, s, t = stat("ops"), stat("loads"), stat("stores"), stat("total")
            print("R=%2d design %s: ops %.1f [%d,%d]  loads %.1f [%d,%d]  stores %.1f [%d,%d]  dispatch %d  tail %d  "
                  "TOTAL %.1f [%d,%d] = %.3f per trial (max %.3f)" % (
                      R, design, o[0], o[1], o[2], l[0], l[1], l[2], s[0], s[1], s[2], rows[0]["dispatch"],
                      rows[0]["tail"], t[0], t[1], t[2], t[0] / 256, t[2] / 256))
