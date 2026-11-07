"""Emit reach.csv: for each SHA3 technique on our grid, works? and cost at r=3,4,5,6,7.
Low-degree (FES) rows are COMPUTED exactly by ledger_by_round (D19-style). Other techniques are
DERIVED/cited from SHA3R6_MAP.md sections 3-4 (which summarizes job55, linstruct, shake, isd).
Cost unit per task: r5 in /1355, r6 in /1626 (tracks exist); r3,r4,r7 in word operations (log2 N).
We also tag each low-degree cost with the natural-unit (271*r = one r-round permutation) score for comparison.
"""

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

import csv, importlib.util, sys
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/newpaths/untried/s3-reach-by-round'))
import ledger_by_round as L

rows = []
# --- low degree on W40 (FES), COMPUTED exact ---
for r in (3, 4, 5, 6, 7):
    D, Nv = L.ledger(r)
    Cr = 271 * r
    lw = L.log2_floor_frac(Nv, 1)       # word-ops log2
    lu = L.log2_floor_frac(Nv, Cr)      # natural-unit log2 (one r-round perm)
    if r in (5, 6):
        cost = f"{lu:.5f} (log2 units /{Cr})"
    else:
        cost = f"{lw:.5f} (log2 word-ops; /{Cr} = {lu:.5f} u)"
    works = "yes" if r <= 6 else "yes-but-not-best-depth"
    note = {3: "affine f_t; birthday-level", 4: "birthday-level", 5: "birthday-level",
            6: "beats board 124.04565 by 0.863",
            7: "setup 2^136 (deg-16 init=3^40 naive / P_16~2^37 Moebius); beats generic ~128 but 2.7b worse than r6; no r7 track"}[r]
    rows.append(("low-degree-W40-FES", r, works, cost, "COMPUTED (ledger_by_round.py)",
                 f"D19 generalized; {note}"))

# --- other techniques, DERIVED/cited from SHA3R6_MAP.md sec 3-4 ---
other = [
 # technique, round, works, cost, label, source
 ("2-round-linear-structure", 5, "yes", "~128 (birthday w/ cheap step; not separately priced r5)", "GUESS", "MAP 3.4 (SOLCLOUD_16)"),
 ("2-round-linear-structure", 6, "yes", "132.0744 (log2 units /1626; standalone) / +0.013 as leader patch", "DERIVED", "MAP 3.4; D15 sec8"),
 ("2-round-linear-structure", 7, "yes", "~128 birthday-level (parent of FES; superseded)", "GUESS", "MAP 3.4"),

 ("3-round-structure", 3, "no", "rank<=2: no family through chi3 (obstruction theta3)", "DERIVED", "MAP 3.5/3.7 (linstruct3)"),
 ("3-round-structure", 4, "no", "n/a (fails already at round 3)", "DERIVED", "MAP 3.5"),
 ("3-round-structure", 5, "no", "n/a; best-case saving <=0.18 bit, likely 0", "DERIVED", "MAP 3.5"),
 ("3-round-structure", 6, "no", "n/a; <=0.18 bit if rank-2 realizable (it is not a family)", "DERIVED", "MAP 3.5"),

 ("internal-differential", 3, "yes", "<=2^105 (fewer rounds; not separately computed)", "GUESS", "MAP 3.1 (<= r5 line)"),
 ("internal-differential", 4, "yes", "<=2^105 (not separately computed)", "GUESS", "MAP 3.1"),
 ("internal-differential", 5, "yes", "2^105 perms (= ~105 log2 units /1355); SUB-BIRTHDAY", "DERIVED", "MAP 3.1 (ZHL2023 period-32)"),
 ("internal-differential", 6, "no", "2^172 perms (169.5 best branch); 67 bits worse than r5", "DERIVED", "MAP 3.1/3.2"),
 ("internal-differential", 7, "no", "n/a; worse than r6", "DERIVED", "MAP 3.1"),

 ("connector+trail", 6, "no", "2^206 (2^197 early-abort); 2-rd connector short >=33 DF; floors ~2^132", "DERIVED", "MAP 3.3 (GLST/shake)"),
 ("connector+trail", 5, "open", "not computed for SHA3-256 r5 (designed for 6-rd SHAKE)", "GUESS", "MAP 3.3"),

 ("generic-birthday", 3, "yes", "~128 units (2^128 r-round perms + overhead)", "DERIVED", "RULES.md cost model"),
 ("generic-birthday", 4, "yes", "~128 units", "DERIVED", "RULES.md"),
 ("generic-birthday", 5, "yes", "~128 units /1355", "DERIVED", "RULES.md"),
 ("generic-birthday", 6, "yes", "124.04565 board best (cheap-step birthday); 124.27 promoted", "DERIVED", "RULES.md board"),
 ("generic-birthday", 7, "yes", "~128 units", "DERIVED", "RULES.md"),
]
rows += other

out = _hca_public_path_text('__HCA_WORKSPACE__/research/newpaths/untried/s3-reach-by-round/reach.csv')
with open(out, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(["technique", "round", "works", "cost", "label", "source"])
    w.writerows(rows)
print(f"wrote {len(rows)} rows to reach.csv")
for row in rows:
    print(row)
