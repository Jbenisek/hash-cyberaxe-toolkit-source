#!/usr/bin/env python3
"""The self-test of the program with many cases, once for every rule given (4, 5 or 6 conditions), one process per rule.

    python -B work/tools/selftest_big.py N seed rule [rule ...]

The same as work/selftest_big.sh (the copy of the script of the package before this one), written for the Python of
the host so that it does not depend on the WSL processors. The program has one line RULE_CONDITIONS = n. For every
rule the program is copied to work/selftest_tmp with that one line set to the rule (for the rule that the program
has, the copy is the program, byte for byte) and the copy runs N cases for the seed text:

    python -B -s <copy> --selftest N seed

Each run prints the program's one JSON line, kept as work/evidence/selftest_<N>_rule<n>_<seed>.json after one line
with: the SHA-256 of the program, the rule of the run, the rule of the program, the SHA-256 of the copy that ran,
the exit status and the seconds. A file is evidence for the program only while the program still has the first
SHA-256 of that line. CPU only, one thread per rule. Research helper, not submitted.
"""
import hashlib
import re
import subprocess
import sys
import time

from common import EVIDENCE, PROGRAM, WORK


def main():
    n, seed, rules = sys.argv[1], sys.argv[2], sys.argv[3:]
    source = PROGRAM.read_bytes()
    digest = hashlib.sha256(source).hexdigest()
    default = re.search(rb"^RULE_CONDITIONS = (\d+)$", source, re.M).group(1).decode()
    tmp = WORK / "selftest_tmp"
    tmp.mkdir(exist_ok=True)
    runs = []
    for rule in rules:
        copy, count = re.subn(rb"^RULE_CONDITIONS = .*$", b"RULE_CONDITIONS = " + rule.encode(), source, flags=re.M)
        if count != 1 or (rule == default) != (copy == source):
            raise SystemExit(f"rule {rule}: the line RULE_CONDITIONS was not found once")
        path = tmp / f"halfsearch_{digest}_rule{rule}.py"
        path.write_bytes(copy)
        out = open(tmp / f"selftest_{n}_rule{rule}_{seed}.out", "wb")
        err = open(tmp / f"selftest_{n}_rule{rule}_{seed}.err", "wb")
        process = subprocess.Popen([sys.executable, "-B", "-s", str(path), "--selftest", n, seed],
                                   stdin=subprocess.DEVNULL, stdout=out, stderr=err)
        runs.append((rule, hashlib.sha256(copy).hexdigest(), process, time.time(), out, err))
    for rule, copy_digest, process, start, out, err in runs:
        status = process.wait()
        seconds = int(time.time() - start)
        out.close()
        err.close()
        body = (tmp / f"selftest_{n}_rule{rule}_{seed}.out").read_bytes().replace(b"\r\n", b"\n")
        head = f"PROGRAM sha256 {digest} RULE_CONDITIONS {rule} (program: {default}) copy sha256 {copy_digest} exit {status} seconds {seconds}\n"
        (EVIDENCE / f"selftest_{n}_rule{rule}_{seed}.json").write_bytes(head.encode("ascii") + body)
        print(head[:230], end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
