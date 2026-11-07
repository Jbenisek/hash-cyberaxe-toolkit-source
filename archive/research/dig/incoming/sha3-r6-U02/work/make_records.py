
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
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/dig'))
import add_cell
W = "research/dig/incoming/sha3-r6-U02/work/"
def ev(*f): return "; ".join(W + x for x in f)
base = dict(hash="sha3-r6", row_i=None, row_j=None, source="our workflow: scan-once", own_test=True,
            date="2026-10-12", lever=False, gain_bits=None)
recs = {}
recs["sha3-r6_round1.chi_chi_Q1"] = dict(base,
 object="round-2 chi (0-indexed round1) on the leader route: z-flip footprint and prefix conditions (5886ca76 / def724e5 structure, lanes 4+14 carry z)",
 question="Q1 count the rows/conditions the leader's chi2 patch uses: chi1 rows and conditions that keep a z-flip sparse, chi2 rows touched, words patched.",
 labels=["N"], status="COMPUTED",
 number="Prefix (def724e5 Sec 2): 312 independent affine conditions on the 1080 message bits (lane16 msg bytes 56 + L8=0 64 + L5 64 + L15 64 + L12 64; rank 312, 768 free bits). Needed by the z-flips themselves: 128 equations (rank 128; 4 neighbour words x 32 planes: after-theta lanes 5,15 = 0 and lanes 8,23 = all-ones), all implied by the 312. Per z-bit: 2 chi1 rows used (64 distinct rows over 32 bits), chi1 output change 2 bits, theta2 footprint 22 A2 words (identical all-ones in every slice, 32/32 directions), 22 distinct chi2 rows, 0 rows with 2 inputs, chi2 output words changed 66, O2P (chi2 + theta3) words patched 499 (union over 1024 slices; mean 314 changed bits per slice). Reconciliation: the 4867f093 figures (21 rows, one two-input row, 554 words) are reproduced EXACTLY by the aligned lane pair (0,5) instead of (4,14); of all 21 aligned same-column pairs (4,14) has the smallest footprint (499; next 508 for (1,6); max 610).",
 evidence=ev("kk6.py", "t0_validate.py", "t1_q1_chi2.py", "t1_q1_chi2_out.json", "t2_conditions.py", "t2_conditions_out.json", "t6_alt_pairs.py", "t6_alt_pairs_out.json"),
 notes="Universe cell sha3-r6|round1.chi|chi|Q1. Own numpy Keccak: 24 rounds match hashlib sha3_256 (20 msgs) and the 6-round prefix permutation matches the organizer reference (20 msgs); Lemma 1 of the proof reproduced (lanes 5,15 zero, lanes 8,23 all-ones after theta1; padding bits are 57,58,63 of lane 16, the proof's P(16,1..63) reads as plane labels). 499 = Lemma 6 count of the def724e5 proof, reproduced. Counts hold for the rounds 1-3 prefix of the path only. 'Round 1' in the cell id is 0-indexed = the second chi (leader's chi2). Union-over-slices counts are sampled (1024 random prefixes) but equal across all 32 z-bits and equal the proof's symbolic number.",
 topic="sha3-r6 leader route chi2 patch counts")
recs["sha3-r6_round1.chi_chi_Q2"] = dict(base,
 object="necessity of each prefix condition group for the leader's chi2 patch (L5, L15, D3/L12, L8, lane16)",
 question="Q2 drop each condition group in turn: does the z-structure (affine A2, 22-word all-ones footprint, 499-word patch) survive?",
 labels=["K"], status="COMPUTED",
 number="Exact linear algebra: dropping L5, L15 or L8 leaves 32 of the 128 needed equations unimplied, dropping the L12 (D3=all-ones) group leaves 64 unimplied; dropping lane16=0 leaves 0 (that 56-bit group is NOT needed: killed freedom). Measured (512 slices x 32 z-bits, 20 random z-pair second-difference tests each): z-affinity of A2 holds in ALL cases (0/20 fails) because each chi1 row has only one varying input; what breaks is the constant all-ones pattern. Full conditions: footprint 22 words, 22 chi2 rows, uniform, 499 patched words. Drop L16: unchanged (22/22/499). Drop L5: 32 words/32 rows/705 patched, not slice-uniform. Drop L15: 32/32/735. Drop L8: 33/33/692. Drop D3 (L12): 44 words/43 rows/860. Minimum set actually needed: 128 equations (rank 128) vs the 312 imposed, so 184 imposed bits are slack.",
 evidence=ev("t2_conditions.py", "t2_conditions_out.json", "t3_q2_drop.py", "t3_q2_drop_out.json", "t1_q1_chi2.py"),
 notes="Universe cell sha3-r6|round1.chi|chi|Q2. Four condition groups are each necessary for the AND-free all-ones patch (not for correctness: the birthday still works on a looser structure, only the per-step patch gets state-dependent masks, 692-860 words instead of 499, no longer a constant W pattern). The 128-equation minimum is plane-restricted (only the 32 planes a z-bit touches); the leader's lane-wide L5/L15/L8/L12 are a convenient superset. Prefix-of-path result (rounds 1-2 only).",
 topic="sha3-r6 leader route condition necessity")
