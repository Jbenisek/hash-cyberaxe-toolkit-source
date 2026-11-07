#!/usr/bin/env python3
"""Seconds and output bytes of the two experiments for 256 seeds, on this host (the organizer's limits: 20 s, 2 MiB, 64 KiB of source).

    python -B work/tools/time_experiments.py      writes work/evidence/time_experiments.txt

The requests are those of work/tools/check_program.py. Research helper, not submitted.
"""
import hashlib
import json
import subprocess
import sys
import time

from common import PROGRAM, WORK, sha, write


def main():
    manifest = json.loads((WORK.parent / "blake3-r2" / "experiments" / "manifest.json").read_text())
    out = [f"PROGRAM sha256 {sha()}; python -B work/tools/time_experiments.py; source {len(PROGRAM.read_bytes())} bytes of 65536 allowed"]
    for entry in manifest["experiments"]:
        name = entry["id"]
        request = {"schema_version": 1, "experiment_id": name, "target_profile": "blake3-r2-prefix-v1", "event": entry["event"],
                   "max_message_bytes": 4096,
                   "trials": [{"trial": i, "seed": hashlib.sha256(b"pkg7-host-%s-%d" % (name.encode(), i)).hexdigest()} for i in range(256)]}
        payload = json.dumps(request, sort_keys=True, separators=(",", ":")).encode() + b"\n"
        start = time.time()
        done = subprocess.run([sys.executable, "-B", "-s", str(PROGRAM)], input=payload, capture_output=True, check=True)
        out.append(f"{name}: 256 seeds, {time.time() - start:.1f} s (limit 20 s in the organizer's container, one processor), "
                   f"{len(done.stdout)} bytes of output (limit 2097152)")
    print(write("time_experiments.txt", out), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
