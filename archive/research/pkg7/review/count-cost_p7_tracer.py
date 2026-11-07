#!/usr/bin/env python3
"""Reviewer (lens: count and cost) tracer for research/pkg7 (DRAFT).

Runs the four counted pieces of blake3-r2/experiments/halfsearch.py on a recording machine written here
(class Trace: none of the program's Machine code is used), then

  1. counts operations, loads and stores per part from the recorded instruction list;
  2. simulates a register file on the instruction list (values freed at their last use, an operation may write
     over an operand that dies in it; kept words held as the program declares, i.e. up to its drop());
  3. checks every lane against a 2-round BLAKE3 compression written here from the specification, on the real
     55 and 63 byte messages of the lane's trial: member, half-collision, rule A on h1 as typed from proof.md
     6.3, the stage-2 word against D3 XOR ROL(D6, 8) of the two digests;
  4. repeats the count for the same source with the line KEPT = 9 replaced by KEPT = 0.

usage: python -B count-cost_p7_tracer.py CASES SEED
"""
import importlib.util
import pathlib
import random
import struct
import sys
import types

HERE = pathlib.Path(__file__).resolve().parent
PROGRAM = HERE.parent / "blake3-r2" / "experiments" / "halfsearch.py"
LANES, LB = 7, 36
WORD = (1 << 256) - 1
M32 = 0xFFFFFFFF


def load_program(kept=None):
    src = PROGRAM.read_text(encoding="utf-8")
    if kept is not None:
        if src.count("\nKEPT = 9\n") != 1:
            raise SystemExit("the line KEPT = 9 was not found once")
        src = src.replace("\nKEPT = 9\n", "\nKEPT = %d\n" % kept)
    mod = types.ModuleType("hs_kept_%s" % kept)
    mod.__file__ = str(PROGRAM)
    sys.modules[mod.__name__] = mod
    exec(compile(src, str(PROGRAM), "exec"), mod.__dict__)
    return mod


class Val:
    __slots__ = ("z", "id", "counter")

    def __init__(self, z, i, counter=False):
        self.z, self.id, self.counter = z, i, counter


