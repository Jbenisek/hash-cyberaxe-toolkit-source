#!/usr/bin/env python3
"""Reviewer check, lens MATHEMATICS AND COST, parts (b) and (c). Reads the package, writes nothing into it.

    python3 -B math_batch.py N SEEDTEXT OUTFILE

Runs the package's own two-stage batch (pkg5 experiments/halfsearch.py: packed_batch on its Machine) on N fresh
cases drawn from SHAKE-256 of "math lens <SEEDTEXT> <case>" (a seed text the package never used), and checks every
lane against references that do NOT come from the package:

  * the complete digests of the lane's two real messages, from the ORGANIZER's verifier/blake3.py (rounds = 2);
  * a traced 2-round compression written here from proof.md Section 1 (its digest must equal the organizer's);
  * rule A, Lemma A (a), (b), (c) and Lemma N written here from the text of proof.md 6.3, with the constants
    typed from the text (S = 0f008000, ALL = 0f008100, V = 0a008000, mask 015fe7c1, value 00036181).

Per lane: Y4 of both messages is the lane's member and lies in the class (Lemma Q form); eta read off the two
real compressions is e7c1815f; digest words 0, 2, 5, 7 agree; h1 (second value of E3 on the 60-byte message) gives
rule A; ROL(h1,24) = z XOR ROL(e1,8) with z from the traced C2 (Lemma A a); the z-conditions (b) and the word (c)
agree with rule A; the stage-A flag of the machine is 0 exactly for rule A; n = eps XOR ROL(beta XOR eps,1) XOR eta
from the traced E1 equals D3 XOR ROL(D6,8) of the organizer digests (Lemma N) and equals the machine's stage-2 word;
the stage-2 flag is 1 exactly when that word is nonzero. Per batch: both branches are taken exactly when a lane has
a zero word in front of them.

The operations are tallied here a second time, by kind, in a subclass of the package's Machine that keeps its own
counters (every add / xor / and / or / shift / counter step one, a compare one, a branch one, every load one).
"""
import hashlib
import importlib.util
import json
import struct
import sys

sys.dont_write_bytecode = True
ROOT = 'historical-sources/~~Projects/~HashSmash/workspace'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


hs = load("pkg5_halfsearch", ROOT + "/research/pkg5/blake3-r2/experiments/halfsearch.py")
org = load("organizer_blake3", ROOT + "/hash-smash/verifier/blake3.py")

M = 0xFFFFFFFF
IV = (0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19)
PERM = (2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8)
CALLS = ((0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15), (0, 5, 10, 15), (1, 6, 11, 12), (2, 7, 8, 13), (3, 4, 9, 14))
ETA = 0xE7C1815F
QMASK, QVALUE = 0x015FE7C1, 0x00036181
S_, ALL_, V_ = 0x0F008000, 0x0F008100, 0x0A008000


def ror(v, n):
    return ((v >> n) | (v << (32 - n))) & M


def rol(v, n):
    return ror(v, 32 - n)


def trace(msg):
    """2-round compression of one message of at most 64 bytes, every assignment of every call kept."""
    n = len(msg)
    w = list(struct.unpack("<16I", msg + bytes(64 - n)))
    v = list(IV) + list(IV[:4]) + [0, 0, n, 11]
    s, calls = list(w), []
    for _ in range(2):
        for i, (a, b, c, d) in enumerate(CALLS):
            A, B, C, D, x, y = v[a], v[b], v[c], v[d], s[2 * i], s[2 * i + 1]
            a1 = (A + B + x) & M; d1 = ror(D ^ a1, 16); c1 = (C + d1) & M; b1 = ror(B ^ c1, 12)
            a2 = (a1 + b1 + y) & M; d2 = ror(d1 ^ a2, 8); c2 = (c1 + d2) & M; b2 = ror(b1 ^ c2, 7)
            v[a], v[b], v[c], v[d] = a2, b2, c2, d2
            calls.append(dict(A=A, B=B, C=C, D=D, x=x, y=y, a1=a1, d1=d1, c1=c1, b1=b1, a2=a2, d2=d2, c2=c2, b2=b2))
        s = [s[p] for p in PERM]
    return w, calls, tuple(v[i] ^ v[i + 8] for i in range(8))


