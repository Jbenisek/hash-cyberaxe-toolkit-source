"""Bring restrictions[3] and [5] of claim.json under the organizer's 1,024-character limit, and correct their content
to the merged program (E on representative words, cluster lists, memory 2^26)."""

# Publication path adapter: resolve data paths from the extracted source tree.
def _hca_public_path_text(value):
    if "__HCA_WORKSPACE__/" not in value:
        return value
    import os as _hca_os
    from pathlib import Path as _hca_Path
    root = _hca_os.environ.get("HASHCYBERAXE_WORKSPACE")
    if root is None:
        here = _hca_Path(__file__).resolve().parent
        root = next((str(p) for p in (here, *here.parents) if (p / "research").is_dir()), None)
    if root is None:
        raise FileNotFoundError("Extract the research source tree, or set HASHCYBERAXE_WORKSPACE to its archive directory.")
    return value.replace("__HCA_WORKSPACE__/", str(_hca_Path(root).resolve()).replace("\\", "/") + "/")

import json
P = _hca_public_path_text('__HCA_WORKSPACE__/research/pkg10/pkg/blake3-r2/claim.json')
c = json.load(open(P, encoding="utf-8"))
r3 = ("Classical 256-bit word RAM under collision-frontier-v5; seven trials per 256-bit word in 36-bit lanes on a "
      "16-register load/store machine on which every memory word costs one load each time it is fetched, except nine "
      "words kept in registers during a loop. A word runs stage A, 37 operations plus 10 loads; only a word in which a "
      "trial passes rule A runs stage 2, 105 plus 30. With the neighbour path of proof.md 6.7, the routing between "
      "pieces stored and loaded, and the middle steps, the table build and the outer step, a trial-equivalent is "
      "charged 1.65 operations, an upper bound. No sorting, no lookup by value and no table that grows with the "
      "number of trials. The algorithm halts with failure when E representative words (one in 32) or S neighbour "
      "words have run stage 2, when G representatives have opened their gate, when W neighbour words have run stage "
      "A, or when 2^84 trials that passed the second test have been processed (proof.md 6.4, step 4).")
r5 = ("Six 32-bit constants, the word eta, two bits of the sub-class and three 32-bit constants of the rule test are "
      "stored in the program (48 bytes of advice). The constants were found by a participant's solver search and "
      "chosen by a participant's count; the sub-class and rule A were proposed by another AI model (GPT Sol 6.1) from "
      "exact counts that the participant's counter reproduces. preprocessing_log2 80 bounds the selection procedure "
      "of proof.md Section 9: every search runs over a stated range and every program run halts at a stated cap, so "
      "its cost, fewer than 2^88.45 operations, is a bound by construction whatever the programs return. That it "
      "returns the stored constants rests on the participant's solver log and counts; its steps for the sub-class, "
      "the rule and the flips have not been run. Choosing a sub-class from the rate of every member follows winglock "
      "(2125212, 2bb5d604). memory_log2_bytes 35 bounds that procedure and the search (below 2^26 bytes). No "
      "priority or novelty claim is made.")
assert len(r3) <= 1024 and len(r5) <= 1024, (len(r3), len(r5))
c["restrictions"][3], c["restrictions"][5] = r3, r5
over = [(i, len(r)) for i, r in enumerate(c["restrictions"]) if len(r) > 1024]
open(P, "w", encoding="utf-8", newline="\n").write(json.dumps(c, indent=2, ensure_ascii=False) + "\n")
print("restrictions[3]", len(r3), "chars; restrictions[5]", len(r5), "chars; any still over 1024:", over)
# every other string field of the claim, for the same limit
long = []
def walk(o, path="$"):
    if isinstance(o, dict):
        for k, v in o.items(): walk(v, f"{path}.{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o): walk(v, f"{path}[{i}]")
    elif isinstance(o, str) and len(o) > 1024:
        long.append((path, len(o)))
walk(c)
print("string fields over 1024 anywhere in claim.json:", long)
