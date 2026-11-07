#!/usr/bin/env python3
"""Checks around the in-package self-test of the operation count (sixth package). Research helper, not submitted.

    python -B tools/selftest_pkg6.py [--program]

Every step prints its result; the exit status is 0 only if all steps that were run hold. Steps 1 to 4 concern the
experiment program; step 5 concerns the text (proof, claim, note) and is left out with --program.

  1. Runs the self-test of experiments/halfsearch.py and prints the head of its JSON line; a second seed text; a
     repeat (same bytes); wrong arguments.
  2. Cross-checks of the program with the constants of this package:
     (a) tools/build_pkg6.py --program (the program has the constants, the rules and the stage counts of the data
         module); its class members against research/r2_class_ref.py; tools/ref_compare.py (context, trial and
         messages against the reference research/h8/design/h8_ref.py and the test vectors
         research/h8/gpu/out/ref_vectors.txt); and the stage-2 words, their flags and the final branch of its batch
         against the research program in which a batch for this family was first written,
         research/h8/batch/h8_batch.py, on the same inputs. That program has another order of the operations, a
         second list and other counts; when the package uses the rule with four conditions, which is the rule of
         that program, the stage-A flags and branch are compared too;
     (b) the program's reference values of a trial (Y4, h1, the word of Lemma N, the word from the digests) against
         the forward compression of check_pkg6.py, which is written separately;
     (c) one complete class loop (all 74,899 batches of one context);
     (d) tools/lane_bound.py (bounds of the sums for all inputs).
  3. Runs check_pkg6.py --program (formulas written a second time, and the program through its contract).
  4. Runs tools/text_scan_pkg6.py on the program file alone.
  5. Text: tools/proof_lines_check.py (the displays of Section 4 typed again), tools/fmt_pkg6.py,
     check_pkg6.py --text, tools/text_scan_pkg6.py on all public files.
"""
import importlib.util
import json
import random
import struct
import subprocess
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True
TOOLS = Path(__file__).resolve().parent
PKG = TOOLS.parent
PROGRAM = PKG / "blake3-r2" / "experiments" / "halfsearch.py"
sys.path.insert(0, str(TOOLS))
import pkg6_data as data  # noqa: E402

SELFTEST = data.SELFTEST
FAILED, FAILED_TEXT = [], []


def need(ok, what, text=False):
    print(f"  [{'ok' if ok else 'FAIL'}] {what}")
    if not ok:
        (FAILED_TEXT if text else FAILED).append(what)
    return ok


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(*args):
    return subprocess.run([sys.executable, "-B", *[str(a) for a in args]], stdin=subprocess.DEVNULL, capture_output=True)


