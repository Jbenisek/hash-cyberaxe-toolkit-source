#!/usr/bin/env python3
"""The cost table of the program of research/pkg7: expected, budgeted and charged per trial, and time_log2.

    python -B work/tools/cost.py          writes COST.txt in research/pkg7

Nothing here is a claim of a package: the package is a draft. Every figure is counted here on the program's own
machine, or read from a file that the output names, or arithmetic on those (tools/pkg7_data.py has the arithmetic):

  - operations, loads and stores of the four counted pieces, per rule (4, 6, 8 conditions; the line
    RULE_CONDITIONS set in memory): the program's batch_check on contexts drawn here. Every lane of these cases must
    be right, the counts must be the same in every case, equal to the program's TABLES and equal to the figures
    typed in tools/pkg7_data.py, or the tool stops. The rows "every read a load" are the same program with the line
    KEPT = 0 set in memory (no word kept in a register; the reading of the text of the filed package);
  - budget on the batches that enter stage 2: a share 2^-(n - 3) of the batches for the rule with n conditions
    (the line STAGE_2_BUDGET of the program). NOT a measured share;
  - expected: the same with the share 1 - (1 - 2^-n)^7 (independent trials that satisfy the rule with 2^-n);
  - per trial: (list words * batch + middle step + (list words * table build + outer step) / 2^32) / members;
  - charged = budgeted * 1.04, rounded up to 0.1;
  - time_log2 = 123.339 - log2(f) + log2(charged / 34) + 0.012, with f = kept count / margin;
  - kept counts: research/pkg7/count/a15_totals.txt (step COUNT), exact and conservative.

The long self-test and the entry measurements in work/evidence are quoted while they are for the program as it is
now (same SHA-256). Research helper, not submitted.
"""
import json
import math
import random
import sys
from pathlib import Path

from common import EVIDENCE, ROOT, RULES, program_with, sha

sys.path.insert(0, str(ROOT / "tools"))
import pkg7_data as data                                                    # noqa: E402


def counted(hs, as_table, cases=40):
    """Stage A, stage 2 as (operations, loads), the three other pieces as (operations, loads, stores), registers."""
    rng = random.Random(1)
    shape, registers = None, {}
    for case in range(cases):
        seven = [rng.getrandbits(32) for _ in range(7)]
        checked, machines = hs.batch_check(seven, hs.BATCHES - 1 if case % 4 == 0 else rng.randrange(hs.BATCHES))
        assert checked["lanes_right"] == 7 and checked["stored_right"] == 1
        found = {name: tuple((p, m.ops[p], m.loads[p], m.stores[p]) for p in m.ops) for name, m in machines.items()}
        shape = shape or found
        assert found == shape
        if as_table:
            assert shape == {name: tuple(r[:4] for r in rows) for name, rows in hs.TABLES.items()}
        for name, m in machines.items():
            registers[name] = max(registers.get(name, 0), m.registers())
    assert max(registers.values()) <= hs.REGISTERS
    b = shape["batch"]
    a, s2 = b[:hs.STAGE_A_PARTS], b[hs.STAGE_A_PARTS:]
    pieces = {name: tuple(sum(r[i] for r in shape[name]) for i in (1, 2, 3)) for name in shape if name != "batch"}
    return ((sum(r[1] for r in a), sum(r[2] for r in a)), (sum(r[1] for r in s2), sum(r[2] for r in s2)), pieces, registers)