def rule_a_text(h1):
    """Rule A as written in proof.md 6.3."""
    bit = lambda i: h1 >> i & 1  # noqa: E731
    return (bit(16) == 1 and bit(0) == bit(1) and bit(1) == bit(2) and bit(2) == bit(3) and bit(3) != bit(4)
            and bit(23) != bit(24))


def z_conditions(z):
    """Lemma A (b) as written."""
    bit = lambda i: z >> i & 1  # noqa: E731
    return (bit(8) == 0 and bit(24) == bit(25) and bit(25) != bit(26) and bit(26) == bit(27) and bit(27) != bit(28)
            and bit(15) != bit(16))


class Tally(hs.Machine):
    """The package's machine with a second, separate count by kind and by stage."""

    def __init__(self):
        super().__init__()
        self.kind = {}

    def note(self, what, n=1):
        stage = "2" if self.part in ("entry count", "C2, rest", "D1", "C1 to Y1", "E1, A and B", "E1 test") else "A"
        self.kind[(stage, what)] = self.kind.get((stage, what), 0) + n

    def load(self, constant):
        self.note("load")
        return super().load(constant)

    def add(self, x, y):
        self.note("add")
        return super().add(x, y)

    def xor(self, x, y):
        self.note("xor")
        return super().xor(x, y)

    def band(self, x, y):
        self.note("and")
        return super().band(x, y)

    def bor(self, x, y):
        self.note("or")
        return super().bor(x, y)

    def shr(self, x, r):
        self.note("shift")
        return super().shr(x, r)

    def shl(self, x, r):
        self.note("shift")
        return super().shl(x, r)

    def advance(self, position):
        self.note("counter")
        return super().advance(position)

    def compare_and_branch(self, x, y):
        self.note("compare")
        self.note("branch")
        return super().compare_and_branch(x, y)