def step_selftest():
    print(f"1. self-test: python3 experiments/halfsearch.py --selftest {' '.join(SELFTEST)}")
    start = time.time()
    done = run("-s", PROGRAM, "--selftest", *SELFTEST)
    out = done.stdout.decode("utf-8", "replace").strip()
    print(f"  exit status {done.returncode}, {time.time() - start:.1f} s, {len(out.splitlines())} line(s) of output")
    print("  " + (out[:400] + " ..." if out else "(no output) " + done.stderr.decode("utf-8", "replace").strip().splitlines()[-1][:160]))
    need(done.returncode == 0 and len(out.splitlines()) == 1, "self-test exit status 0 and exactly one line")
    if done.returncode == 0:
        report = json.loads(out)
        need(report["lanes_right"] == report["lanes_checked"] == 7 * report["cases"] and report["message_bytes"] == [55, 63],
             f"every lane right against the complete digests of its two messages of 55 and 63 bytes "
             f"({report['lanes_right']} of {report['lanes_checked']})")
        need((report["stage_a"]["operations"], report["stage_a"]["loads"]) == (data.STAGE_A_OPS, data.STAGE_A_LOADS)
             and (report["stage_2"]["operations"], report["stage_2"]["loads"]) == (data.STAGE_2_OPS, data.STAGE_2_LOADS)
             and report["counts_equal_table"] and report["same_counts_in_every_case"]
             and report["rule_conditions"] == data.RULE_CONDITIONS,
             f"rule A with {data.RULE_CONDITIONS} conditions: stage A {data.STAGE_A_OPS} operations and {data.STAGE_A_LOADS} loads, "
             f"stage 2 {data.STAGE_2_OPS} and {data.STAGE_2_LOADS}, per part as in the table, in every case")
        need(report["sums_below_bounds"], "every sum below the bound of its part: "
             + ", ".join(f"{p} {v['largest_sum']} < {v['bound']}" for p, v in report["parts"].items() if "bound" in v))
        need(report["zero_lane_patterns_right"] == 128 and report["rule_a_patterns_right"] == report["rule_a_patterns"],
             f"flags right on all 128 patterns of zero lanes and on all {report['rule_a_patterns']} words of rule A patterns")
        need(report["registers"] <= report["register_limit"] == 16 and report["members_in_list"] == 2 ** 19,
             f"registers {report['registers']} of {report['register_limit']}; the list holds {report['members_in_list']} members in "
             f"{report['list_words']} words; constants per context {report['per_context_constants']}, per X14 {report['per_x14_constants']}")
        print(f"    lanes that satisfy rule A: {report['lanes_passing_rule_a']} of {report['lanes_checked']}; batches that enter "
              f"stage 2: {report['batches_entering_stage_2']} of {report['cases']}")
        other = run("-s", PROGRAM, "--selftest", "500", "another seed")
        again = run("-s", PROGRAM, "--selftest", *SELFTEST)
        need(other.returncode == 0, "a second seed text (500 cases) also ends with exit status 0")
        need(again.stdout == done.stdout, "the self-test prints the same bytes when repeated")
        bad = run("-s", PROGRAM, "--selftest")
        need(bad.returncode != 0 and not bad.stdout, "wrong arguments end with a usage message and no output on stdout")


