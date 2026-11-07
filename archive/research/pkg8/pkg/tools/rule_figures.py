#!/usr/bin/env python3
"""The figures of the three rules side by side, for the owner's choice of the rule and of the factor. Research helper.

    python -B tools/rule_figures.py            prints the table and writes evidence/rule_figures.txt

Nothing here is a claim of the package; the package states what tools/pkg6_data.py holds. Every figure is either
counted here on the program's machine, or read from a file that the output names, or arithmetic on those:

  - operations, loads and registers per rule: one batch on the program's machine, with the line RULE_CONDITIONS of
    the program set in memory (no file is touched); the long self-tests in evidence/ are quoted next to it while
    they are for the program as it is now;
  - the share of the trials that satisfy a rule and of the batches that enter stage 2: evidence/rule_share_h8_*.txt;
  - the conservative counts: evidence/conservative_h8.txt (tools/conservative_h8.py: every outcome with a
    solution that violates the rule left out, over ALL betas with a part that were counted in full);
  - the budgeted cost per trial and time_log2: the arithmetic of derive() in tools/pkg6_data.py
    (trials 2^(127 - F); per value of X14 list words * (stage A + stage 2 * share) + PREP_OPS; total exponent
    T + log2(charge) - log2(430), plus 0.01123, rounded up as derive() does).
"""
import hashlib
import importlib.util
import json
import math
import re
import sys
import types
from fractions import Fraction
from pathlib import Path

sys.dont_write_bytecode = True
TOOLS = Path(__file__).resolve().parent
PKG = TOOLS.parent
sys.path.insert(0, str(TOOLS))
import pkg6_data as data  # noqa: E402

PROGRAM = data.PROGRAM
H8 = PKG.parent / "h8" / "batch"


def program_with_rule(n):
    """The program with RULE_CONDITIONS = n, in memory."""
    text = PROGRAM.read_text(encoding="ascii")
    new, count = re.subn(r"^RULE_CONDITIONS = .*$", f"RULE_CONDITIONS = {n}", text, flags=re.M)
    assert count == 1
    module = types.ModuleType(f"halfsearch_rule{n}")
    exec(compile(new, f"halfsearch.py with RULE_CONDITIONS = {n}", "exec"), module.__dict__)
    return module


def counted(hs):
    """One batch on the machine: (stage A operations, loads, stage 2 operations, loads, registers, loads by name per stage)."""
    seven = [0x9E3779B9 * (i + 1) & 0xFFFFFFFF for i in range(7)]
    X, S, w, c0 = hs.context(seven)
    c = hs.batch_constants(X, S, w, c0)[0]
    names = {}
    for name, value in c.items():
        names.setdefault(value, name)
    for r in (7, 8, 12, 16, 24, 31):
        names.setdefault(hs.rep((1 << (32 - r)) - 1), f"mask of rotation {r}, low part")
        names.setdefault(hs.rep(((1 << r) - 1) << (32 - r)), f"mask of rotation {r}, high part")
    loads = []

    class Tally(hs.Machine):
        def load(self, constant):
            loads.append((self.part, names.get(constant, "list word or counter limit")))
            return super().load(constant)

    m = Tally()
    hs.packed_batch(m, c, 5)
    parts = list(m.ops)
    a, s2 = parts[:hs.STAGE_A_PARTS], parts[hs.STAGE_A_PARTS:]
    by_name = {}
    for part, name in loads:
        by_name.setdefault(name, [0, 0])[0 if part in a else 1] += 1
    return (sum(m.ops[p] for p in a), sum(m.loads[p] for p in a), sum(m.ops[p] for p in s2), sum(m.loads[p] for p in s2),
            m.registers(), by_name)


def long_selftest(n, sha):
    """The long self-test of rule n in evidence/, if it is for the program as it is: (file, cases, lanes right, lanes, dict)."""
    best = None
    for path in sorted((PKG / "evidence").glob(f"selftest_*_rule{n}_*.json")):
        lines = path.read_text(encoding="ascii").split("\n")
        head = re.match(rf"PROGRAM sha256 ([0-9a-f]{{64}}) RULE_CONDITIONS {n} \(package: \d\) copy sha256 [0-9a-f]{{64}} exit (\d+) seconds (\d+)$", lines[0])
        if not head or head.group(1) != sha or head.group(2) != "0" or len(lines) < 2 or not lines[1].startswith("{"):
            continue
        d = json.loads(lines[1])
        if best is None or d["cases"] > best[1]:
            best = (path.name, d["cases"], d["lanes_right"], d["lanes_checked"], d)
    return best


def conservative():
    """rule number -> (outcomes that can violate it, count without them), from evidence/conservative_h8.txt."""
    out = {}
    path = data.EVID / "conservative_h8.txt"
    if path.exists():
        for line in path.read_text().split("\n"):
            m = re.match(r"RULE (\d) \| outcomes \d+ \| no violating solution \d+ \| violating solution (\d+) .*?\| conservative count "
                         r"\d+ / \d+ = ([0-9,.]+) \|", line)
            if m:
                out[int(m.group(1))] = (int(m.group(2)), float(m.group(3).replace(",", "")))
    return out


def time_log2(T, charge):
    """total exponent as stated, its bound with two decimals, time_log2 (the three lines of derive())."""
    main = T + math.log2(charge) - math.log2(data.C_UNIT)
    total = math.floor((data.up(main, 5) + 0.01123) * 1e4 + 1) / 1e4
    bound = data.up(total, 2)
    return total, bound, data.up(bound, 1)


