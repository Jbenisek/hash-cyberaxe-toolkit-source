#!/usr/bin/env python3
"""The counts of the program of research/pkg7 on the independent tracer of research/pkg7_prep/opt_verify.

    python -B work/tools/tracer_counts.py [cases per rule, default 300]     writes work/evidence/tracer_counts.txt

research/pkg7_prep/opt_verify/ov_tracer.py is a counting machine written by the agent that checked the recoded
batch; it shares no code with the Machine class of the program (read its head for what it does). It is imported
from where it is and not changed. Here the four counted pieces of the program (outer_step, table_build,
middle_step, packed_batch) are run with that tracer in the place of the program's machine, for the rules with four,
six and eight conditions, and from the recorded instruction list alone the tool gives:

  - operations, loads and stores per piece; stage A = the instructions of the batch up to its second
    compare-and-branch, stage 2 = the rest;
  - the smallest register file that runs each piece (a file that refuses: two counters, a word takes a free register
    when it is made, a loaded operand too, and keeps it to its last read; a kept word to its release), and that the
    file of the program's line REGISTERS runs the batch while one register less is refused;
  - faults of the tracer (a carry across a lane boundary, a stored lane above 2^32 - 1, an operand of another
    machine), which must be none;
  - that the flags and the stage-2 words that the batch returns on the tracer are those it returns on the
    program's own machine, in every case, and that the instruction list is the same in every case.

Exit status 0 only if the counts equal the program's TABLES and all of the above holds. Research helper.
"""
import random
import sys

from common import RESEARCH, RULES, program_with_rule, sha, write

sys.path.insert(0, str(RESEARCH / "pkg7_prep" / "opt_verify"))
from ov_tracer import Refused, Tracer, allocate, cost, fits, stages          # noqa: E402

PIECES = ("outer step", "table build", "middle step", "batch")


def main():
    cases = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    out = [f"PROGRAM sha256 {sha()}; python -B work/tools/tracer_counts.py {cases}; tracer: research/pkg7_prep/opt_verify/ov_tracer.py"]
    good, short = True, []
    for n in RULES:
        hs = program_with_rule(n)
        rng = random.Random(4100 + n)
        first, same_list, same_result, faults = None, 0, 0, 0
        for case in range(cases):
            seven = [rng.getrandbits(32) for _ in range(7)]
            if case % 5 == 4:
                seven = [rng.choice((0, hs.MASK, v, v)) for v in seven]
            j = hs.BATCHES - 1 if case % 4 == 0 else rng.randrange(hs.BATCHES)
            c = hs.memory(seven)
            ms = {name: Tracer(hs) for name in PIECES}
            hs.outer_step(ms["outer step"], c)
            row = hs.table_build(ms["table build"], c, j)
            hs.middle_step(ms["middle step"], c)
            mine = hs.packed_batch(ms["batch"], c, row, j)
            c2 = hs.memory(seven)
            hs.outer_step(hs.Machine(), c2)
            row2 = hs.table_build(hs.Machine(), c2, j)
            hs.middle_step(hs.Machine(), c2)
            theirs = hs.packed_batch(hs.Machine(), c2, row2, j)
            same_result += int(tuple(mine) == tuple(theirs) and row == row2 and c == c2)
            faults += sum(len(m.faults) for m in ms.values())
            shape = {name: [(ins[0], ins[1], ins[3]) for ins in ms[name].trace] for name in PIECES}
            if first is None:
                first, traces = shape, {name: ms[name].trace for name in PIECES}
            same_list += int(shape == first)
        sa, s2 = stages(traces["batch"])
        got = {"stage A": cost(sa), "stage 2": cost(s2)}
        table = hs.TABLES["batch"]
        want = {"stage A": tuple(sum(r[i] for r in table[:hs.STAGE_A_PARTS]) for i in (1, 2, 3)),
                "stage 2": tuple(sum(r[i] for r in table[hs.STAGE_A_PARTS:]) for i in (1, 2, 3))}
        smallest = {}
        for name in PIECES:
            if name != "batch":
                got[name] = cost(traces[name])
                want[name] = tuple(sum(r[i] for r in hs.TABLES[name]) for i in (1, 2, 3))
            peak = allocate(traces[name], 10 ** 4)[0]
            smallest[name] = peak
            if not fits(traces[name], peak) or fits(traces[name], peak - 1):
                smallest[name] = None
        try:
            allocate(traces["batch"], hs.REGISTERS)
            runs = True
        except Refused:
            runs = False
        less = fits(traces["batch"], hs.REGISTERS - 1)
        ok = (got == want and same_list == cases and same_result == cases and faults == 0 and runs and not less
              and None not in smallest.values() and max(smallest.values()) <= hs.REGISTERS)
        good &= ok
        out.append(f"RULE WITH {n} CONDITIONS, {cases} cases: instruction list the same in {same_list}, results of the batch on the "
                   f"tracer equal to those on the program's machine (and the memory and the table words) in {same_result}, faults "
                   f"{faults}")
        out.append("   from the instruction list (operations, loads, stores): " + "; ".join(
            f"{name} {got[name][0]}+{got[name][1]}+{got[name][2]}" for name in ("stage A", "stage 2", "outer step", "table build",
                                                                             "middle step"))
            + f"; equal to TABLES of the program: {got == want}")
        out.append(f"   smallest register file that runs each piece: " + ", ".join(f"{name} {smallest[name]}" for name in PIECES)
                   + f"; the batch on a file of {hs.REGISTERS}: {'runs' if runs else 'REFUSED'}; on {hs.REGISTERS - 1}: "
                   f"{'RUNS' if less else 'refused'}; {'ok' if ok else 'FAIL'}")
        short.append(f"rule {n}: stage A {got['stage A'][0]}+{got['stage A'][1]}, stage 2 {got['stage 2'][0]}+{got['stage 2'][1]}, "
                     f"smallest file for the batch {smallest['batch']} (15 refused: {not less}), middle step {smallest['middle step']}; "
                     f"equal to TABLES {got == want}; {'ok' if ok else 'FAIL'}")
    out.append("RESULT: " + ("the tracer confirms the counts and the registers" if good else "FAILED"))
    write("tracer_counts.txt", out)
    print("\n".join(short + [out[-1]]))
    return 0 if good else 1


if __name__ == "__main__":
    sys.exit(main())