def main():
    cases, seed, out = int(sys.argv[1]), sys.argv[2], sys.argv[3]
    bad = {}
    lanes = right = passing = entered = zero_words = last = 0
    shapes = set()
    worst = 0

    def fail(name):
        bad[name] = bad.get(name, 0) + 1
        return False

    for case in range(cases):
        text = "math lens %s %d" % (seed, case)
        st = struct.unpack("<12I", hashlib.shake_256(text.encode()).digest(48))
        nine, alpha, j = list(st[:9]), st[9], st[10] % hs.BATCHES
        if case % 9 == 0:
            j, last = hs.BATCHES - 1, last + 1
        if case % 11 == 5:                      # few bits set / many bits set, to push carries
            nine = [(v & 0x00000003, v | 0xFFFFFFF0, v, v)[st[11] >> 2 * i & 3] for i, v in enumerate(nine)]
        X, S, w = hs.context(nine)
        m = Tally()
        words, flags, taken, flags_a, taken_a = hs.packed_batch(m, hs.batch_constants(X, S, w, alpha)[0], j)
        members = hs.list_words(j)[1]
        ok_lane, rule, nzero = [], [], 0
        for i, y4 in enumerate(members):
            A, B = hs.messages(hs.trial(X, S, w, alpha, y4)[0])
            ok = len(A) == 60 and len(B) == 62 and A != B or fail("lengths")
            dA, dB = struct.unpack("<8I", org.blake3(A, 2)), struct.unpack("<8I", org.blake3(B, 2))
            (wa, ca, da), (wb, cb, db) = trace(A), trace(B)
            ok &= (da == dA and db == dB) or fail("my trace is not the organizer hash")
            R = [p ^ q for p, q in zip(dA, dB)]
            ok &= (R[0] == 0 and R[2] == 0 and R[5] == 0 and R[7] == 0) or fail("half collision")
            C0a, C2a, C3a, E1a, E3a = ca[8], ca[10], ca[11], ca[13], ca[15]
            C0b, C3b, E1b, E3b = cb[8], cb[11], cb[13], cb[15]
            ok &= (C0a["b2"] == y4 == C0b["b2"]) or fail("Y4 is not the member")
            ok &= (wa[4] == 0x7FFFFFFF and wa[13] == 0xFFFD6E01 and wa[15] == 0 and wb[15] == 0) or fail("pinned words")
            ok &= (C3a["a2"] == 0x3F52EDA0 and C3b["a2"] == 0xC0AC125F and C3a["c2"] == 0x5EBF5BC0 and C3b["c2"] == 0xA144803F) or fail("Fact P")
            e1 = E3a["a1"]
            ok &= (e1 == (C3a["a2"] + y4) & M and e1 & QMASK == QVALUE) or fail("Lemma Q form")
            h1, h1b = E3a["d1"], E3b["d1"]
            ok &= (h1 ^ h1b == ETA and ror(E3a["a1"] ^ E3b["a1"], 16) == ETA) or fail("eta")
            ra = rule_a_text(h1)
            z = C2a["a2"] ^ C2a["d1"]
            ok &= (rol(h1, 24) == z ^ rol(e1, 8)) or fail("Lemma A (a)")
            ok &= (z_conditions(z) == ra) or fail("Lemma A (b)")
            ok &= ((((z ^ ((z >> 1) & S_)) & ALL_) ^ V_ == 0) == ra) or fail("Lemma A (c)")
            ok &= (flags_a[i] == (0 if ra else 1)) or fail("stage-A flag")
            beta, eps = E1a["b1"] ^ E1b["b1"], E1a["c2"] ^ E1b["c2"]
            n = eps ^ rol(beta ^ eps, 1) ^ ETA
            ok &= (n == R[3] ^ rol(R[6], 8)) or fail("Lemma N")
            ok &= (words[i] == n) or fail("stage-2 word")
            ok &= (flags[i] == int(n != 0)) or fail("stage-2 flag")
            # the residual of 6.2 from the traced E1 and E3 equals the digest difference
            r62 = (E1a["a2"] ^ E3a["c2"] ^ E1b["a2"] ^ E3b["c2"], E3a["a2"] ^ E1a["c2"] ^ E3b["a2"] ^ E1b["c2"],
                   E3a["b2"] ^ E1a["d2"] ^ E3b["b2"] ^ E1b["d2"], E1a["b2"] ^ E3a["d2"] ^ E1b["b2"] ^ E3b["d2"])
            ok &= (r62 == (R[1], R[3], R[4], R[6])) or fail("residual of 6.2")
            ok_lane.append(bool(ok)); rule.append(ra); nzero += int(n == 0)
        if taken_a != any(rule):
            fail("stage-A branch"); ok_lane = [False] * 7
        if taken != (nzero > 0):
            fail("stage-2 branch"); ok_lane = [False] * 7
        lanes += 7; right += sum(ok_lane); passing += sum(rule); entered += int(any(rule)); zero_words += nzero
        shapes.add(tuple(sorted(m.kind.items())) + (("pkg", tuple((p, m.ops[p], m.loads[p]) for p in m.ops)),))
        worst = max(worst, max(m.sums.values()))
    kinds = {}
    for shape in shapes:
        for key, val in shape[:-1]:
            kinds.setdefault("%s %s" % key, set()).add(val)
    report = {
        "seed": seed, "cases": cases, "last_batches": last, "lanes": lanes, "lanes_right": right, "failures": bad,
        "lanes_rule_a": passing, "batches_entering_stage_2": entered, "zero_stage2_words": zero_words,
        "distinct_count_shapes": len(shapes),
        "by_kind": {k: sorted(v) for k, v in sorted(kinds.items())},
        "largest_lane_over_2^32": round(worst / 2 ** 32, 3),
    }
    one = next(iter(shapes))
    k = dict(one[:-1])
    for stage in ("A", "2"):
        report["stage_%s_operations_by_my_tally" % stage] = sum(v for (s, what), v in k.items() if s == stage and what != "load")
        report["stage_%s_loads_by_my_tally" % stage] = k.get((stage, "load"), 0)
    report["package_parts"] = [list(p) for p in one[-1][1]]
    with open(out, "w", encoding="ascii", newline="\n") as f:
        f.write(json.dumps(report, indent=1) + "\n")
    print("%s: lanes %d right %d failures %s rule A %d entered %d" % (seed, lanes, right, bad, passing, entered))
    return 0 if right == lanes and not bad and len(shapes) == 1 else 1


if __name__ == "__main__":
    sys.exit(main())
