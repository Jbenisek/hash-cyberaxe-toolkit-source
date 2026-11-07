#!/usr/bin/env python3
"""The program against the references of the two-level arrangement. Research helper, not submitted.

    python -B work/tools/ref_compare.py [contexts, default 2000] [members per context, default 25] [batches, default 400]

Nothing of research/h8 is written; its files are only read. Comparisons (exit status 0 only if all hold), written
to work/evidence/ref_compare.txt:

  1. Constants and class: the pin, W4', delta, Y3, Y3', Y11, Y11', the class mask and value, every tenth member and
     the first and last 4,096, against research/h8/twolevel/h8_ref.py (the unchanged copy of the design reference).
  2. Outer step, middle step, member and trial against research/h8/twolevel/tl_ref.py, the generic solver that
     replays the 96 lines of two_level_H8.txt, one G-call assignment per line: every value that the program's
     outer(), middle() and member() return, by name, against the solver's value of that name (lines tagged "-",
     "Z" and "Y"), the sixteen words of the trial, the two messages, and the trial's X0, X5, X10 (lines tagged "T").
     It also checks that the names the program computes are exactly the 29 + 21 names tagged "-" and "Z", and that
     member() returns names tagged "Y" only.
  3. The batch against research/h8/twolevel/tl_batch.py (the batch whose counts are in TL_cost.txt), for the rules
     with 4, 5 and 6 conditions: on the same context and list word, the five table words, the seven stage-2 words,
     their flags and the final branch. tl_batch.py is run on the seven members of the program's list word (it has
     the whole class and the rules of the filed package; its rule with four conditions is the program's rule with
     four conditions), so for the program's rule with four conditions the seven stage-A flags and the stage-A
     branch are compared as well; for six and eight conditions they are not compared here (work/tools/equiv.py and
     the self-test do that). The counts of the two are printed side by side.
  4. The test of the first 2,000 trials with the organizer's reference verifier/blake3.py, if the repository is
     there: both digests of the program's compress2 equal blake3(message, 2).
"""
import random
import sys

from common import HEAD, RESEARCH, RULES, load, program, program_with_rule, sha, write

TL = RESEARCH / "h8" / "twolevel"


