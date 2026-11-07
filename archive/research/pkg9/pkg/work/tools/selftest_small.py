#!/usr/bin/env python3
"""The short self-test runs that step 1 of tools/selftest_pkg6.py makes for the package before this one.

    python -B work/tools/selftest_small.py      writes work/evidence/selftest_small.txt

The program's self-test with 2000 cases and seed text 1 (head of its JSON line, the checks on its fields), the same
again (same bytes), a second seed text with 500 cases, wrong arguments, and the number of distinct rotation masks
that the four counted pieces load. Research helper, not submitted.
"""
import json
import subprocess
import sys
import time

from common import PROGRAM, program, sha, write


def run(*args):
    return subprocess.run([sys.executable, "-B", "-s", str(PROGRAM), *args], stdin=subprocess.DEVNULL, capture_output=True)


def main():
    out = [f"TIER {__import__('common').TIER}; PROGRAM sha256 {sha()}; python -B work/tools/selftest_small.py"]
    fails = []

    def need(ok, what):
        out.append(f"  [{'ok' if ok else 'FAIL'}] {what}")
        if not ok:
            fails.append(what)

    start = time.time()
    done = run("--selftest", "2000", "1")
    text = done.stdout.decode("utf-8", "replace").strip()
    out.append(f"python3 halfsearch.py --selftest 2000 1: exit status {done.returncode}, {time.time() - start:.1f} s, "
               f"{len(text.splitlines())} line(s), {len(text)} characters")
    need(done.returncode == 0 and len(text.splitlines()) == 1, "self-test exit status 0 and exactly one line")
    if done.returncode == 0:
        r = json.loads(text)
        need(r["lanes_right"] == r["lanes_checked"] == 7 * r["cases"] and r["cases_stored_right"] == r["cases"]
             and r["message_bytes"] == [55, 63],
             f"every lane right against the complete digests of its two messages of 55 and 63 bytes ({r['lanes_right']} of "
             f"{r['lanes_checked']}); stored words right in {r['cases_stored_right']} of {r['cases']} cases")
        need(r["counts_equal_table"] and r["same_counts_in_every_case"],
             f"rule A with {r['rule_conditions']} conditions: stage A {r['stage_a']['operations']} operations and {r['stage_a']['loads']} "
             f"loads, stage 2 {r['stage_2']['operations']} and {r['stage_2']['loads']}; outer step "
             f"{r['outer_step']['operations']}+{r['outer_step']['loads']}+{r['outer_step']['stores']}, table build "
             f"{r['table_build']['operations']}+{r['table_build']['loads']}+{r['table_build']['stores']}, middle step "
             f"{r['middle_step']['operations']}+{r['middle_step']['loads']}+{r['middle_step']['stores']} (operations+loads+stores); "
             "per part as in TABLES, in every case")
        need(r["sums_below_bounds"], "every sum below the bound of its part: "
             + ", ".join(f"{p} {v['largest_sum']} < {v['bound']}" for p, v in r["parts"].items() if "bound" in v))
        need(r["zero_lane_patterns_right"] == 128 and r["rule_a_patterns_right"] == r["rule_a_patterns"],
             f"flags right on all 128 patterns of zero lanes and on all {r['rule_a_patterns']} words of rule A patterns (every "
             f"pattern of the bits of z that the rule reads with every pattern of the free bits {r['rule_a_on_z']['free_bits_of_e1']} "
             f"of e1, once in every lane; in {r['rule_a_patterns_satisfied']} words a lane satisfies the rule)")
        regs = (r["registers"], r["outer_step"]["registers"], r["table_build"]["registers"], r["middle_step"]["registers"])
        limit = {"strict": 16, "light": 64}[__import__("common").TIER]
        out.append(f"    words kept in registers during a class loop: {r['words_kept_in_registers']}; loaded again by stage 2: "
                   f"{r['words_loaded_again_by_stage_2']}; reads of a kept word (no load): stage A {r['stage_a']['uses']}, "
                   f"stage 2 {r['stage_2']['uses']}")
        need(max(regs) <= r["register_limit"] == limit and r["members_in_list"] == 2 ** 17 == r["class"]["members"]
             and (r["class"]["mask"], r["class"]["value"]) == ("07ef8303", "030c0303"),
             f"registers: batch {regs[0]}, outer step {regs[1]}, table build {regs[2]}, middle step {regs[3]}, of {r['register_limit']}; "
             f"the list holds {r['members_in_list']} members in {r['list_words']} words; words stored per outer step "
             f"{r['words_stored_per_outer_step']}, per value of X2 {r['words_stored_per_x2']}")
        out.append(f"    largest lane of a sum: batch {r['largest_lane_bits']} bits, outer step {r['outer_step']['largest_lane_bits']}, "
                   f"table build {r['table_build']['largest_lane_bits']}, middle step {r['middle_step']['largest_lane_bits']} (of {r['lane_bits']}); "
                   f"lanes that satisfy rule A: {r['lanes_passing_rule_a']} of {r['lanes_checked']}; batches that enter stage 2: "
                   f"{r['batches_entering_stage_2']} of {r['cases']} (every fourth case is the short last batch)")
        again = run("--selftest", "2000", "1")
        need(again.stdout == done.stdout, "the self-test prints the same bytes when repeated")
        other = run("--selftest", "500", "another seed")
        need(other.returncode == 0, "a second seed text (500 cases) also ends with exit status 0")
        bad = run("--selftest")
        need(bad.returncode != 0 and not bad.stdout, "wrong arguments end with a usage message and no output on stdout")
    hs = program()
    masks = set()

    class Tally(hs.Machine):
        def pror(self, z, r):
            masks.update((hs.rep((1 << (32 - r)) - 1), hs.rep(((1 << r) - 1) << (32 - r))))
            return super().pror(z, r)

    c = hs.memory([0x9E3779B9 * (i + 1) & 0xFFFFFFFF for i in range(7)])
    hs.outer_step(Tally(), c)
    row = hs.table_build(Tally(), c, 5)
    hs.middle_step(Tally(), c)
    hs.packed_batch(Tally(), c, row, 5)
    out.append(f"    distinct rotation masks loaded by the four pieces (constants, 256-bit words): {len(masks)}")
    out.append("RESULT: " + ("all steps hold" if not fails else "FAILED: " + "; ".join(fails)))
    print(write("selftest_small.txt", out)[-1500:], end="")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