class Trace:
    """Records LOAD / OP / OPC (counter) / CMPBR / STORE / USE / DROP with the part they belong to."""

    def __init__(self):
        self.ins, self.kept, self.memory, self.part, self.n = [], {}, {}, None, 0
        self.live_in, self.live_out, self.maxlane = [], [], {}

    def _new(self, z, counter=False):
        self.n += 1
        return Val(z, self.n, counter)

    def at(self, part):
        self.part = part
        self.maxlane.setdefault(part, 0)

    def load(self, constant):
        v = self._new(constant)
        self.ins.append(("LOAD", self.part, v, (), None))
        return v

    def k(self, name):
        if name in self.kept:
            self.ins.append(("USE", self.part, None, (self.kept[name],), name))
            return self.kept[name]
        v = self._new(self.memory[name])
        self.ins.append(("LOAD", self.part, v, (), name))
        return v

    def get(self, *names):
        if self.kept_mode == 0:
            return
        for name in names:
            if name not in self.kept:
                v = self._new(self.memory[name])
                self.ins.append(("LOAD", self.part, v, (), name))
                self.kept[name] = v

    def drop(self, names):
        for name in names:
            if name in self.kept:
                self.ins.append(("DROP", self.part, None, (self.kept.pop(name),), name))

    def resident(self, names):
        for name in names:
            v = self._new(self.memory[name])
            self.live_in.append(v)
            self.kept[name] = v

    def finish(self, names=()):
        if set(self.kept) != set(names) or any(self.kept[x].z != self.memory[x] for x in names):
            raise SystemExit("kept words at the end of a piece are not the declared ones")
        self.live_out = list(self.kept.values())

    def store(self, x):
        self.ins.append(("STORE", self.part, None, (x,), None))
        return x.z

    def _op(self, z, *used):
        v = self._new(z)
        self.ins.append(("OP", self.part, v, used, None))
        return v

    def add(self, x, y):
        big = max(((x.z >> LB * i) & (1 << LB) - 1) + ((y.z >> LB * i) & (1 << LB) - 1) for i in range(LANES))
        self.maxlane[self.part] = max(self.maxlane[self.part], big)
        return self._op((x.z + y.z) & WORD, x, y)

    def xor(self, x, y):
        return self._op(x.z ^ y.z, x, y)

    def band(self, x, y):
        return self._op(x.z & y.z, x, y)

    def bor(self, x, y):
        return self._op(x.z | y.z, x, y)

    def shr(self, x, r):
        return self._op(x.z >> r, x)

    def shl(self, x, r):
        return self._op((x.z << r) & WORD, x)

    def pror(self, z, r):
        low = self.band(self.shr(z, r), self.k("A%d" % r))
        high = self.band(self.shl(z, 32 - r), self.k("B%d" % r))
        return self.bor(low, high)

    def prol(self, z, r):
        return self.pror(z, 32 - r)

    def advance(self, position):
        v = self._new(position + 1, counter=True)
        self.ins.append(("OPC", self.part, v, (), None))
        return v

    def compare_and_branch(self, x, y):
        self.ins.append(("CMPBR", self.part, None, (x, y), None))
        return x.z != y.z

    # ---------------------------------------------------------------- analysis
    def counts(self):
        out = {}
        for kind, part, _, _, _ in self.ins:
            c = out.setdefault(part, [0, 0, 0, 0, 0])      # ops, loads, stores, uses of kept words, list/table loads
            if kind in ("OP", "OPC"):
                c[0] += 1
            elif kind == "CMPBR":
                c[0] += 2
            elif kind == "LOAD":
                c[1] += 1
            elif kind == "STORE":
                c[2] += 1
            elif kind == "USE":
                c[3] += 1
        for kind, part, _, _, name in self.ins:
            if kind == "LOAD" and name is None:
                out[part][4] += 1
        return out

    def registers(self, declared=True):
        """Peak number of general registers, plus the two counters."""
        last = {}
        for idx, (kind, _, out, used, _) in enumerate(self.ins):
            for v in used:
                if v.counter:
                    continue
                if kind == "DROP":
                    if declared:
                        last[v.id] = idx
                else:
                    last[v.id] = idx
        end = len(self.ins)
        for v in self.live_out:
            last[v.id] = end
        held = {v.id for v in self.live_in}
        peak = len(held)
        for idx, (kind, _, out, used, _) in enumerate(self.ins):
            if kind == "DROP" and not declared:
                continue
            for v in used:
                if not v.counter and v.id not in held:
                    raise SystemExit("an operand is not in a register at instruction %d (%s)" % (idx, kind))
            for v in used:
                if not v.counter and last[v.id] == idx:
                    held.discard(v.id)
            if out is not None and not out.counter:
                if out.id not in last:
                    raise SystemExit("a value is made and never used at instruction %d" % idx)
                held.add(out.id)
            peak = max(peak, len(held))
        left = held - {v.id for v in self.live_out}
        if left:
            raise SystemExit("values left in registers at the end")
        return peak + 2


# ---------------------------------------------------------------- 2-round BLAKE3 from the specification
IV = (0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19)
PERM = (2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8)


def rotr(x, r):
    return ((x >> r) | (x << (32 - r))) & M32


def gmix(v, a, b, c, d, x, y):
    v[a] = (v[a] + v[b] + x) & M32; v[d] = rotr(v[d] ^ v[a], 16)
    v[c] = (v[c] + v[d]) & M32; v[b] = rotr(v[b] ^ v[c], 12)
    v[a] = (v[a] + v[b] + y) & M32; v[d] = rotr(v[d] ^ v[a], 8)
    v[c] = (v[c] + v[d]) & M32; v[b] = rotr(v[b] ^ v[c], 7)


