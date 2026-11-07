# Stage 1 questions walk — Poseidon algebraic rows

Status: **DERIVED** from the current Poseidon row, `GRID_POSEIDON.md`, `LENSES.md`, `flagdrop.md`, `proof_vs_code.md`, and `open_cells.md`. One line per Stage 1 question; each line ends in a concrete number, file, or action.

1. **New path or re-pricing?** The univariate line + powering + half-gcd is an existing path; this queue is a re-pricing/correctness audit, not a new attack. **Action:** fold the result into the next Poseidon row only after the wrap path is repaired; evidence `research/luna_scout/flagdrop.md`.
2. **Home run / leap?** A real leap would require a product family giving independent lists, not another line constant; the toy Wagner separability test found 513/65,536 mixed differences zero, not an identity. **Number/action:** no filing-grade leap; keep the product-family cell open in `research/luna_scout/open_cells.md`.
3. **Missing sphere/lenses?** The three previously empty algebraic cells (interpolation, one-S-box G&D, Wagner) are now recorded; remaining candidate lenses are listed in `research/LENSES.md` (N02/N08/N09/N10). **File/action:** update the Poseidon grid from `open_cells.md`, do not claim an unrun lens.
4. **Transfer from another hash?** No SHA-3/BLAKE3/SHA-256 transfer preserves the required independent decomposition; the only transferable lesson is to charge every output and memory edge. **File/action:** use the generic transfer rule in `open_cells.md`; no new cross-hash number.
5. **Dismissed by argument?** A bounded control was run: p=65,537, t=3, 65,537 inputs, 0.41 s wall, 30,776 kB peak; the G&D and mixed-difference results are in `toy_open_cells.out`. **Number/action:** keep the result as a measured check, not a proof of a deployed-row speedup.
6. **Dense boring details?** The audit found a concrete copied-detail defect: wrap-enabled qg on the non-b path lacks the high-tail add-back. **Number:** r21 missing charge `22,624,338,332,797,127,698` operations per affected qg product; file `flagdrop.md`.
7. **Do printed conditions hold on the witness?** The prose says T1 is held through cyclic qg, but c frees it at source line 939 and no c/a add-back is charged. **Action:** mark the filed r21 wrap-enabled claim as pending repair; mapping `proof_vs_code.md`.
8. **Mill tailings?** No old Poseidon kill was re-priced in this pass; the three open cells were checked instead. **Action:** queue any old-kill repricing separately; do not reuse a kill argument.
9. **Trash / discarded pairs?** No discarded collision corpus was available in the specified inputs, so no bias estimate is claimed. **Action:** mine a controlled discard file only if one is supplied.
10. **Archive/pre-contest research?** The relevant archive/grid/lens records were read: `GRID_POSEIDON.md` Part 4 and `LENSES.md`; no older result superseded the three open cells. **File/action:** retain those paths as dependencies of this scout report.
11. **Is a 2^-k filter really a match?** No: the toy mixed-difference test rejects an independent `F(a+b)=u(a)+v(b)` split, and the MDS couples lanes after each partial round. **Number/action:** no birthday-list price is justified; keep the current line/root route as the control.

Label check: the toy counts cited above are **COMPUTED** in open_cells.md and toy_open_cells.out; the actions and cross-file judgments here are **DERIVED**.

