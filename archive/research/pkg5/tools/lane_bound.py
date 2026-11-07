#!/usr/bin/env python3
"""Largest lane value of every SUM of the two-stage batch, per part, against the bounds quoted in pkg5 proof 6.5.

A second look at what the in-package self-test reports, with the machine of the research program in which the
two-stage batch was first written (research/night/cheaper/night_batch4.py) instead of the package's own. That
program reads the filed package's halfsearch.py and replaces its constants in memory; its pin, eta and rule A
are set here from this package's program through the environment. No file is written.

    python -B tools/lane_bound.py [batches, default 2000]
"""
import importlib.util
import os
import random
import sys
from pathlib import Path

sys.dont_write_bytecode = True
TOOLS = Path(__file__).resolve().parent
PKG = TOOLS.parent


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


new = load(PKG / "blake3-r2" / "experiments" / "halfsearch.py", "halfsearch_pkg5")
os.environ.update(NIGHT_PIN=",".join(f"{getattr(new, k):08x}" for k in ("X3", "X7", "X11", "X15", "W4", "W13")),
                  NIGHT_ETA=f"{new.ETA:08x}", NIGHT_A_RULE=",".join(f"{m:08x}:{v}" for m, v in new.RULE_A),
                  NIGHT_NO_B="1", NIGHT_CONV="filed", NIGHT_SUB="0:0", NIGHT_A_LIST="0")
night = load(PKG.parent / "night" / "cheaper" / "night_batch4.py", "night_batch4")

B = 1 << 32
# the parts of that program and the bound that proof 6.5 quotes for the sums of the same assignments (units of 2^32)
QUOTED = {"C0 backwards": 2, "K3": 6, "C2 to z": 8, "stage-A test": 2, "stage B: rest of C2": 3, "stage B: D1": 2,
          "stage B: C1": 6, "stage B: E1 to c1": 10, "stage B: test": 10, "stage C: rest of E1": 10,
          "stage C: E1-only test": 2}


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
    rng = random.Random(7)
    sums, same = {}, 0
    for i in range(n):
        nine = [rng.getrandbits(32) for _ in range(9)]
        if i % 4 == 0:                      # extreme words now and then
            nine = [rng.choice((0, new.MASK, rng.getrandbits(32))) for _ in range(9)]
        X, S, w = new.context(nine)
        alpha = rng.choice((0, new.MASK, rng.getrandbits(32)))
        j = rng.randrange(new.BATCHES)
        m = night.Machine2()
        words, flags, taken, flags_a, taken_a, _, _ = night.batch(m, night.constants(X, S, w, alpha)[0], j)
        mine = new.packed_batch(new.Machine(), new.batch_constants(X, S, w, alpha)[0], j)
        same += mine == (words, flags, taken, flags_a, taken_a)
        for part, top in m.sums.items():
            sums[part] = max(sums.get(part, 0), top)
    print(f"class eta {new.ETA:08x}: {same} of {n} batches with the same words, flags and branches in both programs")
    ok = same == n
    for part, v in sums.items():
        q = QUOTED.get(part)
        if not v:
            continue
        line = f"  {part:24s} largest sum {v / B:6.3f} * 2^32"
        if q is not None:
            line += f"   quoted bound {q} * 2^32   {'ok' if v < q * B else 'EXCEEDED'}"
            ok &= v < q * B
        print(line)
    print("largest lane value of a sum:", f"{max(sums.values()) / B:.3f} * 2^32 (limit 16 * 2^32)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
