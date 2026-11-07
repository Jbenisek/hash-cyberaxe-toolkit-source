#!/usr/bin/env python3
"""Numerical check of the experiment program with a forward compression written here. Research helper, not submitted.

    python -B work/tools/check_program.py [trials, default 20000] [experiment trials, default 256]

The counterpart, for the two-level program, of parts (a) and (b) of check_pkg6.py of the package before this one.
The forward 2-round BLAKE3 compression below is written here (columns, diagonals, permutation) and keeps the
states S, X, Y; it is compared with the organizer's verifier/blake3.py when that file is there.

(a) Random trials of the program's own functions context() and trial(): the two messages are compressed forwards
    and everything the trial claims is read off the forward computation: lengths, zero tail, pinned words, every
    S and X of the context, the trial's X, Y4 equal to the member in A and in B, Y of A and B different only in
    Y3 and Y11, digest words 0, 2, 5, 7 equal, the word of Lemma N from E1 alone equal to D3 XOR ROL(D6, 8) of the
    digests, rule A on h1 equal to the program's test on z (steps, word of the list V, mask: Lemma A as the
    program has it), Y4 inside the sub-class, and the round trip: the seven words of the context read off the forward computation (second
    and third value of C0, second value of D3, S15, S9, w5, X2) are the seven words the trial was made from. It
    also checks the loop structure: a context that differs only in X2 has the same values of outer(), and two
    members of one context differ in no message word outside w8..w11.
(b) The program through its stdin/stdout contract for both experiments: output byte-identical on a second run, one
    row per trial, and for every returned pair what (a) checks plus the organizer's mask event and, for
    "residual-search", the low byte of digest word 1 and the six observations (the counts of the program's TABLES
    and seven right lanes).

Exit status 0 only if every check holds. The result is written to work/evidence/check_program.txt.
"""
import hashlib
import json
import random
import struct
import subprocess
import sys

from common import PROGRAM, RESEARCH, WORK, program, sha, write

hs = program()
M32 = 0xFFFFFFFF
IV = (0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19)
PERM = (2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8)
MANIFEST = WORK.parent / "blake3-r2" / "experiments" / "manifest.json"
FAILS = []


def ror(v, n):
    return ((v >> n) | (v << (32 - n))) & M32


def rol(v, n):
    return ror(v, 32 - n)


def g_steps(A, B, C, D, x, y):
    """The eight assignments of one G call, in the order a1, d1, c1, b1, a2, d2, c2, b2."""
    a1 = (A + B + x) & M32; d1 = ror(D ^ a1, 16); c1 = (C + d1) & M32; b1 = ror(B ^ c1, 12)
    a2 = (a1 + b1 + y) & M32; d2 = ror(d1 ^ a2, 8); c2 = (c1 + d2) & M32; b2 = ror(b1 ^ c2, 7)
    return a1, d1, c1, b1, a2, d2, c2, b2


def G(A, B, C, D, x, y):
    s = g_steps(A, B, C, D, x, y)
    return s[4], s[7], s[6], s[5]


def hash2(message):
    """Forward 2-round compression of a message of at most 64 bytes: digest words and the states S, X, Y."""
    n = len(message)
    s = list(struct.unpack("<16I", message + bytes(64 - n)))
    v = list(IV) + list(IV[:4]) + [0, 0, n, 11]
    snap = []
    for _ in range(2):
        for j in range(4):
            idx = (j, 4 + j, 8 + j, 12 + j)
            for i, o in zip(idx, G(*(v[i] for i in idx), s[2 * j], s[2 * j + 1])):
                v[i] = o
        snap.append(list(v))
        for j, idx in enumerate(((0, 5, 10, 15), (1, 6, 11, 12), (2, 7, 8, 13), (3, 4, 9, 14))):
            for i, o in zip(idx, G(*(v[i] for i in idx), s[8 + 2 * j], s[9 + 2 * j])):
                v[i] = o
        snap.append(list(v))
        s = [s[p] for p in PERM]
    S, X, Y, Z = snap
    return [Z[i] ^ Z[i + 8] for i in range(8)], S, X, Y


def rule_on_h1(h1, rule):
    return all(bin(h1 & mask).count("1") & 1 == value for mask, value in rule)