def main():
    sha = hashlib.sha256(PROGRAM.read_bytes()).hexdigest()
    share = data.read_rule_share_h8()
    cons = conservative()
    out = [f"PROGRAM sha256 {sha}",
           f"class eta {data.ETA:08x}, pin H8, lengths {data.LEN_A} and {data.LEN_B}; the package uses the rule with "
           f"{data.RULE_CONDITIONS} conditions, factor 2^{data.LOG2_FACTOR}, charge {data.CHARGE} (provisional), PREP_OPS {data.PREP_OPS} "
           f"(a bound; evidence/prep_count.txt has the count of that work)",
           ""]
    members = None
    for n in sorted(data.RULES):
        hs = program_with_rule(n)
        a_ops, a_loads, s_ops, s_loads, registers, by_name = counted(hs)
        members, words = hs.CLASS_SIZE, hs.BATCHES
        log_share = n - 3
        assert (a_ops, a_loads) == data.STAGE_A_BY_RULE[n] and (s_ops, s_loads) == (data.STAGE_2_OPS, data.STAGE_2_LOADS)
        assert hs.STAGE_2_LOG2_SHARE == log_share
        a, s2 = a_ops + a_loads, s_ops + s_loads
        per_x14 = words * a + Fraction(words * s2, 2 ** log_share) + data.PREP_OPS
        budgeted = per_x14 / members
        out.append(f"RULE WITH {n} CONDITIONS")
        out.append(f"  machine (one batch counted here): stage A {a_ops} operations + {a_loads} loads = {a}; stage 2 {s_ops} + {s_loads} = {s2}; "
                   f"registers {registers} of {hs.REGISTERS}")
        st = long_selftest(n, sha)
        if st:
            d = st[4]
            out.append(f"  long self-test evidence/{st[0]}: {st[1]:,} batches, {st[2]:,} of {st[3]:,} lanes right against the complete digests; "
                       f"stage A {d['stage_a']['operations']} + {d['stage_a']['loads']}, stage 2 {d['stage_2']['operations']} + "
                       f"{d['stage_2']['loads']}, registers {d['registers']}, largest lane of a sum {d['largest_lane'] / 2 ** 32:.3f} * 2^32, "
                       f"same counts in every case {d['same_counts_in_every_case']}")
        else:
            out.append("  long self-test: no file in evidence/ for the program as it is now")
        out.append(f"  stage-2 budget: a share 1/{2 ** log_share} of the batches; budgeted cost per trial "
                   f"({words:,} * {a} + {words:,} * {s2} / {2 ** log_share} + {data.PREP_OPS}) / {members:,} = {float(budgeted):.4f}")
        if share:
            r = share[n]
            rate = Fraction(r["passes"], share["trials"])
            ent = Fraction(r["entered"], share["batches"])
            expected = (words * a + words * s2 * ent + data.PREP_OPS) / members
            out.append(f"  measured (evidence/rule_share_h8_{share['contexts']}_{data.RULE_SHARE_H8_RUN[1]}.txt, {share['trials']:,} real trials): "
                       f"trials that satisfy the rule 2^-{r['log2']:.4f}; 7 times that share {float(7 * rate):.6f} "
                       f"({'below' if 7 * rate < Fraction(1, 2 ** log_share) else 'NOT BELOW'} the budget {1 / 2 ** log_share:.4f}, "
                       f"which is larger by a factor of {float(Fraction(1, 2 ** log_share) / (7 * rate)):.3f}); batches that enter stage 2 "
                       f"{float(ent):.6f} (per context between {r['smallest']:.4f} and {r['largest']:.4f}); cost per trial at that "
                       f"measured share {float(expected):.4f} (information; the package budgets the larger share)")
        else:
            out.append("  measured shares: no usable file of tools/rule_share_h8.py for the program as it is now")
        if n in cons:
            out.append(f"  conservative count (evidence/conservative_h8.txt, rule with {n} conditions; all betas counted in full): {cons[n][1]:,.1f} "
                       f"({cons[n][0]} outcomes left out)")
        for F in (24, 25, 26):
            T = 127 - F
            margin = f"{cons[n][1] / 2 ** F:.3f}" if n in cons else "unknown"
            row = f"  factor 2^{F} ({2 ** F:,}): count / factor = {margin}; trials 2^{T};"
            for wanted in (0.030, 0.038, 0.044):
                charge = math.ceil(float(budgeted) * (1 + wanted) * 10 - 1e-9) / 10
                total, bound, t = time_log2(T, charge)
                row += f" charge {charge:.1f} (margin {100 * (charge / float(budgeted) - 1):.1f}%): total below 2^{bound:.2f}, time_log2 {t:.1f};"
            out.append(row.rstrip(";"))
        if n == data.RULE_CONDITIONS:
            total, bound, t = time_log2(127 - data.LOG2_FACTOR, data.CHARGE)
            out.append(f"  as the data module has it now: factor 2^{data.LOG2_FACTOR}, charge {data.CHARGE} (margin "
                       f"{100 * (data.CHARGE / float(budgeted) - 1):.1f}%): total below 2^{bound:.2f}, time_log2 {t:.1f}")
            repeated = sorted(((v[0] + v[1], name, v) for name, v in by_name.items() if v[0] + v[1] > 1), reverse=True)
            out.append("  constants loaded more than once in a batch (stage A, stage 2): "
                       + "; ".join(f"{name} ({v[0]}, {v[1]})" for _, name, v in repeated))
        out.append("")
    out.append("Charges are rounded up to one decimal from the budgeted cost times 1.030, 1.038 and 1.044 (the filed package has a margin of 3.7%).")
    out.append("The margin count / factor of the earlier packages was 3.4 to 3.6.")
    text = "\n".join(out) + "\n"
    (PKG / "evidence" / "rule_figures.txt").write_bytes(text.encode("ascii"))
    print(text, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
