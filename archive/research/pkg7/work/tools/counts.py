#!/usr/bin/env python3
"""Machine counts of the four counted pieces of the program, for the rules with 4, 6 and 8 conditions.

    python -B work/tools/counts.py [cases per rule, default 1500]     writes work/evidence/counts.txt

Every count is taken from the program's own Machine (class Machine of halfsearch.py: every operation 1, every
load 1, every store 1, a rotation 5 operations + 2 loads, a comparison and a branch 2), by running the program's
batch_check on contexts drawn here: one outer step, one word of each list of the table, one middle step and one
packed batch per case, each on a new machine. The rule is set by the one line RULE_CONDITIONS of the program, in
memory. For every rule it reports the counts per part, whether they are the same in every case and equal to the
program's TABLES, the registers and the largest lane of a sum per piece, and how many lanes are right against the
complete digests of the two real messages. It also tallies, by name, the memory cells that each piece loads.
Research helper, not submitted. Nothing but the evidence file is written.
"""
import random
import sys

from common import HEAD, RULES, program_with_rule, rule_text, sha, write


def main():
    cases = int(sys.argv[1]) if len(sys.argv) > 1 else 1500
    out = [f"{HEAD}PROGRAM sha256 {sha()}; python -B work/tools/counts.py {cases}"]
    short = []
    good = True
    for n in RULES:
        hs = program_with_rule(n)
        rng = random.Random(20261006 + n)
        shape, same, right, stored, entered, passing = None, True, 0, 0, 0, 0
        registers = {name: 0 for name in hs.TABLES}
        sums = {name: {} for name in hs.TABLES}
        for case in range(cases):
            seven = [rng.getrandbits(32) for _ in range(7)]
            if case % 5 == 4:
                seven = [rng.choice((0, hs.MASK, v, v)) for v in seven]
            j = hs.BATCHES - 1 if case % 4 == 0 else rng.randrange(hs.BATCHES)
            checked, machines = hs.batch_check(seven, j)
            right += checked["lanes_right"]
            stored += checked["stored_right"]
            entered += checked["stage_2_entered"]
            passing += checked["lanes_passing_rule_a"]
            found = {name: tuple((p, m.ops[p], m.loads[p], m.stores[p]) for p in m.ops) for name, m in machines.items()}
            shape = shape or found
            same = same and found == shape
            uses = dict(machines["batch"].uses)
            for name, m in machines.items():
                registers[name] = max(registers[name], m.registers())
                for p, top in m.sums.items():
                    sums[name][p] = max(sums[name].get(p, 0), top)
        table = {name: tuple(row[:4] for row in rows) for name, rows in hs.TABLES.items()}
        equal = shape == table
        ok = same and equal and right == 7 * cases and stored == cases and max(registers.values()) <= hs.REGISTERS \
            and all(max(s.values()) < 1 << hs.LANE_BITS for s in sums.values())
        good = good and ok
        out.append("")
        out.append(f"RULE WITH {n} CONDITIONS: {cases} cases, {right} of {7 * cases} lanes right, stored words right in {stored} of "
                   f"{cases} cases, same counts in every case {same}, equal to TABLES of the program {equal}; rule A on z: "
                   f"{rule_text(hs)}")
        tot = {}
        for name in hs.TABLES:
            rows = shape[name]
            ops, loads, stores = (sum(r[i] for r in rows) for i in (1, 2, 3))
            largest = max(sums[name].values())
            tot[name] = (ops, loads, stores)
            out.append(f"  {name}: {ops} operations + {loads} loads + {stores} stores = {ops + loads + stores}; registers "
                       f"{registers[name]} of {hs.REGISTERS}; largest lane of a sum {largest / 2 ** 32:.3f} * 2^32 "
                       f"({largest.bit_length()} bits of {hs.LANE_BITS})")
            for p, o, l, s in rows:
                out.append(f"      {p:12s} {o:3d} operations {l:3d} loads {s:2d} stores   largest sum {sums[name][p] / 2 ** 32:.3f} * 2^32")
            if rows != table[name]:
                out.append(f"      TABLES of the program has: {table[name]}")
        a, s2 = shape["batch"][:hs.STAGE_A_PARTS], shape["batch"][hs.STAGE_A_PARTS:]
        sa = (sum(r[1] for r in a), sum(r[2] for r in a))
        st = (sum(r[1] for r in s2), sum(r[2] for r in s2))
        out.append(f"  batch, stage A {sa[0]} + {sa[1]} = {sum(sa)}; stage 2 {st[0]} + {st[1]} = {sum(st)}; in these cases "
                   f"{passing} of {7 * cases} lanes satisfy the rule and {entered} of {cases} batches enter stage 2 (every "
                   f"fourth case is the short last batch)")
        ua, u2 = (sum(uses[r[0]] for r in rows_) for rows_ in (a, s2))
        out.append(f"  machine: {hs.REGISTERS} registers; words kept in registers during a class loop: {len(hs.RESIDENT)} "
                   f"{list(hs.RESIDENT)}; given up by stage 2 and loaded again at its end: {list(hs.EVICT)}; reads of a "
                   f"word kept in a register (no load): stage A {ua}, stage 2 {u2}; so with every read a load the same "
                   f"operations would have {sa[1] + ua} loads in stage A")
        short.append(f"rule {n}: stage A {sa[0]}+{sa[1]}={sum(sa)}, stage 2 {st[0]}+{st[1]}={sum(st)}, registers "
                     f"{registers['batch']}, largest lane {max(sums['batch'].values()).bit_length()} bits; lanes right {right}/{7 * cases}; "
                     f"TABLES equal {equal}; ok {ok}")
        if n == RULES[-1]:
            others = "; ".join(f"{name} {tot[name][0]}+{tot[name][1]}+{tot[name][2]}={sum(tot[name])} (registers {registers[name]}, "
                               f"lane {max(sums[name].values()).bit_length()} bits)" for name in ("outer step", "table build", "middle step"))
            short.append("operations+loads+stores: " + others)
        # the cells every piece loads, by name (one case)
        names = {}
        seven = [0x9E3779B9 * (i + 1) & 0xFFFFFFFF for i in range(7)]
        c = hs.memory(seven)
        loads = []

        class Tally(hs.Machine):
            def load(self, constant):
                loads.append(constant)
                return super().load(constant)

        def cells_of(run):
            del loads[:]
            before = dict(c)
            run()
            where = {}
            for name, value in list(before.items()) + list(c.items()):
                where.setdefault(value, name)
            return sorted({where.get(v, "(rotation mask, list word, table word or counter limit)") for v in loads})

        used = {"outer step": cells_of(lambda: hs.outer_step(Tally(), c))}
        row = {}
        used["table build"] = cells_of(lambda: row.update(hs.table_build(Tally(), c, 5)))
        used["middle step"] = cells_of(lambda: hs.middle_step(Tally(), c))
        used["batch"] = cells_of(lambda: hs.packed_batch(Tally(), c, row, 5))
        by_outer, by_middle = hs.stored(hs.context(seven))
        for name, cells in used.items():
            kinds = {"outer": [x for x in cells if x in by_outer], "middle": [x for x in cells if x in by_middle]}
            rest = [x for x in cells if x not in by_outer and x not in by_middle]
            out.append(f"  {name} loads, by name: stored by the outer step {len(kinds['outer'])} {kinds['outer']}; stored by the "
                       f"middle step {len(kinds['middle'])} {kinds['middle']}; other {len(rest)} {rest}")
    out.append("")
    out.append("RESULT: " + ("all counts hold" if good else "FAILED"))
    write("counts.txt", out)
    print("\n".join(short))
    print("RESULT: " + ("all counts hold" if good else "FAILED") + "  (detail in work/evidence/counts.txt)")
    return 0 if good else 1


if __name__ == "__main__":
    sys.exit(main())