def rule_on_z(z, y4):
    """The program's test on z (Lemma A as the program has it), on one 32-bit word, for the member y4: the steps
    A_STEPS, then the XOR with the member's word of the list V, the mask ALL and the comparison with ALL."""
    y, s = z, None
    for step in hs.A_STEPS:
        if isinstance(step, tuple):
            s = ((y << step[0]) if step[0] > 0 else (y >> -step[0])) & step[1]
        else:
            s = (s << step) if step > 0 else (s >> -step)
        y ^= s
    return ((y ^ hs.rule_word(y4)) & hs.A_ALL) == hs.A_ALL


class Tally:
    def __init__(self):
        self.count, self.order = {}, []

    def check(self, name, ok):
        if name not in self.count:
            self.count[name] = [0, 0]
            self.order.append(name)
        self.count[name][0] += 1
        if ok:
            self.count[name][1] += 1
        elif len(FAILS) < 10:
            FAILS.append(name)
        return ok

    def report(self, out):
        for name in self.order:
            n, good = self.count[name]
            out.append(f"  [{'ok' if n == good else 'FAIL'}] {good} of {n}  {name}")
        return all(n == good for n, good in self.count.values())


def organizer():
    root = RESEARCH.parent / "hash-smash"
    if not (root / "verifier" / "blake3.py").exists():
        return None
    sys.path.insert(0, str(root))
    try:
        from verifier.blake3 import blake3 as ref
    except Exception:
        return None
    return ref


def pair_checks(t, name, A, B, members, ref, seven=None, y4=None):
    """Everything that is read off the forward computation of one pair. Returns (digests, states) of A and B."""
    wa = struct.unpack("<16I", A + bytes(64 - len(A)))
    wb = struct.unpack("<16I", B + bytes(64 - len(B)))
    da, S, X, Y = hash2(A)
    db, Sb, Xb, Yb = hash2(B)
    t.check(f"{name}: lengths 55 and 63, B ends in eight zero bytes, A and B differ only in w4, w5 (w5' = w5 + delta)",
            (len(A), len(B)) == (55, 63) and B[55:] == bytes(8) and [i for i in range(16) if wa[i] != wb[i]] == [4, 5]
            and wb[5] == (wa[5] + hs.DELTA5) & M32)
    t.check(f"{name}: pinned words and state (w4, w4', w13, w14, w15, X3, X7, X11, X15), top byte of w13 zero",
            (wa[4], wb[4], wa[13], wa[14], wa[15]) == (hs.W4, hs.W4B, hs.W13, 0, 0) and wa[13] >> 24 == 0
            and (X[3], X[7], X[11], X[15]) == (hs.X3, hs.X7, hs.X11, hs.X15))
    t.check(f"{name}: length cancellation: A and B have the same state S and the same state X after round 0", S == Sb and X == Xb)
    t.check(f"{name}: Y of A and B differ only in Y3, Y11, with the values of the pin; Y4 is a member of the class",
            all(Y[i] == Yb[i] for i in range(16) if i not in (3, 11)) and (Y[3], Yb[3], Y[11], Yb[11]) == (hs.Y3, hs.Y3B, hs.Y11, hs.Y11B)
            and Y[4] in members)
    t.check(f"{name}: digest words 0, 2, 5, 7 of A and B are equal", all(da[i] == db[i] for i in (0, 2, 5, 7)))
    # Lemma N from E1 alone; Lemma A from C2 forwards
    a1 = (Y[1] + Y[6] + wa[12]) & M32
    d1 = ror(Y[12] ^ a1, 16)
    b1, b1b = ror(Y[6] ^ ((hs.Y11 + d1) & M32), 12), ror(Y[6] ^ ((hs.Y11B + d1) & M32), 12)
    eps = G(Y[1], Y[6], hs.Y11, Y[12], wa[12], wa[5])[2] ^ G(Y[1], Y[6], hs.Y11B, Y[12], wb[12], wb[5])[2]
    word_n = eps ^ rol(b1 ^ b1b ^ eps, 1) ^ hs.ETA
    t.check(f"{name}: Lemma N: n from E1 alone equals D3 XOR ROL(D6, 8) of the two complete digests",
            word_n == (da[3] ^ db[3]) ^ rol(da[6] ^ db[6], 8))
    c2 = g_steps(X[2], X[6], X[10], X[14], wa[7], wa[0])
    z = c2[4] ^ c2[1]
    e1 = (Y[3] + Y[4]) & M32
    h1 = ror(Y[14] ^ e1, 16)
    t.check(f"{name}: Lemma A: Y14 = ROR(z, 8), ROL(h1, 24) = z XOR ROL(e1, 8), and the rule on h1 "
            f"and the test of the program on z (steps, word of the list V, mask) say the same (rule of the program: {len(hs.RULE_A)} conditions)",
            Y[14] == ror(z, 8) and rol(h1, 24) == z ^ rol(e1, 8) and rule_on_h1(h1, hs.RULE_A) == rule_on_z(z, Y[4]) == hs.rule_a(h1))
    # round trip: the seven words of the context, read off the forward computation
    c0 = g_steps(X[0], X[4], X[8], X[12], wa[2], wa[6])
    d3 = g_steps(S[3], S[4], S[9], S[14], wa[14], wa[15])
    own = [c0[2], c0[1], d3[1], S[15], S[9], wa[5], X[2]]
    v = hs.context(own)
    t.check(f"{name}: round trip: context() and trial() on the pair's own seven words and Y4, read off its forward "
            "computation, return the pair's words", hs.trial(v, Y[4])[0] == list(wa) and (seven is None or own == list(seven))
            and (y4 is None or Y[4] == y4))
    t.check(f"{name}: every S and X of the context and the six X of the trial are those of the forward computation",
            all(v[f"S{i}"] == S[i] for i in range(16)) and all(v[f"X{i}"] == X[i] for i in (2, 4, 8, 9, 13, 14))
            and all(hs.trial(v, Y[4])[1][f"X{i}"] == X[i] for i in (0, 1, 5, 6, 10, 12)))
    if ref is not None:
        t.check(f"{name}: both digests equal the organizer reference blake3(m, 2)",
                ref(A, 2) == struct.pack("<8I", *da) and ref(B, 2) == struct.pack("<8I", *db))
    return da, db, wa, Y