def compress2(message):
    """Root compression of a one-block message with 2 rounds: (digest words, state after the column step of the
    second round, the permuted message of the second round)."""
    block = message + bytes(64 - len(message))
    m = list(struct.unpack("<16I", block))
    v = list(IV) + list(IV[:4]) + [0, 0, len(message), 1 | 2 | 8]
    ycol = mp = None
    for r in range(2):
        gmix(v, 0, 4, 8, 12, m[0], m[1]); gmix(v, 1, 5, 9, 13, m[2], m[3])
        gmix(v, 2, 6, 10, 14, m[4], m[5]); gmix(v, 3, 7, 11, 15, m[6], m[7])
        if r == 1:
            ycol, mp = list(v), list(m)
        gmix(v, 0, 5, 10, 15, m[8], m[9]); gmix(v, 1, 6, 11, 12, m[10], m[11])
        gmix(v, 2, 7, 8, 13, m[12], m[13]); gmix(v, 3, 4, 9, 14, m[14], m[15])
        m = [m[PERM[i]] for i in range(16)]
    return [v[i] ^ v[i + 8] for i in range(8)], ycol, mp


def rule_a_text(h1):
    h = [(h1 >> i) & 1 for i in range(32)]
    return (h[0] == 0 and h[1] == 1 and h[16] == 0 and h[17] == 0 and h[2] ^ h[10] == 1 and h[3] ^ h[11] == 1
            and h[3] ^ h[12] ^ h[24] == 0 and h[6] ^ h[13] ^ h[25] == 0)


FREE_POS = [2, 3, 4, 5, 6, 7, 10, 11, 12, 13, 14, 20, 27, 28, 29, 30, 31]      # Lemma Q2
Y3 = 0x8127C181


def member_text(k):
    e1 = 0x030C0303
    for t, pos in enumerate(FREE_POS):
        e1 |= ((k >> t) & 1) << pos
    return (e1 - Y3) & M32


# The tables of proof.md 6.5, typed here: part -> (operations, loads, stores)
TEXT = {
    "batch": {"loop": (3, 1, 0), "X0 to X10": (3, 4, 0), "C2 to z": (17, 4, 0), "rule A": (14, 1, 0),
              "entry count": (3, 1, 0), "C2, rest": (17, 7, 0), "C1 to Y1": (31, 8, 0), "E1, A and B": (41, 6, 0),
              "E1 test": (13, 4, 0), "restore": (0, 4, 0)},
    "table build": {"build loop": (3, 1, 0), "build C0": (13, 11, 2), "build D1": (27, 14, 3)},
    "middle step": {"next X2": (6, 7, 2), "D2 and K1": (47, 15, 4), "K0": (32, 9, 3), "class loop entry": (0, 9, 0)},
    "outer step": {"next w5": (6, 6, 2), "K2 and D3": (67, 39, 9), "K3": (43, 25, 4), "C0 and D2": (32, 21, 6)},
}
STAGE_A = ("loop", "X0 to X10", "C2 to z", "rule A")
TEXT_REG = {"batch": 16, "outer step": 11, "table build": 7, "middle step": 13}


