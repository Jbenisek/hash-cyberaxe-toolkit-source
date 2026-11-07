#!/usr/bin/env python3
"""Checks around the in-package self-test of the operation count (fifth package). Research helper, not submitted.

    python -B tools/selftest_pkg5.py

Always the same command line. Every step prints its result; the exit status is 0 only if all of them hold.

  1. Runs the self-test of experiments/halfsearch.py and prints the head of its JSON line; a second seed text; a
     repeat (same bytes); wrong arguments.
  2. Cross-checks of the program with the constants of this package:
     (a) its class members against research/r2_class_ref.py, and its two-stage batch against the research program
         in which that batch was first written, research/night/cheaper/night_batch4.py, on the same inputs: the
         stage-2 words, both sets of flags, both branches and the counts of the stages (that program reads the
         filed package's halfsearch.py and replaces its constants in memory; no file is touched). This is a check
         that the batch was moved over unchanged, not an independent implementation;
     (b) the program's reference values of a trial (Y4, h1, the word of Lemma N, the word from the digests) against
         the forward compression of check_pkg5.py, which is written separately from the proof's text;
     (c) one complete class loop.
  3. Runs tools/fmt_pkg5.py (nothing is written).
  4. Runs check_pkg5.py.
  5. Runs tools/text_scan_pkg5.py on the files that a submission makes public.
"""
import importlib.util
import json
import os
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
import pkg5_data as data  # noqa: E402

SELFTEST = data.SELFTEST
FAILED = []


def need(ok, what):
    print(f"  [{'ok' if ok else 'FAIL'}] {what}")
    if not ok:
        FAILED.append(what)
    return ok


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def step_selftest():
    print(f"1. self-test: python3 experiments/halfsearch.py --selftest {' '.join(SELFTEST)}")
    start = time.time()
    done = subprocess.run([sys.executable, "-B", "-s", str(PROGRAM), "--selftest", *SELFTEST],
                          stdin=subprocess.DEVNULL, capture_output=True)
    out = done.stdout.decode("utf-8", "replace").strip()
    print(f"  exit status {done.returncode}, {time.time() - start:.1f} s, {len(out.splitlines())} line(s) of output")
    print("  " + (out[:400] + " ..." if out else "(no output) " + done.stderr.decode("utf-8", "replace").strip().splitlines()[-1][:160]))
    need(done.returncode == 0 and len(out.splitlines()) == 1, "self-test exit status 0 and exactly one line")
    if done.returncode == 0:
        report = json.loads(out)
        need(report["lanes_right"] == report["lanes_checked"] == 7 * report["cases"],
             f"every lane right against the complete digests of its two messages ({report['lanes_right']} of {report['lanes_checked']})")
        need((report["stage_a"]["operations"], report["stage_a"]["loads"]) == (data.STAGE_A_OPS, data.STAGE_A_LOADS)
             and (report["stage_2"]["operations"], report["stage_2"]["loads"]) == (data.STAGE_2_OPS, data.STAGE_2_LOADS)
             and report["counts_equal_table"] and report["same_counts_in_every_case"],
             f"stage A {data.STAGE_A_OPS} operations and {data.STAGE_A_LOADS} loads, stage 2 {data.STAGE_2_OPS} and {data.STAGE_2_LOADS}, "
             f"per part as in the table, in every case")
        need(report["sums_below_bounds"], "every sum below the bound that proof.md 6.5 quotes for its part: "
             + ", ".join(f"{p} {v['largest_sum']} < {v['bound']}" for p, v in report["parts"].items() if "bound" in v))
        need(report["zero_lane_patterns_right"] == 128 and report["rule_a_patterns_right"] == report["rule_a_patterns"],
             f"flags right on all 128 patterns of zero lanes and on all {report['rule_a_patterns']} words of rule A patterns")
        print(f"    lanes that satisfy rule A: {report['lanes_passing_rule_a']} of {report['lanes_checked']}; batches that enter "
              f"stage 2: {report['batches_entering_stage_2']} of {report['cases']}; registers {report['registers']}")
        other = subprocess.run([sys.executable, "-B", "-s", str(PROGRAM), "--selftest", "500", "another seed"],
                               stdin=subprocess.DEVNULL, capture_output=True)
        again = subprocess.run([sys.executable, "-B", "-s", str(PROGRAM), "--selftest", *SELFTEST],
                               stdin=subprocess.DEVNULL, capture_output=True)
        need(other.returncode == 0, "a second seed text (500 cases) also ends with exit status 0")
        need(again.stdout == done.stdout, "the self-test prints the same bytes when repeated")
        bad = subprocess.run([sys.executable, "-B", "-s", str(PROGRAM), "--selftest"], stdin=subprocess.DEVNULL, capture_output=True)
        need(bad.returncode != 0 and not bad.stdout, "wrong arguments end with a usage message and no output on stdout")