def part_a(trials, rng, ref, out):
    out.append(f"(a) context() and trial() of the program against a forward 2-round compression, {trials} random trials")
    t = Tally()
    members = {hs.class_member(k) for k in range(hs.CLASS_SIZE)}
    t.check(f"the {hs.CLASS_SIZE} members of the class are distinct", len(members) == hs.CLASS_SIZE)
    passes = 0
    for n in range(trials):
        seven = [rng.getrandbits(32) for _ in range(7)]
        if n % 16 == 0:
            seven = [rng.choice((0, M32, x)) for x in seven]
        y4 = hs.class_member(rng.randrange(hs.CLASS_SIZE))
        v = hs.context(seven)
        words = hs.trial(v, y4)[0]
        A, B = hs.messages(words)
        da, db, wa, Y = pair_checks(t, "trial", A, B, members, ref if n < 2000 else None, seven, y4)
        passes += hs.rule_a(ror(Y[14] ^ ((Y[3] + Y[4]) & M32), 16))
        if n < 4000:
            other = list(seven)
            other[6] = rng.getrandbits(32)
            o1, o2 = hs.outer(seven[:6]), hs.context(other)
            t.check("loop structure: a context that differs only in X2 has the same values of outer() (4000 trials)",
                    all(o2[name] == value for name, value in o1.items()))
            words_o = hs.trial(v, hs.class_member(rng.randrange(hs.CLASS_SIZE)))[0]
            t.check("loop structure: two members of one context differ in no message word outside w8..w11 (4000 trials)",
                    all(words_o[i] == words[i] for i in range(16) if not 8 <= i <= 11))
            t.check("loop structure: the row of the table (member(), table_row()) is the same for another X2 (4000 trials)",
                    hs.table_row(v, y4) == hs.table_row(o2, y4) and hs.member(v, y4) == hs.member(o2, y4))
    ok = t.report(out)
    out.append(f"    trials that satisfy rule A: {passes} of {trials} (a share of 2^-{len(hs.RULE_A)} is {trials / 2 ** len(hs.RULE_A):.1f}); "
               f"organizer reference: {'used for the first 2000 trials' if ref is not None else 'not available'}")
    return ok


