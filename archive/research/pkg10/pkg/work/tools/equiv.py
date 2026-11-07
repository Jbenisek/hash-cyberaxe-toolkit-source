#!/usr/bin/env python3
"""Decisions of the batch of research/pkg7 against the batch of research/pkg7_program (the two-level program before
any recoding), on the same contexts and list positions.

    python3 -B work/tools/equiv.py N [seed [shard shards]]       writes work/evidence/equiv_<seed>_<shard>of<shards>.txt

What is compared, per batch of seven trials: the five table words; the seven stage-A flags and the stage-A branch;
the seven reduced stage-2 words, their seven flags and the final branch. The program before runs its own outer
step, table build, middle step and batch (every word fetched where it is read, no word kept in a register, no value
formed again, the stage-2 test with the masked rotation), on the same sub-class: its four lines CLASS_MASK,
CLASS_VALUE, CLASS_FREE, CLASS_SIZE and BATCHES are set, in memory, to the values of the program of pkg7, so that
list word j holds the same seven members. Its rule (five conditions, on a class that fixes every bit of e1 it
reads) is not the rule of pkg7. In its place the stage-A word of the program before is made here, lane by lane,
from ITS z: 0 where h1 = ROR(ROR(z, 8) XOR e1, 16), e1 = Y3 + Y4 of the lane's member, satisfies the conditions
RULE below (typed here from research/pkg7/count/COUNT.md section 2, and compared with the program's), 1 elsewhere;
its own lane_flags() then gives its flags and its branch. So the stage-A decision of the program before is "the
rule as written on h1, on the z of the batch before", and everything else is its own machine code.

Every fourth batch is the last word of the list, in every fifth each context word is 0, 2^32 - 1 or as drawn (the
cases of the program's self-test, other seed text). Research helper, not submitted.
"""
import hashlib
import struct
import sys

from common import PROGRAM, RESEARCH, load, program, sha, write

RULE = {4: ((0x00000001, 0), (0x00000002, 1), (0x00010000, 0), (0x00020000, 0))}
RULE[6] = RULE[4] + ((0x00000404, 1), (0x00000808, 1))
RULE[8] = RULE[6] + ((0x01001008, 0), (0x02002040, 0))
BEFORE = RESEARCH / "pkg7_program" / "halfsearch.py"


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
    seed = sys.argv[2] if len(sys.argv) > 2 else "1"
    shard, shards = (int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else (0, 1)
    new, old = program(), load(BEFORE, "halfsearch_before")
    rule = RULE[len(new.RULE_A)]
    assert tuple(new.RULE_A) == rule
    for name in ("CLASS_MASK", "CLASS_VALUE", "CLASS_FREE", "CLASS_SIZE", "BATCHES"):
        setattr(old, name, getattr(new, name))
    now = {}

    def satisfied(h1):
        return all(bin(h1 & mask).count("1") & 1 == value for mask, value in rule)

    def word_before(m, c, z):
        lanes = [v & old.MASK for v in old.lanes(z.z)]
        now["z"] = lanes
        return m.load(old.pack(0 if satisfied(old.ror(old.ror(v, 8) ^ (old.Y3 + y4) & old.MASK, 16)) else 1
                               for v, y4 in zip(lanes, now["members"])))

    old.rule_a_word = word_before
    total = dict(batches=0, same=0, tables=0, stage_a=0, stage_2=0, passing=0, entering=0, zero=0, last=0, extreme=0,
                 members=0)
    first = None
    for case in range(shard, n, shards):
        text = "equiv %s %d" % (seed, case)
        stream = struct.unpack("<9I", hashlib.shake_256(text.encode("utf-8")).digest(36))
        seven, j = list(stream[:7]), stream[7] % new.BATCHES
        if case % 4 == 0:
            j, total["last"] = new.BATCHES - 1, total["last"] + 1
        if case % 5 == 4:
            seven = [(0, new.MASK, v, v)[stream[8] >> 2 * i & 3] for i, v in enumerate(seven)]
            total["extreme"] += 1
        got = []
        for hs in (new, old):
            c = hs.memory(seven)
            hs.outer_step(hs.Machine(), c)
            row = hs.table_build(hs.Machine(), c, j)
            hs.middle_step(hs.Machine(), c)
            now["members"] = hs.list_words(j)[1]
            words, flags, taken, flags_a, taken_a = hs.packed_batch(hs.Machine(), c, row, j)
            got.append((dict(row), (list(flags_a), bool(taken_a)), (list(words), list(flags), bool(taken)),
                        list(now["members"])))
        a, b = got
        total["batches"] += 1
        total["members"] += int(a[3] == b[3])
        total["tables"] += int(a[0] == b[0])
        total["stage_a"] += int(a[1] == b[1])
        total["stage_2"] += int(a[2] == b[2])
        same = a == b
        total["same"] += int(same)
        total["passing"] += 7 - sum(a[1][0])
        total["entering"] += int(a[1][1])
        total["zero"] += sum(int(w == 0) for w in a[2][0])
        if not same and first is None:
            first = (case, seven, j)
    out = [f"PROGRAM sha256 {sha()}; before: research/pkg7_program/halfsearch.py sha256 "
           f"{hashlib.sha256(BEFORE.read_bytes()).hexdigest()}; python3 -B work/tools/equiv.py {n} {seed} {shard} {shards}",
           f"rule of {len(rule)} conditions on h1 (typed in the tool, equal to the program's): "
           f"{['%08x:%d' % r for r in rule]}; sub-class mask {new.CLASS_MASK:08x} value {new.CLASS_VALUE:08x}, "
           f"{new.CLASS_SIZE} members, {new.BATCHES} list words",
           f"batches compared {total['batches']} (cases {shard}, {shard + shards}, ... below {n}; {total['last']} the last "
           f"list word, {total['extreme']} with extreme words)",
           f"same seven members {total['members']}, same five table words {total['tables']}, same stage-A flags and branch "
           f"{total['stage_a']}, same stage-2 words, flags and branch {total['stage_2']}, all the same {total['same']}",
           f"different {total['batches'] - total['same']}" + ("" if first is None else f"; first: case {first[0]}, context "
                                                                                 f"{['%08x' % v for v in first[1]]}, j {first[2]}"),
           f"lanes that satisfy the rule {total['passing']} of {7 * total['batches']}, batches entering stage 2 "
           f"{total['entering']}, zero stage-2 words {total['zero']}",
           "RESULT: " + ("decisions identical in every batch" if total["same"] == total["batches"] else "DIFFERENCES")]
    write(f"equiv_{seed}_{shard}of{shards}.txt", out)
    print("\n".join(line[:230] for line in out[2:]))
    return 0 if total["same"] == total["batches"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