def step_cross():
    print("2. cross-checks of the program")
    new = load(PROGRAM, "halfsearch_pkg6")
    rng = random.Random(20261006)
    # (a) the data module and the outside references
    done = run(TOOLS / "build_pkg6.py", "--program")
    print("  " + done.stdout.decode("utf-8", "replace").strip()[:330])
    need(done.returncode == 0, "the program has the pin, the lengths, eta, the rules, the stage-2 budget and the stage counts of the data module")
    try:
        ref = load(PKG.parent / "r2_class_ref.py", "r2_class_ref")
        members = ref.class_members(new.ETA, new.Y3, (new.Y3B - new.Y3) & new.MASK)
        need(members == [new.class_member(k) for k in range(new.CLASS_SIZE)],
             f"all {new.CLASS_SIZE} class members equal those of r2_class_ref.py, in order")
    except Exception as error:
        print("  outside reference r2_class_ref.py not usable:", repr(error))
    done = run(TOOLS / "ref_compare.py", "2000", "25")
    for line in done.stdout.decode("utf-8", "replace").splitlines():
        print("  " + line[:230])
    need(done.returncode == 0, "ref_compare.py: constants, class, context, trial and messages equal h8_ref.py and the test vectors")
    h8 = None
    try:
        h8 = load(PKG.parent / "h8" / "batch" / "h8_batch.py", "h8_batch")
    except (Exception, SystemExit) as error:
        print("  research program h8_batch.py not usable:", repr(error))
    if h8 is not None:
        total, same, same_a, four = 300, 0, 0, len(new.RULE_A) == 4
        for _ in range(total):
            seven = [rng.getrandbits(32) for _ in range(7)]
            j = rng.randrange(new.BATCHES)
            X, S, w, c0 = new.context(seven)
            mine = new.packed_batch(new.Machine(), new.batch_constants(X, S, w, c0)[0], j)
            u, v, members = h8.list_words(j)
            theirs = h8.per_member(h8.Machine(), h8.constants(h8.H.context(dict(zip(new.CONTEXT_WORDS, seven)))), u, v, True)
            same += mine[:3] == theirs[:3] and members == new.list_words(j)[1] and u == new.list_words(j)[0]
            same_a += mine[3:] == theirs[3:]
        need(same == total, f"stage-2 words, their flags and the final branch equal those of h8_batch.py in {same} of {total} batches")
        if four:
            need(same_a == total, f"stage-A flags and branch equal those of h8_batch.py (rule with four conditions) in {same_a} of {total} batches")
        else:
            print(f"    (stage A is not compared: h8_batch.py has the rule with four conditions, the package the one with {len(new.RULE_A)})")
    # (b) the reference values of the program against the forward compression of check_pkg6.py
    chk = load(PKG / "check_pkg6.py", "check_pkg6")
    M, ror, rol = chk.M32, chk.ror, chk.rol
    total, good, zero, passing = 3000, 0, 0, 0
    for _ in range(total):
        seven = [rng.getrandbits(32) for _ in range(7)]
        y4 = new.class_member(rng.randrange(new.CLASS_SIZE))
        X, S, w, c0 = new.context(seven)
        A, B = new.messages(new.trial(X, S, w, c0, y4)[0])
        (da, _, _, Ya), (db, _, _, Yb) = chk.hash2(A), chk.hash2(B)
        wa = struct.unpack("<16I", A + bytes(64 - len(A)))
        wb = struct.unpack("<16I", B + bytes(64 - len(B)))
        h1 = ror(Ya[14] ^ ((Ya[3] + Ya[4] + wa[15]) & M), 16)
        outs = []
        for Y, words in ((Ya, wa), (Yb, wb)):
            a1 = (Y[1] + Y[6] + words[12]) & M
            b1 = ror(Y[6] ^ ((Y[11] + ror(Y[12] ^ a1, 16)) & M), 12)
            outs.append((b1, chk.G(Y[1], Y[6], Y[11], Y[12], words[12], words[5])[2]))
        beta, eps = outs[0][0] ^ outs[1][0], outs[0][1] ^ outs[1][1]
        n = chk.ETA ^ eps ^ rol(beta ^ eps, 1)
        r = new.reference(X, S, w, c0, y4)
        good += (r["y4"] == Ya[4] == y4 and r["h1"] == h1 and r["word"] == n == (da[3] ^ db[3]) ^ rol(da[6] ^ db[6], 8)
                 and r["word_from_digests"] == n and r["half"] == 1 and r["words"] == 1 and (len(A), len(B)) == (55, 63)
                 and new.rule_a(h1) == data.rule_a(h1) == chk.rule_on_h1(h1))
        zero += n == 0
        passing += data.rule_a(h1)
    need(good == total, f"reference values of the program (Y4, h1, the word of Lemma N, the word from the digests) equal those from "
                        f"check_pkg6's forward compression of both messages in {good} of {total} trials (zero words: {zero}; "
                        f"trials that satisfy rule A: {passing})")
    # (c) one complete class loop
    X, S, w, c0 = new.context([rng.getrandbits(32) for _ in range(7)])
    right, shapes, seen, entered, passing = 0, set(), set(), 0, 0
    start = time.time()
    for j in range(new.BATCHES):
        r = new.batch_check(X, S, w, c0, j)
        right += r["lanes_right"]
        shapes.add((r["stage_a_operations"], r["stage_a_loads"], r["stage_2_operations"], r["stage_2_loads"]))
        entered += r["stage_2_entered"]
        passing += r["lanes_passing_rule_a"]
        seen.update(new.list_words(j)[1])
    need(right == 7 * new.BATCHES and shapes == {(data.STAGE_A_OPS, data.STAGE_A_LOADS, data.STAGE_2_OPS, data.STAGE_2_LOADS)}
         and len(seen) == new.CLASS_SIZE,
         f"one complete class loop: {new.BATCHES} batches, {right} of {7 * new.BATCHES} lanes right, stage counts {sorted(shapes)}, "
         f"{len(seen)} different members ({time.time() - start:.0f} s)")
    print(f"    in that loop {entered} of {new.BATCHES} batches enter stage 2 ({entered / new.BATCHES:.4f}; budget "
          f"{1 / 2 ** data.STAGE_2_LOG2_SHARE:.3f}); lanes that satisfy rule A: {passing} of {7 * new.BATCHES} (the five spare "
          f"lanes of the last batch repeat the last member)")
    # (d) bounds of the sums for all inputs
    done = run(TOOLS / "lane_bound.py", "2000")
    for line in done.stdout.decode("utf-8", "replace").splitlines():
        print("  " + line[:230])
    need(done.returncode == 0, "lane_bound.py: every sum below the bound of its part for all inputs")


