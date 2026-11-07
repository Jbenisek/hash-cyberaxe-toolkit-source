"""Move every figure that depends on the charge and the total: charge 1.71 -> 1.65, total 92.58 -> 92.53, uniform-rate
total 2^119.038 / 119.1 -> 2^118.986 / 119.0, and reword the sentences that described the old budgeted charge.
Exact-once (or exact-count) replacements; stops before writing if any does not match."""

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

import json, sys
K = _hca_public_path_text('__HCA_WORKSPACE__/research/pkg10/pkg/')
FILES = {"proof": K + "blake3-r2/proof.md", "claim": K + "blake3-r2/claim.json", "note": K + "submission-note-r2.md"}
# (file, old, new, expected count)
R = [
 ("proof", "1.71 primitive operations, memory loads and stores included.", "1.65 primitive operations, memory loads and stores included.", 1),
 ("proof", "below 2^92.58 target-compression units, so the claimed scalar is 92.58.", "below 2^92.53 target-compression units, so the claimed scalar is 92.53.", 1),
 ("proof", "and, at the same 1.71 operations per trial, the total of Section 8 is below\n2^(119.038 - log2 f): below 2^92.58 at the assumed factor, and below 2^119.038",
           "and, at the same 1.65 operations per trial, the total of Section 8 is below\n2^(118.986 - log2 f): below 2^92.53 at the assumed factor, and below 2^118.986", 1),
 ("proof", "stage, an expectation against a looser machine. Section 8 charges **1.71**, 4.3\nper cent above the budgeted 1.6389 of this package's own ledger with the budget\nfactor 1.2: ABOVE both audits at the measured rates and below the 2.1798 and\n2.1870 they reach when the share of open gates is charged at 1.72 times its mean.",
           "stage, an expectation against a looser machine. Section 8 charges **1.65**, an\nupper bound with the routing included and the neighbour path capped by its\nbudgets at 1.2 times the measured means: ABOVE both audits at the measured\nrates. Charging the share of open gates at 1.72 times its mean, as the audits'\nstricter readings do, is not possible: the run halts at the budget (H6).", 1),
 ("proof", "- The neighbour-path budget, 1.2 times the measured shares, is no more proved\n  than step 4's; the largest X2 value of a sample grows with it (1.64 times the\n  mean over 8,192 values, 1.72 over 16,384); charging it gives 92.93 and 93.24,\n  not 92.58.",
           "- The neighbour budgets, 1.2 times the measured shares, are halts: a run whose\n  shares exceed them stops with failure, which costs success and not time. The\n  largest share of one value of X2 grows with the sample (1.64 times the mean\n  over 8,192 values, 1.72 over 16,384); H6 assumes that the average over a run\n  stays below the budgets.", 1),
 ("proof", "- time_log2 = 92.58 bounds total charged time by 2^92.58 units.", "- time_log2 = 92.53 bounds total charged time by 2^92.53 units.", 1),
 ("proof", "baseline or security bound; 92.58 is below it.", "baseline or security bound; 92.53 is below it.", 1),
 ("proof", "| charged | 19.1 per trial | 1.71 per equivalent |", "| charged | 19.1 per trial | 1.65 per equivalent |", 1),
 ("proof", "| time_log2 | 97.6 | 92.58 |", "| time_log2 | 97.6 | 92.53 |", 1),
 ("proof", "67.225 units per representative", "67.585 units per representative", 1),
 ("proof", "The bound 2^92.58 is 4.95 below the bound\n2^97.52 of entry c66f230d in the exponent: 1.47 from the larger assumed factor,\nof which 0.91 is the margin of 2.00 in place of 3.75, and 3.48 from the lower",
           "The bound 2^92.53 is 5.00 below the bound\n2^97.52 of entry c66f230d in the exponent: 1.47 from the larger assumed factor,\nof which 0.91 is the margin of 2.00 in place of 3.75, and 3.53 from the lower", 1),
 ("claim", '"time_log2": 92.58,', '"time_log2": 92.53,', 1),
 ("claim", "With stage 2 counted for one batch in 32 and with the middle step, the table build and the outer step, a trial is charged 1.71 operations.",
           "With the neighbour path of proof.md 6.7 capped by its budgets, the routing between pieces stored and loaded, stage 2 counted for at most E representative words and S neighbour words, and the middle steps, the table build and the outer step, a trial-equivalent is charged 1.65 operations, an upper bound.", 1),
 ("note", "time_log2 = 92.58", "time_log2 = 92.53", 1),
 ("note", "1.71 for 41.02 of them per representative", "1.65 for 41.02 of them per representative", 1),
 ("note", "trial-equivalent is charged 1.71 operations (budgeted 1.6389), which is 67.225\nunits per representative divided by 41.02 trial-equivalents;",
          "trial-equivalent is charged 1.65 operations, an upper bound, which is 67.585\nunits per representative divided by 41.02 trial-equivalents;", 1),
 ("note", "The total is below 2^92.58 and the\nclaim is 92.58.", "The total is below 2^92.53 and the\nclaim is 92.53.", 1),
 ("note", "| 47, 135 | 1.71 | 92.58 |", "| 47, 135 | 1.65 | 92.53 |", 1),
 ("note", "The 1.71 charged here is\nabove both of them, because it budgets the neighbour path at 1.2 times the\nmeasured shares. Charging instead the largest share of one value of X2 that any\nsample showed gives 2.19 to 2.54 and claims of 93.83 to 94.14.",
          "The 1.65 charged here is\nabove both of them: it is an upper bound with the routing included and the\nneighbour path capped by budgets of 1.2 times the measured shares, at which the\nrun halts, so a larger share costs success and not time."),
 ("note", "[CHARGE]", "1.65", 1),
 ("note", "The claim 92.58 is a cost bound", "The claim 92.53 is a cost bound", 1),
]
txt = {k: open(v, encoding="utf-8", newline="\n").read() for k, v in FILES.items()}
bad = []
for r in R:
    f, a, b = r[0], r[1], r[2]; n = r[3] if len(r) > 3 else 1
    if txt[f].count(a) != n: bad.append(f"{f} x{txt[f].count(a)} (want {n}): {a[:80]!r}")
if bad:
    print("STOP:"); print("\n".join(bad)); sys.exit(1)
for r in R:
    txt[r[0]] = txt[r[0]].replace(r[1], r[2])
# the uniform-rate claim, wherever it is stated
for k in txt:
    txt[k] = txt[k].replace("time_log2 119.1", "time_log2 119.0").replace("time_log2 = 119.1", "time_log2 = 119.0").replace("would claim 119.1", "would claim 119.0").replace("submit 119.1", "submit 119.0")
json.loads(txt["claim"])
for k, v in FILES.items():
    open(v, "w", encoding="utf-8", newline="\n").write(txt[k])
print(f"{len(R)} replacements applied; 119.1 -> 119.0 where stated; claim.json parses")
