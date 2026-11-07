#!/usr/bin/env python3
"""pairs_pf.py - descriptive listing of the pairs of deep hits (E1L, E3P) inside one frame (block), per arm, from the
main/*.hits files: within one outer step, same c1 in different outer steps (and whether K_O(g) = Y1 + w12 is equal,
the K-collision of Lemma AK that makes the E1 sides identical), different c1 in different outer steps.
python3 -B pairs_pf.py <run_dir> <out.json>"""
import glob
import json
import os
import struct
import sys
from collections import defaultdict


def main():
    run_dir, outp = sys.argv[1], sys.argv[2]
    hits = []
    for f in sorted(glob.glob(os.path.join(run_dir, "s*_a*_g*.hits"))):
        b = open(f, "rb").read()
        n = struct.unpack("<I", b[:4])[0]
        hits += [struct.unpack("<16I", b[4 + 64 * i:4 + 64 * i + 64]) for i in range(n)]
    out = {}
    for name, bit in (("E1L", 2), ("E3P", 4)):
        for arm in (0, 1):
            by = defaultdict(list)
            for h in hits:
                if h[0] == arm and h[7] & bit:
                    by[(h[1], h[2])].append(h)
            c = {"hits": sum(len(v) for v in by.values()), "within": 0, "same_c1": 0, "same_c1_same_K": 0,
                 "diff_c1": 0, "same_c1_examples": []}
            for v in by.values():
                for i in range(len(v)):
                    for j in range(i + 1, len(v)):
                        a, b = v[i], v[j]
                        if a[3] == b[3]:
                            c["within"] += 1
                        elif a[5] == b[5]:
                            c["same_c1"] += 1
                            c["same_c1_same_K"] += int(a[15] == b[15])
                            if len(c["same_c1_examples"]) < 10:
                                c["same_c1_examples"].append({"gen": a[1], "block": a[2], "steps": [a[3], b[3]],
                                                              "c1": "%08x" % a[6], "K": ["%08x" % a[15], "%08x" % b[15]],
                                                              "tau": ["%08x" % a[8], "%08x" % b[8]]})
                        else:
                            c["diff_c1"] += 1
            out["%s_arm%d" % (name, arm)] = c
    json.dump(out, open(outp, "w"), indent=1)
    print(json.dumps({k: {q: v[q] for q in v if q != "same_c1_examples"} for k, v in out.items()}))


if __name__ == "__main__":
    main()