def run(hs, cases, seed, kept_mode, check_text):
    rng = random.Random(seed)
    seen, regs, regs_min, biggest = {}, {}, {}, {}
    lanes_ok = lanes_all = pass_lanes = pass_batches = zero_words = 0
    wrong = []
    for case in range(cases):
        free = [rng.getrandbits(32) for _ in range(7)]
        if case % 5 == 4:
            free = [rng.choice((0, M32, x)) for x in free]
        j = 18724 if case % 4 == 3 else rng.randrange(18725)
        c = hs.memory(free)
        pieces = {}
        for name in ("outer step", "table build", "middle step", "batch"):
            t = Trace()
            t.kept_mode = kept_mode
            if name == "outer step":
                hs.outer_step(t, c)
            elif name == "table build":
                row = hs.table_build(t, c, j)
            elif name == "middle step":
                hs.middle_step(t, c)
            else:
                res = hs.packed_batch(t, c, row, j, case)
            pieces[name] = t
            cnt = {p: tuple(v) for p, v in t.counts().items()}
            if seen.setdefault(name, cnt) != cnt:
                wrong.append("counts differ between cases in " + name)
            regs[name] = max(regs.get(name, 0), t.registers(True))
            regs_min[name] = max(regs_min.get(name, 0), t.registers(False))
            for p, v in t.maxlane.items():
                biggest[p] = max(biggest.get(p, 0), v)
        words, flags, taken, flags_a, taken_a = res
        v = hs.context(free)
        for i in range(LANES):
            k = min(7 * j + i, 131071)
            y4 = member_text(k)
            w, _ = hs.trial(v, y4)
            a, b = hs.messages(w)
            da, ycol, mp = compress2(a)
            db, ycolb, _ = compress2(b)
            e1 = (ycol[3] + ycol[4] + mp[14]) & M32
            h1 = rotr(ycol[14] ^ e1, 16)
            n = (da[3] ^ db[3]) ^ (((da[6] ^ db[6]) << 8 | (da[6] ^ db[6]) >> 24) & M32)
            good = (len(a) == 55 and len(b) == 63 and a != b and ycol[4] == y4 and ycolb[4] == y4
                    and (e1 & 0x07EF8303) == 0x030C0303 and ycol[3] == Y3
                    and all(da[t] == db[t] for t in (0, 2, 5, 7))
                    and (flags_a[i] == 0) == rule_a_text(h1) and words[i] == n and (flags[i] == 1) == (n != 0))
            lanes_all += 1
            lanes_ok += good
            pass_lanes += rule_a_text(h1)
            zero_words += n == 0
        pass_batches += taken_a
        if taken_a != any(f == 0 for f in flags_a) or taken != any(f == 0 for f in flags):
            wrong.append("a branch is not taken exactly when a lane passes, case %d" % case)
    print("KEPT = %s: cases %d, lanes right %d of %d; lanes that satisfy rule A %d in %d batches; zero stage-2 words %d"
          % (kept_mode, cases, lanes_ok, lanes_all, pass_lanes, pass_batches, zero_words))
    for name in ("batch", "table build", "middle step", "outer step"):
        tot = [sum(v[t] for v in seen[name].values()) for t in range(5)]
        line = "  %s: %d + %d + %d = %d; registers %d (freed at last use: %d)" % (
            name, tot[0], tot[1], tot[2], sum(tot[:3]), regs[name], regs_min[name])
        if name == "batch":
            a = [sum(seen[name][p][t] for p in STAGE_A) for t in range(5)]
            s2 = [tot[t] - a[t] for t in range(5)]
            line += "; stage A %d + %d = %d (uses of kept words %d, list or table loads %d); stage 2 %d + %d = %d (uses %d, list or table loads %d)" % (
                a[0], a[1], a[0] + a[1], a[3], a[4], s2[0], s2[1], s2[0] + s2[1], s2[3], s2[4])
        print(line)
        if check_text:
            for p, want in TEXT[name].items():
                got = seen[name].get(p, (0, 0, 0))[:3]
                if tuple(got) != want:
                    wrong.append("part %s: traced %s, text %s" % (p, got, want))
            if set(seen[name]) - set(TEXT[name]):
                wrong.append("parts not in the text: %s" % (set(seen[name]) - set(TEXT[name])))
            if regs[name] != TEXT_REG[name]:
                wrong.append("registers of %s: traced %d, text %d" % (name, regs[name], TEXT_REG[name]))
    print("  largest lane of a sum per part, in units of 2^32: "
          + ", ".join("%s %.3f" % (p, x / 2 ** 32) for p, x in biggest.items() if x))
    if lanes_ok != lanes_all:
        wrong.append("lanes wrong: %d" % (lanes_all - lanes_ok))
    print("  findings: %s" % (wrong if wrong else "none"))
    return wrong


def main():
    cases, seed = int(sys.argv[1]), int(sys.argv[2])
    bad = run(load_program(), cases, seed, 9, True)
    bad += run(load_program(0), max(cases // 4, 20), seed + 1, 0, False)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
