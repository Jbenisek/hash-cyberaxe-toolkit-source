#!/usr/bin/env python3
"""The recoded batch with NO word kept in a register: every memory word that an operation reads is one load.

    python -B work/tools/every_use.py [cases per rule, default 1500]     writes work/evidence/every_use.txt

This is the count that is comparable, line for line, with the program of research/pkg7_program (stage A 29+18,
30+19, 33+20 and stage 2 102+45), whose machine fetches every operand where it is read. It is obtained from
strict/halfsearch.py with the one line KEPT = 0, set in memory (no file is touched): then no word is resident, get()
keeps nothing, stage A keeps the third value of C2 and stage 2 has no part "restore". What is left is the coding
alone: the test of rule A by a carry, w12 folded into the word -S1-S6, and the left shift of the E1 test without
its mask. TABLES of the file is for KEPT = 9 and is not compared here; the counts are read off the machines. Every
lane is checked by the program's own batch_check against the complete digests of its two real messages.
Research helper, not submitted.
"""
import random
import sys

from common import HEAD, RULES, TIER, program_with, sha, write


def main():
    cases = int(sys.argv[1]) if len(sys.argv) > 1 else 1500
    assert TIER == "strict"
    out = [f"{HEAD}PROGRAM sha256 {sha()} with the line KEPT = 0 set in memory; python -B work/tools/every_use.py {cases}"]
    good, short = True, []
    for n in RULES:
        hs = program_with(n, KEPT=0)
        assert hs.RESIDENT == () and hs.EVICT == () and not hs.RC_AGAIN and not hs.Z_AGAIN and hs.REGISTERS == 16
        rng = random.Random(20261006 + n)
        shape, same, right, stored, registers = None, True, 0, 0, {name: 0 for name in hs.TABLES}
        for case in range(cases):
            seven = [rng.getrandbits(32) for _ in range(7)]
            if case % 5 == 4:
                seven = [rng.choice((0, hs.MASK, v, v)) for v in seven]
            j = hs.BATCHES - 1 if case % 4 == 0 else rng.randrange(hs.BATCHES)
            checked, machines = hs.batch_check(seven, j)
            right += checked["lanes_right"]
            stored += checked["stored_right"]
            found = {name: tuple((p, m.ops[p], m.loads[p], m.stores[p], m.uses[p]) for p in m.ops) for name, m in machines.items()}
            shape = shape or found
            same = same and found == shape
            for name, m in machines.items():
                registers[name] = max(registers[name], m.registers())
        b = shape["batch"]
        a, s2 = b[:hs.STAGE_A_PARTS], b[hs.STAGE_A_PARTS:]
        sa, st = (sum(r[1] for r in a), sum(r[2] for r in a)), (sum(r[1] for r in s2), sum(r[2] for r in s2))
        uses = sum(r[4] for rows in shape.values() for r in rows)
        ok = same and right == 7 * cases and stored == cases and max(registers.values()) <= 16 and uses == 0
        good &= ok
        out.append("")
        out.append(f"RULE WITH {n} CONDITIONS, no word kept: {cases} cases, {right} of {7 * cases} lanes right, stored words right "
                   f"in {stored} of {cases}, same counts in every case {same}, reads of a kept word {uses}")
        for name, rows in shape.items():
            tot = tuple(sum(r[i] for r in rows) for i in (1, 2, 3))
            out.append(f"  {name}: {tot[0]} operations + {tot[1]} loads + {tot[2]} stores = {sum(tot)}; registers {registers[name]} of 16; "
                       + "; ".join(f"{r[0]} {r[1]}+{r[2]}" + (f"+{r[3]}" if r[3] else "") for r in rows))
        out.append(f"  batch, stage A {sa[0]} + {sa[1]} = {sum(sa)}; stage 2 {st[0]} + {st[1]} = {sum(st)}")
        mid = tuple(sum(r[i] for r in shape["middle step"]) for i in (1, 2, 3))
        short.append(f"rule {n}, every read a load: stage A {sa[0]}+{sa[1]}={sum(sa)}, stage 2 {st[0]}+{st[1]}={sum(st)}, registers "
                     f"{registers['batch']}, middle step {mid[0]}+{mid[1]}+{mid[2]}={sum(mid)}; lanes right {right}/{7 * cases}; ok {ok}")
    out.append("")
    out.append("RESULT: " + ("all counts hold" if good else "FAILED"))
    write("every_use.txt", out)
    print("\n".join(short))
    print("RESULT: " + ("all counts hold" if good else "FAILED") + "  (detail in work/evidence/every_use.txt)")
    return 0 if good else 1


if __name__ == "__main__":
    sys.exit(main())