def step_check():
    print("3. check_pkg6.py --program")
    start = time.time()
    done = run(PKG / "check_pkg6.py", "--program")
    lines = done.stdout.decode("utf-8", "replace").splitlines()
    oks = sum("[ok]" in line for line in lines)
    for line in lines:
        if "[ok]" not in line and not line.startswith(("      words of A", "      digest xor", "    first trial")):
            print("  " + line[:230])
    print(f"  lines marked ok: {oks}; exit status {done.returncode}; {time.time() - start:.0f} s")
    need(done.returncode == 0 and any(line.startswith("RESULT (a), (b): all checks of the program passed") for line in lines),
         "check_pkg6.py: all checks of the program passed")
    print("4. tools/text_scan_pkg6.py --program")
    done = run(TOOLS / "text_scan_pkg6.py", "--program")
    for line in done.stdout.decode("utf-8", "replace").splitlines():
        print("  " + line[:230])
    need(done.returncode == 0, "text scan of the program file: nothing found")


def step_text():
    print("5. text: tools/proof_lines_check.py, tools/fmt_pkg6.py (nothing written), check_pkg6.py --text, tools/text_scan_pkg6.py")
    done = run(TOOLS / "proof_lines_check.py", "20000")
    for line in done.stdout.decode("utf-8", "replace").splitlines():
        print("  " + line[:230])
    need(done.returncode == 0, "proof_lines_check.py: steps S1 and T as displayed in Section 4 hold on 20000 trials", text=True)
    done = run(TOOLS / "fmt_pkg6.py")
    for line in done.stdout.decode("utf-8", "replace").splitlines():
        if line.startswith(("   lines over", "proof line count", "H1-", "H2-", "H3-", "claim.json proof ranges", "  note bytes", "  claim:",
                            "rendered files", "  DRIFT", "RESULT", "  main term", "  factor", "  class eta", "  per X14")) or ": proof:" in line:
            print("  " + line[:230])
    if done.returncode != 0 and done.stderr:
        print("  " + done.stderr.decode("utf-8", "replace").strip().splitlines()[-1][:230])
    need(done.returncode == 0, "fmt_pkg6.py exit status 0", text=True)
    done = run(PKG / "check_pkg6.py", "--text")
    for line in done.stdout.decode("utf-8", "replace").splitlines():
        if "[ok]" not in line:
            print("  " + line[:230])
    need(done.returncode == 0, "check_pkg6.py --text: proof.md prints what the check computes", text=True)
    done = run(TOOLS / "text_scan_pkg6.py")
    for line in done.stdout.decode("utf-8", "replace").splitlines():
        print("  " + line[:230])
    need(done.returncode == 0, "text scan of all public files: nothing found", text=True)


def main():
    step_selftest()
    step_cross()
    step_check()
    print("RESULT, program (steps 1 to 4):", "all steps hold" if not FAILED else "FAILED: " + "; ".join(FAILED))
    if "--program" not in sys.argv:
        step_text()
        print("RESULT, text (step 5):", "all steps hold" if not FAILED_TEXT else "FAILED: " + "; ".join(FAILED_TEXT))
    return 1 if FAILED or FAILED_TEXT else 0


if __name__ == "__main__":
    sys.exit(main())