def main():
    digest = sha()
    kept, total = data.kept_counts()
    out = [f"COST.txt of research/pkg7 (a DRAFT): cost per trial and time_log2 for the program blake3-r2/experiments/halfsearch.py",
           f"PROGRAM sha256 {digest}; python -B work/tools/cost.py; figures and arithmetic: tools/pkg7_data.py",
           f"sub-class (e1 AND {data.CLASS_MASK:08x}) == {data.CLASS_VALUE:08x}, {data.CLASS_SIZE} members, {data.LIST_WORDS} list "
           f"words; R of the sub-class under the model {float(total):,.2f} (count/a15_totals.txt)",
           f"formula: time_log2 = {data.BASE} - log2(f) + log2(charged / {data.UNIT}) + {data.TAIL}; charged = budgeted * "
           f"{data.MARGIN_ON_COST} rounded up to 0.1; budget on stage 2: a share 2^-(n - 3) of the batches; expected: the share "
           f"1 - (1 - 2^-n)^7", ""]
    rows, problems = {}, []
    for kept_words, label in ((data.KEPT_WORDS, "program"), (0, "every read a load")):
        for n in RULES:
            hs = program_with(n, KEPT=kept_words)
            a, s2, pieces, registers = counted(hs, kept_words == data.KEPT_WORDS)
            rows[label, n] = (a, s2, pieces, registers)
            if kept_words:
                typed = (data.STAGE_A_BY_RULE[n], data.STAGE_2_BY_RULE[n], data.OUTER_STEP, data.TABLE_BUILD, data.MIDDLE_STEP)
                same = (a, s2, pieces["outer step"], pieces["table build"], pieces["middle step"]) == typed \
                    and registers == data.REGISTERS_IN_USE and (hs.CLASS_SIZE, hs.BATCHES) == (data.CLASS_SIZE, data.LIST_WORDS)
            else:
                same = (a, s2) == data.EVERY_READ_A_LOAD[n] and pieces["middle step"] == data.EVERY_READ_MIDDLE_STEP
            if not same:
                problems.append(f"{label}, rule {n}: the machine counts {a}, {s2}, {pieces}, {registers}")
    if problems:
        raise SystemExit("the counts typed in tools/pkg7_data.py are not those of the program's machine:\n  " + "\n  ".join(problems))
    hs = program_with(data.RULE_CONDITIONS)
    assert (hs.FACTOR, hs.CUBE, hs.RULES, hs.REGISTERS, hs.KEPT) == (data.FACTOR, data.CUBE, data.RULES, data.MACHINE_REGISTERS,
                                                                     data.KEPT_WORDS)
    a, s2, pieces, registers = rows["program", data.RULE_CONDITIONS]
    out += ["COUNTS (the program's machine, 40 cases per row, all lanes right, same counts in every case, equal to TABLES and to "
            "tools/pkg7_data.py)",
            f"  outer step {'+'.join(map(str, pieces['outer step']))} = {sum(pieces['outer step'])} (operations + loads + stores); "
            f"table build per list word {'+'.join(map(str, pieces['table build']))} = {sum(pieces['table build'])}; middle step per "
            f"value of X2 {'+'.join(map(str, pieces['middle step']))} = {sum(pieces['middle step'])} (its {data.KEPT_WORDS} loads of the "
            f"class loop entry included)",
            f"  registers in use: batch {registers['batch']}, outer step {registers['outer step']}, table build "
            f"{registers['table build']}, middle step {registers['middle step']}, of {data.MACHINE_REGISTERS}; words kept in registers "
            f"during a class loop: {data.KEPT_WORDS} {list(hs.RESIDENT)}"]
    for label in ("program", "every read a load"):
        out.append(f"  {label}: " + "; ".join(
            f"rule {n}: stage A {rows[label, n][0][0]}+{rows[label, n][0][1]} = {sum(rows[label, n][0])}, stage 2 "
            f"{rows[label, n][1][0]}+{rows[label, n][1][1]} = {sum(rows[label, n][1])}" for n in RULES)
            + f"; middle step {sum(rows[label, RULES[0]][2]['middle step'])}, registers of the batch {rows[label, RULES[0]][3]['batch']}")
    once = (sum(data.TABLE_BUILD) * data.LIST_WORDS + sum(data.OUTER_STEP)) / 2 ** data.X2_VALUES_LOG2 / data.CLASS_SIZE
    out += [f"  amortised per trial: middle step {sum(data.MIDDLE_STEP)} / {data.CLASS_SIZE} = {sum(data.MIDDLE_STEP) / data.CLASS_SIZE:.6f}; "
            f"table build and outer step ({sum(data.TABLE_BUILD)} * {data.LIST_WORDS} + {sum(data.OUTER_STEP)}) / 2^{data.X2_VALUES_LOG2} "
            f"/ {data.CLASS_SIZE} = {once:.3g}; a batch counts as {data.LIST_WORDS} / {data.CLASS_SIZE} = "
            f"1 / {data.CLASS_SIZE / data.LIST_WORDS:.5f} per trial (the last list word has three spare lanes)", ""]

    def table(title, label, which):
        out.append(title)
        out.append("  rule (name) | kept count | stage A, stage 2 | expected | budgeted | charged | "
                   + " | ".join(f"margin {m}: f, log2 f, time_log2" for m in data.MARGINS)
                   + f" | f = {data.FACTOR} (the program's FACTOR): margin, time_log2")
        for n in RULES:
            a, s2, pieces, _ = rows[label, n]
            expected, budgeted, charged = data.cost(n, a, s2, sum(pieces["middle step"]))
            k = float(kept[n][which])
            line = (f"  {n} ({data.RULE_NAMES[n]}) | {k:,.2f} | {sum(a)}, {sum(s2)} | {expected:.4f} | {budgeted:.4f} | {charged:.1f} | ")
            line += " | ".join(f"{k / m:,.0f}, {math.log2(k / m):.4f}, {data.time_log2(k / m, charged):.3f}" for m in data.MARGINS)
            out.append(line + f" | {k / data.FACTOR:.4f}, {data.time_log2(data.FACTOR, charged):.3f}")
        out.append("")

    table("TABLE 1: the program as it is (16 registers, 9 words kept in registers during a class loop, every executed load and "
          "store charged); kept count EXACT", "program", 0)
    table("TABLE 2: the same with the CONSERVATIVE kept count (every outcome with a violating solution in the sub-class dropped whole)",
          "program", 1)
    table("TABLE 3: every read of a memory word a load (the line KEPT = 0; the sentence of the filed text); kept count EXACT",
          "every read a load", 0)
    n = data.RULE_CONDITIONS
    a, s2, pieces, _ = rows["program", n]
    expected, budgeted, charged = data.cost(n, a, s2, sum(pieces["middle step"]))
    k = float(kept[n][0])
    out += [f"RULE IN USE: {n} conditions ({data.RULE_NAMES[n]}): expected {expected:.4f}, budgeted {budgeted:.4f}, charged {charged:.1f}; "
            f"time_log2 {data.time_log2(k / data.MARGINS[0], charged):.3f} at margin {data.MARGINS[0]} and "
            f"{data.time_log2(k / data.MARGINS[1], charged):.3f} at margin {data.MARGINS[1]}; with the program's FACTOR "
            f"{data.FACTOR} (margin {k / data.FACTOR:.4f}): {data.time_log2(data.FACTOR, charged):.3f}",
            f"  one operation or load more in stage A adds {data.LIST_WORDS / data.CLASS_SIZE:.4f} per trial; the charged figure has "
            f"room for {(charged / data.MARGIN_ON_COST - budgeted) * data.CLASS_SIZE / data.LIST_WORDS:.2f} of them before it rises", ""]
    out.append("EVIDENCE QUOTED (for this SHA-256 only)")
    for n in RULES:
        for path in sorted(EVIDENCE.glob(f"selftest_*_rule{n}_*.json")):
            head, _, body = path.read_text(encoding="ascii").partition("\n")
            if f"sha256 {digest} " not in head or " exit 0 " not in head:
                out.append(f"  {path.name}: NOT for this program or not exit 0: {head[:110]}")
                continue
            r = json.loads(body)
            out.append(f"  {path.name}: {r['cases']} cases, exit 0, {r['lanes_right']} of {r['lanes_checked']} lanes right, stored words "
                       f"right in {r['cases_stored_right']}, stage A {r['stage_a']['operations']}+{r['stage_a']['loads']}, stage 2 "
                       f"{r['stage_2']['operations']}+{r['stage_2']['loads']}, counts equal TABLES {r['counts_equal_table']}, registers "
                       f"{r['registers']}, rule A patterns {r['rule_a_patterns_right']} of {r['rule_a_patterns']}; "
                       f"{r['lanes_passing_rule_a']} lanes satisfy the rule, {r['batches_entering_stage_2']} batches enter stage 2 "
                       f"(every fourth case is the short last batch)")
    n = data.RULE_CONDITIONS
    for path in sorted(EVIDENCE.glob("entry_share_*.txt")):
        lines = path.read_text(encoding="ascii").split("\n")
        if f"PROGRAM sha256 {digest} " not in lines[0]:
            continue
        for line in lines:
            if line.startswith(f"RULE {n} "):
                f = [x.strip() for x in line.split("|")]
                out.append(f"  {path.name} (MEASUREMENT, not used in the budget; 2^30 real trials): rule {n}: share of the trials {f[3]}, "
                           f"share of the batches that enter stage 2 {f[5]} (budget {f[8]}); largest and smallest single context "
                           f"{f[9]}; per outer step {f[10]}")
    text = "\n".join(out) + "\n"
    (ROOT / "COST.txt").write_bytes(text.encode("ascii"))
    for line in out:
        if line.startswith(("RULE IN USE", "  8 (S8)", "  6 (old6)")):
            print(line[:260])
    return 0


if __name__ == "__main__":
    sys.exit(main())