def main():
    contexts = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
    per = int(sys.argv[2]) if len(sys.argv) > 2 else 25
    batches = int(sys.argv[3]) if len(sys.argv) > 3 else 400
    new = program()
    sys.path.insert(0, str(TL))
    T = load(TL / "tl_ref.py", "tl_ref")
    ref = T.H
    out = [f"{HEAD}PROGRAM sha256 {sha()}; python -B work/tools/ref_compare.py {contexts} {per} {batches}"]
    ok = True

    same = ((new.X3, new.X7, new.X11, new.X15, new.W4, new.W13, new.W4B, new.DELTA5, new.ETA, new.LEN_A, new.LEN_B)
            == (ref.X3, ref.X7, ref.X11, ref.X15, ref.W4, ref.W13, ref.W4B, ref.DELTA, ref.ETA, ref.LEN_A, ref.LEN_B)
            and (new.Y3, new.Y3B, new.Y11, new.Y11B) == (ref.Y3A, ref.Y3B, ref.Y11A, ref.Y11B)
            and (new.CLASS_MASK, new.CLASS_VALUE) == (ref.CLASS_MASK | new.CUBE[0], ref.CLASS_VALUE | new.CUBE[1])
            and not ref.CLASS_MASK & new.CUBE[0] and new.CLASS_SIZE << bin(new.CUBE[0]).count("1") == ref.CLASS_SIZE
            and sorted(new.CONTEXT_WORDS) == sorted(T.OUTER_WORDS + [T.MIDDLE_WORD]) and new.CONTEXT_WORDS[6] == T.MIDDLE_WORD)
    # the sub-class: exactly the members of the reference class whose e1 = Y3 + Y4 has the bits of CUBE
    inside = [y for y in (ref.class_member(k) for k in range(ref.CLASS_SIZE))
              if (ref.Y3A + y) & new.MASK & new.CUBE[0] == new.CUBE[1]]
    mine = [new.class_member(k) for k in range(new.CLASS_SIZE)]
    members = sum(ref.in_class(y) for y in mine)
    out.append(f"1. constants and the seven context words: {'equal' if same else 'DIFFERENT'}; sub-class mask {new.CLASS_MASK:08x} "
               f"value {new.CLASS_VALUE:08x} = class of h8_ref.py (mask {ref.CLASS_MASK:08x}, {ref.CLASS_SIZE} members) with the "
               f"bits {new.CUBE[0]:08x} of e1 set to {new.CUBE[1]:08x}; members of the program in the class of h8_ref.py: "
               f"{members} of {len(mine)}; the program's members are exactly the {len(inside)} members of that class with "
               f"these bits, in the same order: {mine == inside}")
    ok &= same and members == len(mine) and mine == inside

    tags = {t: [v for v, _ in T.LINES[t]] for t in "-ZYT"}
    rng = random.Random(61006)
    six0 = [rng.getrandbits(32) for _ in range(6)]
    o0 = new.outer(six0)
    v0 = new.middle(o0, 5)
    mine_outer = set(o0) - set(new.CONTEXT_WORDS)
    mine_middle = set(v0) - set(o0) - {"X2"}
    fixed_k2 = {"K2.a1", "K2.d1", "K2.c1", "K2.b1"}
    names = (mine_outer | fixed_k2 == set(tags["-"]) and mine_middle == set(tags["Z"])
             and set(new.member(o0, new.class_member(1))) <= set(tags["Y"]))
    out.append(f"2. names: outer() returns {len(mine_outer)} names and the four constants of K2 are module constants, the solver "
               f"has {len(tags['-'])} lines tagged '-'; middle() adds {len(mine_middle)} names, the solver has {len(tags['Z'])} "
               f"lines tagged 'Z'; member() returns only names tagged 'Y': {names}")
    ok &= names
    total = good = values = 0
    for n in range(contexts):
        seven = [rng.getrandbits(32) for _ in range(7)]
        if n % 5 == 4:
            seven = [rng.choice((0, new.MASK, v)) for v in seven]
        v = new.context(seven)
        octx = T.outer(dict(zip(new.CONTEXT_WORDS[:6], seven[:6])))
        zctx = T.middle(octx, seven[6])
        k2 = (new.K2A, new.K2D, new.K2C, new.K2B) == tuple(octx[x] for x in ("K2.a1", "K2.d1", "K2.c1", "K2.b1"))
        ctx_ok = k2 and all(v[name] == zctx[name] for name in v)
        values += len(v)
        for _ in range(per):
            y4 = new.class_member(rng.randrange(new.CLASS_SIZE))
            row = T.member(octx, y4)
            words, t = new.trial(v, y4)
            rwords, st = T.trial(octx, zctx, row)
            mem = new.member(v, y4)
            state = all(mem[name] == st[name] for name in mem) and all(t[name] == st[name] for name in ("X0", "X5", "X10"))
            trow = new.table_row(v, y4)
            tab = (trow == {"XA": (st["C0.a1"] - st["X4"]) & new.MASK, "X6": st["X6"], "X1": st["X1"],
                            "R": new.rol(st["D1.d1"], 16), "Y12": st["Y12"]})
            total += 1
            good += ctx_ok and words == rwords and new.messages(words) == ref.messages(rwords) and state and tab
    out.append(f"2. outer, middle, member and trial against tl_ref.py: every value by name ({values // contexts} per context), the "
               f"sixteen words, the two messages, the member's values and the table row equal in {good} of {total} trials "
               f"({contexts} contexts, every fifth with extreme words)")
    ok &= good == total

    tb = load(TL / "tl_batch.py", "tl_batch")
    for rule in RULES:
        hs = program_with_rule(rule)
        good, shapes = 0, set()
        for n in range(batches):
            seven = [rng.getrandbits(32) for _ in range(7)]
            j = hs.BATCHES - 1 if n % 8 == 0 else rng.randrange(hs.BATCHES)
            c = hs.memory(seven)
            hs.outer_step(hs.Machine(), c)
            mb = hs.Machine()
            row = hs.table_build(mb, c, j)
            hs.middle_step(hs.Machine(), c)
            m = hs.Machine()
            mine = hs.packed_batch(m, c, row, j)
            octx = T.outer(dict(zip(hs.CONTEXT_WORDS[:6], seven[:6])))
            zctx = T.middle(octx, seven[6])
            ms = hs.list_words(j)[1]
            co = tb.outer_constants(octx)
            tmb = tb.Machine()
            u, vr = tb.static_words(ms, 4)
            L = tb.build_batch(tmb, co, u)
            tm = tb.Machine()
            theirs = tb.per_trial(tm, tb.middle_constants(co, octx, zctx), L, vr, 4)
            if rule != 4:                       # stage A of tl_batch.py is its rule with four conditions
                mine, theirs = mine[:3], theirs[:3]
            split = list(tm.ops).index("entry count")
            a = (sum(list(tm.ops.values())[:split]), sum(list(tm.loads.values())[:split]))
            s2 = (sum(list(tm.ops.values())[split:]), sum(list(tm.loads.values())[split:]))
            parts = list(m.ops)
            ma = (sum(m.ops[p] for p in parts[:hs.STAGE_A_PARTS]), sum(m.loads[p] for p in parts[:hs.STAGE_A_PARTS]))
            m2 = (sum(m.ops[p] for p in parts[hs.STAGE_A_PARTS:]), sum(m.loads[p] for p in parts[hs.STAGE_A_PARTS:]))
            shapes.add((ma, m2, m.registers(), (sum(mb.ops.values()), sum(mb.loads.values()), sum(mb.stores.values())),
                        a, s2, tm.registers(), (sum(tmb.ops.values()), sum(tmb.loads.values()), sum(tmb.stores.values()))))
            good += (mine == theirs and all(ref.in_class(y) for y in ms) and u == hs.list_words(j)[0]
                     and row == {name: L[name] for name in row} and set(row) == set(L))
        one = sorted(shapes)[0]
        out.append(f"3. rule with {rule} conditions against tl_batch.py: table words, stage-2 words, their flags, the final branch"
                   f"{', the stage-A flags and the stage-A branch' if rule == 4 else ''} "
                   f"equal in {good} of {batches} batches; counts here: stage A {one[0][0]}+{one[0][1]}, "
                   f"stage 2 {one[1][0]}+{one[1][1]}, registers {one[2]}, build {one[3][0]}+{one[3][1]}+{one[3][2]}; tl_batch.py: stage A "
                   f"(its rule 4) {one[4][0]}+{one[4][1]}, stage 2 {one[5][0]}+{one[5][1]}, registers {one[6]}, build {one[7][0]}+{one[7][1]}+{one[7][2]}; "
                   f"one shape in all batches: {len(shapes) == 1}; counts equal to tl_batch.py: {one[:4] == one[4:]} (they "
                   f"are meant to differ: this program is the recoded batch with another rule)")
        ok &= good == batches and len(shapes) == 1

    blake = None
    root = RESEARCH.parent / "hash-smash"
    if (root / "verifier" / "blake3.py").exists():
        sys.path.insert(0, str(root))
        try:
            from verifier.blake3 import blake3 as blake
        except Exception:
            blake = None
    if blake is None:
        out.append("4. organizer reference verifier/blake3.py: not available, not compared")
    else:
        import struct
        good = 0
        for n in range(2000):
            seven = [rng.getrandbits(32) for _ in range(7)]
            A, B = new.messages(new.trial(new.context(seven), new.class_member(rng.randrange(new.CLASS_SIZE)))[0])
            good += (struct.pack("<8I", *new.compress2(A)[1]) == blake(A, 2) and struct.pack("<8I", *new.compress2(B)[1]) == blake(B, 2)
                     and (len(A), len(B)) == (55, 63))
        out.append(f"4. compress2 of the program against the organizer's verifier/blake3.py with 2 rounds: both digests equal in "
                   f"{good} of 2000 trials")
        ok &= good == 2000
    out.append("RESULT: " + ("all equal" if ok else "DIFFERENCES"))
    write("ref_compare.txt", out)
    for line in out[1:]:
        print(line[:300])
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