def part_b(count, ref, out):
    out.append(f"(b) the program through its stdin/stdout contract, {count} seeds per experiment (manifest: work copy, unchanged)")
    manifest = json.loads(MANIFEST.read_text())
    t = Tally()
    members = {hs.class_member(k) for k in range(hs.CLASS_SIZE)}
    table = hs.TABLES["batch"]
    expect = (sum(r[1] for r in table[:hs.STAGE_A_PARTS]), sum(r[2] for r in table[:hs.STAGE_A_PARTS]),
              sum(r[1] for r in table[hs.STAGE_A_PARTS:]), sum(r[2] for r in table[hs.STAGE_A_PARTS:]), 7)
    for entry in manifest["experiments"]:
        name, event = entry["id"], entry["event"]
        request = {"schema_version": 1, "experiment_id": name, "target_profile": "blake3-r2-prefix-v1",
                   "event": event, "max_message_bytes": 4096,
                   "trials": [{"trial": i, "seed": hashlib.sha256(b"pkg7-host-%s-%d" % (name.encode(), i)).hexdigest()}
                              for i in range(count)]}
        payload = json.dumps(request, sort_keys=True, separators=(",", ":")).encode() + b"\n"
        outs = [subprocess.run([sys.executable, "-B", "-s", str(PROGRAM)], input=payload, capture_output=True, check=True).stdout
                for _ in range(2)]
        t.check(f"{name}: output byte-identical on a second run", outs[0] == outs[1])
        result = json.loads(outs[0])
        mask, expected = int(event["mask_hex"], 16), int(event["expected_hex"], 16)
        tries, missing, full, seen, entered = [], 0, 0, set(), 0
        t.check(f"{name}: one row per requested trial, in order", [r["trial"] for r in result["trials"]] == list(range(count)))
        for row in result["trials"]:
            if row["message_a_hex"] is None:
                missing += 1
                continue
            A, B = bytes.fromhex(row["message_a_hex"]), bytes.fromhex(row["message_b_hex"])
            da, db, wa, Y = pair_checks(t, name, A, B, members, ref)
            digest_a, digest_b = struct.pack("<8I", *da), struct.pack("<8I", *db)
            t.check(f"{name}: the organizer's mask event holds",
                    (int.from_bytes(digest_a, "big") ^ int.from_bytes(digest_b, "big")) & mask == expected)
            if name == "residual-search":
                t.check(f"{name}: low byte of digest word 1 agrees", (da[1] ^ db[1]) & 0xFF == 0)
                obs = row["observations"]
                tries.append(obs["tries"])
                t.check(f"{name}: the counted batch reports stage A {expect[0]} + {expect[1]}, stage 2 {expect[2]} + {expect[3]} "
                        "(TABLES of the program) and 7 right lanes",
                        (obs["batch_stage_a_operations"], obs["batch_stage_a_loads"], obs["batch_stage_2_operations"],
                         obs["batch_stage_2_loads"], obs["batch_lanes_right"]) == expect)
                entered += obs["batch_stage_2_entered"]
            full += da == db
            seen.add(A)
        t.check(f"{name}: every seed returned a pair", missing == 0)
        t.check(f"{name}: all returned messages A are different", len(seen) == count - missing)
        line = f"    {name}: pairs {count - missing} of {count}, full collisions {full}, {len(outs[0])} bytes of output"
        if tries:
            line += (f", members tried: mean {sum(tries) / len(tries):.1f}, max {max(tries)}; counted batches in which a lane "
                     f"satisfies rule A: {entered} of {len(tries)}")
        out.append(line)
    return t.report(out)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    trials = int(args[0]) if len(args) > 0 else 20000
    count = int(args[1]) if len(args) > 1 else 256
    rng = random.Random(20261006)
    ref = organizer()
    out = [f"TIER {__import__('common').TIER}; PROGRAM sha256 {sha()}; python -B work/tools/check_program.py {trials} {count}"]
    ok_a = part_a(trials, rng, ref, out)
    ok_b = part_b(count, ref, out)
    out.append("RESULT (a), (b): " + ("all checks of the program passed" if ok_a and ok_b else "FAILED: " + "; ".join(FAILS)))
    write("check_program.txt", out)
    marks = sum("[ok]" in line for line in out)
    for line in out:
        if "[ok]" not in line:
            print(line[:260])
    print(f"lines marked ok: {marks}; detail in work/evidence/check_program.txt")
    return 0 if ok_a and ok_b else 1


if __name__ == "__main__":
    sys.exit(main())
