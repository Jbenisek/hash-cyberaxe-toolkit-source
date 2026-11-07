#!/usr/bin/env python3
"""count-cost reviewer: the package's counting machine on fresh seeds, for the three rules, and the work per X14.

    python -B count-cost_machine.py [batches for rule 5, default 12000] [batches for rules 4 and 6, default 4000]

Rule 5: the program of the package is run where it lies (python -B, nothing is written there). Rules 4 and 6: a
copy of the program with the one line RULE_CONDITIONS changed is written into review/ and run. Three processes.
Then the work per value of X14 is counted again with the functions of tools/prep_count.py on contexts of my own
(its main() is not called, so the package's evidence file is not rewritten).
Output: review/count-cost_machine.out and at most ten lines.
"""
import hashlib
import importlib.util
import json
import random
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
PKG = HERE.parent
PROGRAM = PKG / "blake3-r2" / "experiments" / "halfsearch.py"
SEED = "count-cost 2026-10-06 fresh"
EXPECT = {4: (52, 31), 5: (55, 32), 6: (58, 33)}


def main():
    n5 = sys.argv[1] if len(sys.argv) > 1 else "12000"
    n46 = sys.argv[2] if len(sys.argv) > 2 else "4000"
    raw = PROGRAM.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    src = raw.decode("utf-8")
    if src.count("RULE_CONDITIONS = 5\n") != 1:
        raise SystemExit("the program does not have exactly one line RULE_CONDITIONS = 5")
    procs = {5: subprocess.Popen([sys.executable, "-B", str(PROGRAM), "--selftest", n5, SEED], stdout=subprocess.PIPE, text=True)}
    for n in (4, 6):
        copy = HERE / f"count-cost_halfsearch_rule{n}.py"
        copy.write_bytes(src.replace("RULE_CONDITIONS = 5\n", f"RULE_CONDITIONS = {n}\n").encode("utf-8"))
        procs[n] = subprocess.Popen([sys.executable, "-B", str(copy), "--selftest", n46, SEED], stdout=subprocess.PIPE, text=True)
    out, good = [f"program sha256 {sha}; seed text '{SEED}'"], True
    for n in (4, 5, 6):
        text, _ = procs[n].communicate()
        r = json.loads(text)
        ok = (procs[n].returncode == 0 and r["lanes_right"] == r["lanes_checked"] and r["rule_conditions"] == n
              and (r["stage_a"]["operations"], r["stage_a"]["loads"]) == EXPECT[n]
              and (r["stage_2"]["operations"], r["stage_2"]["loads"]) == (115, 48) and r["same_counts_in_every_case"]
              and r["counts_equal_table"] and r["sums_below_bounds"] and r["registers"] <= 16 and r["members_in_list"] == 524288
              and r["list_words"] == 74899 and r["zero_lane_patterns_right"] == 128 and r["rule_a_patterns_right"] == r["rule_a_patterns"]
              and r["stage_2_log2_share"] == n - 3)
        good = good and ok
        out.append(f"RULE {n}: exit {procs[n].returncode}, batches {r['cases']}, lanes right {r['lanes_right']} of {r['lanes_checked']}, stage A "
                   f"{r['stage_a']['operations']} + {r['stage_a']['loads']}, stage 2 {r['stage_2']['operations']} + {r['stage_2']['loads']}, "
                   f"registers {r['registers']}, largest lane {r['largest_lane'] / 2 ** 32:.3f} * 2^32, lanes satisfying the rule "
                   f"{r['lanes_passing_rule_a']} (share 2^{__import__('math').log2(r['lanes_passing_rule_a'] / r['lanes_checked']):.3f}), batches entering stage 2 "
                   f"{r['batches_entering_stage_2']} of {r['cases']}, constants per context {r['per_context_constants']}, per X14 "
                   f"{r['per_x14_constants']}, all as the text says: {ok}")
        out.append("JSON " + text.strip())
    # the work per value of X14, with the tool's own functions on my contexts
    sys.path.insert(0, str(PKG / "tools"))
    spec = importlib.util.spec_from_file_location("prep_count_pkg6", PKG / "tools" / "prep_count.py")
    pc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pc)
    hs = pc.load_program()

    class Counting(hs.Machine):
        def __init__(self):
            super().__init__()
            self.stores = {}

        def at(self, part):
            super().at(part)
            self.stores[part] = 0

        def store(self, x):
            self.stores[self.part] += 1
            self.step += 1
            x.last = self.step
            return x.z

    rng = random.Random(987654321)
    shapes, equal, registers, largest, cases = set(), 0, 0, 0, 3000
    for case in range(cases):
        seven = [rng.getrandbits(32) for _ in range(7)]
        if case % 3 == 0:
            seven[1] &= 0x7FFFF                                   # vd in the range of the algorithm
        if case % 7 == 6:
            seven = [(0, hs.MASK, v, v)[rng.randrange(4)] for v in seven]
        per_context, fixed = pc.outer(hs, seven[0], seven[1], seven[2], seven[3], seven[4], seven[6])
        mem = {name: hs.rep(value) for group in (per_context, fixed) for name, value in group.items()}
        m = Counting()
        got = pc.prepare(hs, m, mem, hs.rep(seven[5] - 1), hs.rep(rng.getrandbits(32)))
        c = hs.batch_constants(*hs.context(seven))[0]
        equal += int(len(got) == 13 and all(got[name] == c[name] for name in pc.FOR_X14))
        shapes.add((sum(m.ops.values()), sum(m.loads.values()), sum(m.stores.values())))
        registers = max(registers, m.registers())
        largest = max(largest, max(m.sums.values()))
    ok = equal == cases and len(shapes) == 1 and registers <= 16 and largest < 1 << 36 and sum(next(iter(shapes))) <= 1024
    good = good and ok
    o, l, s = next(iter(shapes))
    out.append(f"work per X14 on {cases} contexts of mine: {o} operations + {l} loads + {s} stores = {o + l + s} (same in every case "
               f"{len(shapes) == 1}); the thirteen stored constants equal those of the batch in {equal} of {cases}; registers {registers}; "
               f"largest lane {largest / 2 ** 32:.3f} * 2^32; below the charged 1024: {o + l + s <= 1024}")
    out.append("RESULT: " + ("all as the text says" if good else "DIFFERENCES"))
    (HERE / "count-cost_machine.out").write_text("\n".join(out) + "\n", encoding="ascii", newline="\n")
    for line in out:
        if not line.startswith("JSON"):
            print(line[:420])
    return 0 if good else 1


if __name__ == "__main__":
    sys.exit(main())