recs["sha3-r6_round1.chi_chi_Q3"] = dict(base,
 object="log2 freedom left under the leader's prefix conditions at the chi2 patch",
 question="Q3 log2 degrees of freedom (exact GF(2) rank) left after the conditions that make the z-flip sparse.",
 labels=["N"], status="COMPUTED",
 number="1080 message bits - rank 312 = 768 free bits (log2 = 768; free lanes 0,1,2,3,4,6,7,9,10,11,13,14); 32 of them are the z counter (XORed into lane4 and lane14 low 32 bits, column parity cancels), leaving 736 prefix bits; a 2^128 birthday needs 128, slack 640 (608 after z). With only the 128 equations the z-flips need, 952 bits would be free (+184). chi2 itself adds no condition on the free bits: its change is computed from the state (AND-free), so no freedom is spent at chi2.",
 evidence=ev("t2_conditions.py", "t2_conditions_out.json", "kk6.py"),
 notes="Universe cell sha3-r6|round1.chi|chi|Q3. Rank by explicit GF(2) elimination of the 312 condition forms over the 1080 message variables (padding byte 0x86 as constant), consistent with the proof's 768. Freedom is not binding (128 bits needed, 2^768 available), so the slack carries no gain. Prefix-of-path result.",
 topic="sha3-r6 leader route freedom")
recs["sha3-r6_round1.chi_chi_Q4"] = dict(base,
 object="alternatives to the leader's chi2 patch: z-subspaces affine through chi2/chi3, other lane pairs carrying z",
 question="Q4 alternatives: largest subspace of the leader's 32 z-directions affine through chi2 and through chi3 (rank<=2 of linstruct3), and the other aligned lane pairs.",
 labels=["Z"], status="SAMPLED",
 number="Through chi2 (exact, state-independent): 106 of 496 z-coordinate pairs conflict (adjacent in a chi2 row); exact maximum coordinate clique = 9 (j=0,2,...,16); random-greedy general subspaces (2,160 restarts) never beat dimension 9; check: 0.7863 = 390/496 pair-pass at 2 rounds on 512 bases, matches. Through chi3: 0 of 496 coordinate pairs pass on any of 512 bases (max clique 1 on all 512), and 0 of 809,024 (12,641 random z-space pairs x 64 bases) general pairs pass; 95% upper bound on a pass rate 3.7e-6. So the leader's z-space holds no rank-2 3-round structure (linstruct3's rank 2 lives in other directions). All 21 aligned same-column lane pairs are feasible with the same 128-equation recipe (cond rank 128; (11,16) 107), A2 footprint 22, O2P patch 499 for (4,14) vs 508-610 for the others.",
 evidence=ev("t4_chi2_affine.py", "t4_chi2_affine_out.json", "t5_3round.py", "t5_out.txt", "t5b_general_pairs.py", "t5b_out.json", "t6_alt_pairs.py", "t6_alt_pairs_out.json"),
 notes="Universe cell sha3-r6|round1.chi|chi|Q4. Own Keccak (validated). The 9-dim chi2-affine z-subspace is a measured structure, not a priced saving: it would replace the state-dependent patch by fixed NOT patterns for those Gray bits only, and the leader's K=13 views already cheapen low bits (unpriced). Dimension 9 is a lower bound for general subspaces (greedy), exact for coordinate subsets. The 3-round result is for the leader's z-space only, not a proof about all 3-round structures; linstruct3 (research/sha3r6/linstruct3/RESULT.md) is the earlier agent run on other directions and was not re-run.",
 topic="sha3-r6 chi2/chi3 affine alternatives")
recs["sha3-r6_round1.theta_theta_Q4"] = dict(base,
 object="theta2 column-parity kernel membership of the z-space chi1-output differences, all 21 aligned lane pairs",
 question="Q4 theta kernel alternatives: can any z combination (any aligned lane pair) have a chi1-output difference in the theta2 kernel, so theta2 does not spread it?",
 labels=["Z"], status="COMPUTED",
 number="Kernel dimension 0 for all 21 aligned same-column lane pairs (including the leader's (4,14)): the 32 column-parity vectors of the z-bits are linearly independent (rank 32), so the only z-combination in the theta2 kernel is 0. The leader's two flipped bits sit in chi1-output columns 0 and 2 (distinct), spreading to 4 D columns = 22 words.",
 evidence=ev("t7_theta_kernel.py", "t7_theta_kernel_out.json", "t6_alt_pairs.py"),
 notes="Universe cell sha3-r6|round1.theta|theta|Q4. Exact GF(2) nullspace of the 32 parity vectors per pair (flips at the chi1 output position X of each varying input, neighbours at stop values 0 / all-ones). Scope: 2 aligned lanes per z, z in bits 0..31, equal plane offset; three-lane or shifted-z carriers and non-aligned z (theta1 spreading) were not scanned. The earlier double-kernel ISD work (research/sha3r6/isd/RESULT.md) covers general message directions and was not re-run.",
 topic="sha3-r6 theta2 kernel alternatives")
ex = add_cell.load()
for k, r in recs.items():
    fn = f"../{k}.json"
    json.dump(r, open(fn, "w"), indent=1)
    print(k, add_cell.validate(json.load(open(fn)), ex))
