# Merge of the three fixes into research\pkg10\pkg, in this order

T = `python ./research/pkg10/tools_integrate.py`

1. **Program (fixA).** Copy `fixA\halfsearch.py` over `pkg\blake3-r2\experiments\halfsearch.py`. Read
   `fixA\NUMBERS.md`: CHARGE (upper bound per trial-equivalent), the three budget constants and names, self-tests.
2. **Text edits (fixC).** `T edits fixC\EDITS.md proof` then `T edits fixC\EDITS.md claim` (pairs are split by
   file if fixC marks them; otherwise apply the file's pairs per target). Stops on any pair not found exactly once.
3. **Heuristics (fixC).** `T heur fixC\HEURISTICS.json` (H4-cluster-yield, H5-cluster-mass, H6-neighbour-budgets).
4. **Preprocessing (fixB).** `T splice "## 9. " "## 10. " fixB\SECTION9.md`; apply `fixB\FIELD.md` to the
   preprocessing bullet of "Field meanings"; apply `fixB\CLAIM.md` pairs to claim.json; set
   `claim.preprocessing_log2` = P.
5. **Section 8.** `python fill_total.py CHARGE P` (writes sec8_total_filled.md and sec8_preproc_filled.md), then
   `T splice "- **Preprocessing.**" "Total:" sec8_preproc_filled.md` and
   `T splice "Total:" "## 9. " sec8_total_filled.md`. Replace the ledger rows "budgeted, per
   representative 67.225", "budgeted, per trial-equivalent 1.6389", "charged ... 1.71" and the sentence "The
   charge is 4.3 per cent above the budget" by fixA's derivation.
6. **Numbers.** `T nums 1.71=CHARGE 92.58=TIME` where only charge and total are meant (checked against the
   classification: proof 35, 1309, 1354, 1374-75, 2102-03, 2408; claim line 20; note 94, 106, 125, 137 for the
   charge; proof 41, 1310, 1423, 1429, 2200, 2289, 2302, 2410, 2417, claim line 9, note 1, 115-16, 125, 339 for
   the total). If P >= 86, recompute the no-cluster scalars 95.8 / 95.0 / 94.8 and claim line 20's 96.0 with the
   same total formula. Fill the note's `[CHARGE]`.
7. **Sweep.** No sentence may still say the program "does not contain the neighbour path", the charge is a "lower
   bound", the routing is "not counted", success holds under "H1, H2 and H3", the selection is an "estimate", or
   tell a reviewer what to test; J has one definition. Grep for each.
8. **Line references.** `T repoint` (all six heuristics from section anchors).
9. **Stage and validate.** `wsl -d Ubuntu -- bash .../pkg10/pkg/tools/stage_pkg10.sh` (writes VERIFIED.sha256),
   then `.../tools/validate_pkg7_fix.sh` (organizer validation in its own mirror). Both experiments 256/256.
10. **Owner's go**, then `.../tools/submit_pkg10.sh`.