def step_cross():
    print("2. cross-checks of the program")
    new = load(PROGRAM, "halfsearch_pkg5")
    rng = random.Random(20261006)
    # (a) the outside references
    try:
        ref = load(PKG.parent / "r2_class_ref.py", "r2_class_ref")
        members = ref.class_members(new.ETA, new.Y3, (new.Y3B - new.Y3) & new.MASK)
        need(members == [new.class_member(k) for k in range(new.CLASS_SIZE)], "class members equal those of r2_class_ref.py, in order")
    except Exception as error:
        print("  outside reference r2_class_ref.py not usable:", repr(error))
    night = None
    try:
        os.environ.update(NIGHT_PIN=",".join(f"{getattr(new, k):08x}" for k in ("X3", "X7", "X11", "X15", "W4", "W13")),
                          NIGHT_ETA=f"{new.ETA:08x}", NIGHT_A_RULE=",".join(f"{m:08x}:{v}" for m, v in new.RULE_A),
                          NIGHT_NO_B="1", NIGHT_CONV="filed", NIGHT_SUB="0:0", NIGHT_A_LIST="0")
        night = load(PKG.parent / "night" / "cheaper" / "night_batch4.py", "night_batch4")
    except (Exception, SystemExit) as error:
        print("  research program night_batch4.py not usable:", repr(error))
    if night is not None:
        total, same, counts = 300, 0, set()
        for _ in range(total):
            nine = [rng.getrandbits(32) for _ in range(9)]
            alpha, j = rng.getrandbits(32), rng.randrange(new.BATCHES)
            X, S, w = new.context(nine)
            nm, rm = new.Machine(), night.Machine2()
            mine = new.packed_batch(nm, new.batch_constants(X, S, w, alpha)[0], j)
            words, flags, taken, flags_a, taken_a, _, _ = night.batch(rm, night.constants(X, S, w, alpha)[0], j)
            same += (mine == (words, flags, taken, flags_a, taken_a) and night.list_words(j)[2] == new.list_words(j)[1]
                     and night.hs.context(nine) == (X, S, w))
            parts = list(rm.ops)
            a_parts = [p for p in parts if not p.startswith("stage B") and not p.startswith("stage C")]
            b_parts = [p for p in parts if p not in a_parts]
            counts.add((sum(rm.ops[p] for p in a_parts), sum(rm.loads[p] for p in a_parts),
                        sum(rm.ops[p] for p in b_parts), sum(rm.loads[p] for p in b_parts)))
        need(same == total, f"stage-2 words, both sets of flags and both branches equal those of night_batch4.py in {same} of {total} batches")
        need(counts == {(data.STAGE_A_OPS, data.STAGE_A_LOADS, data.STAGE_2_OPS - 3, data.STAGE_2_LOADS - 1)},
             f"its counts are those of this package without the count of the stage-2 entry (3 operations, 1 load): {sorted(counts)}")
    # (b) the reference values of the program against the forward compression of check_pkg5.py
    chk = load(PKG / "check_pkg5.py", "check_pkg5")
    M, ror, rol = chk.M32, chk.ror, chk.rol
    total, good, zero, passing = 3000, 0, 0, 0
    for _ in range(total):
        nine = [rng.getrandbits(32) for _ in range(9)]
        alpha, y4 = rng.getrandbits(32), new.class_member(rng.randrange(new.CLASS_SIZE))
        X, S, w = new.context(nine)
        A, B = new.messages(new.trial(X, S, w, alpha, y4)[0])
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
        r = new.reference(X, S, w, alpha, y4)
        good += (r["y4"] == Ya[4] == y4 and r["h1"] == h1 and r["word"] == n == (da[3] ^ db[3]) ^ rol(da[6] ^ db[6], 8)
                 and r["word_from_digests"] == n and r["half"] == 1 and new.rule_a(h1) == data.rule_a(h1))
        zero += n == 0
        passing += data.rule_a(h1)
    need(good == total, f"reference values of the program (Y4, h1, the word of Lemma N, the word from the digests) equal those from "
                        f"check_pkg5's forward compression of both messages in {good} of {total} trials (zero words: {zero}; "
                        f"trials that satisfy rule A: {passing})")
    # (c) one complete class loop
    X, S, w = new.context([rng.getrandbits(32) for _ in range(9)])
    alpha = rng.getrandbits(32)
    right, shapes, seen, entered, passing = 0, set(), set(), 0, 0
    start = time.time()
    for j in range(new.BATCHES):
        r = new.batch_check(X, S, w, alpha, j)
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
          f"{1 / 2 ** data.STAGE_2_LOG2_SHARE:.3f}); lanes that satisfy rule A: {passing} of {7 * new.BATCHES}")


def step_tools():
    print("3. tools/fmt_pkg5.py (nothing written)")
    done = subprocess.run([sys.executable, "-B", str(TOOLS / "fmt_pkg5.py")], capture_output=True)
    for line in done.stdout.decode("utf-8", "replace").splitlines():
        if line.startswith(("   lines over", "proof line count", "H1-", "H2-", "H3-", "claim.json proof ranges", "  note bytes", "  claim:",
                            "rendered files", "  DRIFT", "RESULT", "  main term", "  factor", "  class eta", "  per alpha")) or ": proof:" in line:
            print("  " + line[:230])
    need(done.returncode == 0, "fmt_pkg5.py exit status 0")
    print("4. check_pkg5.py")
    start = time.time()
    done = subprocess.run([sys.executable, "-B", str(PKG / "check_pkg5.py")], capture_output=True)
    lines = done.stdout.decode("utf-8", "replace").splitlines()
    oks = sum("[ok]" in line for line in lines)
    for line in lines:
        if "[ok]" not in line and not line.startswith(("      words of A", "      digest xor", "    first trial", "      changed words")):
            print("  " + line[:230])
    print(f"  lines marked ok: {oks}; exit status {done.returncode}; {time.time() - start:.0f} s")
    need(done.returncode == 0 and any(line.startswith("RESULT: all checks passed") for line in lines), "check_pkg5.py: all checks passed")
    print("5. tools/text_scan_pkg5.py")
    done = subprocess.run([sys.executable, "-B", str(TOOLS / "text_scan_pkg5.py")], capture_output=True)
    for line in done.stdout.decode("utf-8", "replace").splitlines():
        print("  " + line[:230])
    need(done.returncode == 0, "text scan: nothing found")


def main():
    step_selftest()
    step_cross()
    step_tools()
    print("RESULT:", "all steps hold" if not FAILED else "FAILED: " + "; ".join(FAILED))
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
