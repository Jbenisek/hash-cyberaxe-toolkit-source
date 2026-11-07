#!/usr/bin/env python3
"""Registers in use per part of the batch, from the program's own lifetimes (the method of Machine.registers()).

    python -B work/tools/register_peaks.py [cases, default 200]     writes work/evidence_<tier>/register_peaks.txt

Machine.registers() gives one number for the whole batch. This tool gives the largest number per part, so that one
sees where the limit is reached: a subclass of the program's Machine notes the step at which every part begins,
and the count per step is formed exactly as registers() forms it (a value, a kept word too, holds a register from
the step that makes it to the step of its last use; two more for the counters). Research helper, not submitted.
"""
import random
import sys

from common import HEAD, RULES, program_with_rule, sha, write


def main():
    cases = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    out = [f"{HEAD}PROGRAM sha256 {sha()}; python -B work/tools/register_peaks.py {cases}"]
    good = True
    for n in RULES:
        hs = program_with_rule(n)

        class Marked(hs.Machine):
            def at(self, part):
                self.__dict__.setdefault("marks", []).append((part, self.step))
                super().at(part)

        rng = random.Random(99 + n)
        shapes = set()
        for case in range(cases):
            seven = [rng.getrandbits(32) for _ in range(7)]
            j = hs.BATCHES - 1 if case % 4 == 0 else rng.randrange(hs.BATCHES)
            c = hs.memory(seven)
            hs.outer_step(hs.Machine(), c)
            row = hs.table_build(hs.Machine(), c, j)
            hs.middle_step(hs.Machine(), c)
            m = Marked()
            hs.packed_batch(m, c, row, j)
            change = [0] * (m.step + 2)
            first = len(hs.RESIDENT)                       # the words that resident() put into registers
            for value in m.values:
                change[value.born] += 1
                change[value.last] -= 1
            held, per_step = 0, []
            for delta in change:
                held += delta
                per_step.append(held)
            marks = m.marks + [("end", m.step + 1)]
            parts = tuple((part, max(per_step[start + 1:marks[i + 1][1] + 1] or [0]) + 2) for i, (part, start) in enumerate(marks[:-1]))
            shapes.add((parts, m.registers(), first))
        one = sorted(shapes)[0]
        ok = len(shapes) == 1 and max(p[1] for p in one[0]) == one[1] <= hs.REGISTERS
        good &= ok
        stage_a = max(p[1] for p in one[0][:hs.STAGE_A_PARTS])
        stage_2 = max(p[1] for p in one[0][hs.STAGE_A_PARTS:])
        out.append(f"RULE WITH {n} CONDITIONS, {cases} batches, one shape {len(shapes) == 1}: registers in use per part (the two counters "
                   f"included): " + ", ".join(f"{part} {peak}" for part, peak in one[0]) + f"; stage A {stage_a}, stage 2 {stage_2}, "
                   f"whole batch {one[1]} of {hs.REGISTERS}; words in registers when the batch begins {one[2]}; "
                   f"{'ok' if ok else 'FAIL'}")
    out.append("RESULT: " + ("consistent with Machine.registers()" if good else "FAILED"))
    text = write("register_peaks.txt", out)
    for line in text.split("\n")[1:]:
        print(line[:330])
    return 0 if good else 1


if __name__ == "__main__":
    sys.exit(main())
