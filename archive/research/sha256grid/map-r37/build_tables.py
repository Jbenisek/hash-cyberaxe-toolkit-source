# Writes entries_r37.tsv (one row per sha256-r37 board entry).  Summaries are our own words; numbers marked [note]
# are the filer's own figures as printed in its public note; COMPUTED/DERIVED/GUESS mark our numbers.
# Credit is by submission id only; no participant text is copied.

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

import csv, json
B = _hca_public_path_text('__HCA_WORKSPACE__/research/rivals/boards_sha256-r37-exploratory_live.json')
d = json.load(open(B, encoding="utf-8"))
meta = {s["id"][:8]: s for s in d["submissions"]}
E = {}
def e(i, *v):
    assert len(v) == 7, i
    E[i] = v
GB = "GB generic birthday"
P1 = "P1 single-S two-block (ePrint 2026/1120)"
P2 = "P2 A0-variant two-block (ePrint 2026/1120)"
e("f0065dce", GB, "1 block (55-byte msgs)", "none",
  "counted 7x36-bit SWAR, 140-bit key, uninitialised tagged table, candidate cap",
  "first r37 package (v0); claimed 125.383 [note]",
  "H1 random-function table/cap tails; SWAR packing lineage",
  "visible in successor 383bad42: review rejected v0 - messages not regenerable from table index (fatal), expectation in a worst-case ledger, H1 untested, undeclared SWAR premise")
e("383bad42", GB, "1 block", "none",
  "deterministic index-to-message family (two coins), round-skip key (144 digest bits final after round 35 E half), SWAR 1451 ops/7 msgs [note]",
  "v1b answers the v0 review: regenerable messages, deterministic cap V, scaled H1 experiments",
  "H1 table/cap tails (preregistered scaled experiments h1-success, h1-overwrite); H2 SWAR exactness", "")
e("abaa09ae", GB, "1 block", "none",
  "bit-sliced 256-lane grouped search (2^24 msgs share W0..W12), 160-bit pre-last-round key, gates charged x2",
  "first bit-sliced r37 birthday entry",
  "H1 grouped digests independent-uniform (scaled 18-bit key experiments, single-group layout)", "")
e("817d444c", GB, "1 block", "none",
  "bit-sliced grouped, 144-bit key fixed before round 36, 64-register VM with every load/store charged, 48,704 ops/batch [note]",
  "physical-scheduling convention later used by all bit-sliced entries",
  "H1-grouped-random-digests (scaled experiments)", "")
e("29be77ba", "P0 published-S straight port", "2 blocks + padding block", "paper's S only; no variants",
  "scalar first blocks (1 compression + 64 ops), Step 2 by brute force (2^-10.000 measured [note]), Step 3 over 32 L*",
  "claimed 78.32 [note]; A_C 2^70; Step 1 charged at 4x the paper",
  "H1 transcription reading; H2 measured rates carry over; H3 op counts from pseudocode; H4 A_C<=2^70",
  "not visible; the refile 84f1f00b switched to pooled per-step rates with exact Poisson/Bonferroni bounds and added H5, which suggests the q3 statistic was challenged (GUESS)")
e("50c7864d", GB, "1 block", "none",
  "383bad42 family and key on 7x36 SWAR, 1,406 ops/7 msgs (butterfly key transpose) [note]",
  "-45 ops per batch on 383bad42", "H1, H2 as 383bad42", "")
e("fca38c6d", GB, "1 block", "none",
  "bit-sliced physically scheduled, 47,932 ops/batch; key on raw state words (no feed-forward adders); NOT-free full adder [note]",
  "builds on abaa09ae and 817d444c", "H1", "")
e("84f1f00b", "P0 published-S straight port", "2 blocks + padding block", "paper's S only",
  "as 29be77ba",
  "claimed 78.59 [note]; product of pooled per-step rates (H5), joint 95% Poisson/Bonferroni bounds, organizer experiment re-measuring q2 and row 16",
  "H1-H5 (H5: pooled product <= true probability)",
  "not visible; no later r37 refile by this author")
e("64bca7e2", GB, "1 block", "none",
  "bit-sliced, 46,384 ops/batch (merged round-35 column, register pool tweaks) [note]",
  "builds on 817d444c and fca38c6d", "H1-grouped-random-digests", "")
e("a39b593c", "GB distribution-free", "1 block", "none",
  "iid family (21 zero + 34 random bytes), bijective early key, sort + duplicate finder, 67,409 ops/256 msgs [note]",
  "heuristic-free alternative to the grouped family", "none declared (distribution-free bound)", "")
e("f208cdfa", GB, "1 block", "none",
  "fca38c6d + folded sums, searched addend order, one allocation, NOT-free mixed-polarity carries: 45,773 ops/batch [note]",
  "claimed 124.10776 [note]", "H1",
  "not visible; never refiled (GUESS: superseded by 6de1b685 and 5951ba00)")
e("7c4e24c7", "P0w witness port", "2 blocks + padding block", "paper's SFS pair and collision structure",
  "capped chained verification over 2^81 chains at 132 ops each; the paper's 2^79.1 search charged as 2^80 development [note]",
  "claimed 88.04985 [note]", "H1a/H1b per-chain 2^-10 x 2^-71 bound",
  "not visible (GUESS: the ledger does not price an executable search - no compression is charged per chain)")
e("6c77089c", P1, "2 blocks + padding block",
  "dense part = paper's S (A0..A13, E4..E13, W8..W13 of both members); no variants; Step 3 over 32 L* (4 can never pass row 16)",
  "grouped first blocks (W0..W14 per group, W15 varies) in 7x36 SWAR, rounds 15..36, 1442 ops/7 = 206 per FB [note]; rare path SWAR W6 + scalar Step 3a/3b; fixed caps with halting counter",
  "package d1: exact transcription with corrections (W6 has 4 conditions; A15[29]=A17[29]), exact F6/F7 (p2 2^-9.8796 [note]), q3_model 2^-74.01 [note]",
  "H1 uniform CV (grouprate.c, 2^29.8 compressions); H2 q3 (preregistered SMC 32 seeds, organizer replica, 1,020 validation replicates); H3 packed-word pricing; H4 A_C 2^60, A_S 2^50, DEV 2^40 by comparison", "")
e("6de1b685", GB, "1 block", "none",
  "64bca7e2 + shared-XOR AND-NOT, 64 allocatable registers: 45,518 ops/batch [note]",
  "counted-program changes only", "H1", "")
e("5951ba00", GB, "1 block", "none",
  "64bca7e2 base; key read through the last four rounds (fewer rounds computed per message)",
  "best generic entry (board 123.93722)", "H1-grouped-random-digests (18-bit masked projections)", "")
e("efd8aa9d", P1, "2 blocks + padding block", "paper's S",
  "bit-sliced 256-lane first-block batch with both Step-2 tests in the circuit: 44,265 ops/256 = 172.9 per FB [note]",
  "6c77089c with the SWAR batch replaced; accounting repairs carried from r38 reviews",
  "H1 per trial; H2; H3 bit-sliced pricing; H4; H5 within-group pairs (<=2^-40, Bonferroni, Hoeffding cap)", "")
e("ad9745bf", P1, "2 blocks + padding block", "paper's S",
  "bs1: bit-sliced batch 44,135 ops/256 = 172.4 per FB [note]; valid lanes' CV recomputed on the scalar machine (1,198 ops)",
  "same idea as efd8aa9d, independent", "H1-H4 (H3 bit-sliced pricing)", "")
e("dd6656d4", P1, "2 blocks + padding block", "paper's S",
  "bs1 + dead W35/W36 inlined, F6/F7 tested as affine parity checks (F7 two spaces, F6 three), interleaved round-36 adders: 43,466 ops/batch [note]",
  "circuit shaving", "H1-H4 + H5 SMC confidence calibration (flagged as unreviewed)", "")
e("359e68f7", P1, "2 blocks + padding block", "paper's S",
  "dd6656d4 + post-loop W6/W7 adders, truncated carry, parity factoring; scalar lane_cv 1,198 -> 965 and step3 tightened [note]",
  "claimed 73.94602 [note]", "H1-H4",
  "visible in refile f09f56e7: lane_experiments rated H4 unsupported because H4's evidence ids did not list the organizer experiments")
e("f09f56e7", P1, "2 blocks + padding block", "paper's S",
  "same program as 359e68f7", "evidence linkage only: both experiments load and validate the <8 KiB advice package", "H1-H4", "")
e("ad184203", "GB distribution-free", "1 block (organizer family)", "none",
  "keyed tabulation-hash chained table instead of the organizer merge sort", "analytic, no experiments", "none", "")
e("6523a67c", "P1v S-shift variants", "2 blocks + padding block", "48 shifts of S (A0+=D, E4+=D, W8-=D in both members)",
  "bit-sliced batch replicating per-variant W7/W6 parity tests: 59,209 ops/256 trials [note]; overlap charge kappa2 = 3/5",
  "claimed 69.99374 [note]; pooled 48x40 q3 study", "bs1 premises + H5 variant structure and overlap charge",
  "visible in 1f12a09a's note: refuted as F-EXEC-COST-MISMATCH (priced work not the executed program)")
e("5db3c77e", P1, "2 blocks + padding block", "paper's S",
  "bounded-distance CSE, clean-spill eviction, tighter scalar rare path: 43,335 ops/batch [note]",
  "best P1 entry (board 73.94225)", "H1-H4", "")
e("76407c7c", P2, "2 blocks + padding block", "12,103,680 A0 variants, 64 c7 classes of 3600",
  "as 1c368173", "claimed 63.47455 [note]", "as 1c368173",
  "visible in refile 1c368173: not_evaluable - all four lanes rated H4 unsupported (A_C 2^60 inherited without evidence)")
e("871bfee5", P2 + " bucket table", "2 blocks + padding block", "2^18 A0 variants",
  "as b947b377", "claimed 64.0687 [note]", "as b947b377",
  "visible in refile b947b377: not_evaluable - H4 unsupported; an undeclared per-pair upper bound used in Chen-Stein; H3 lacked experiment coverage")
e("1c368173", P2, "2 blocks + padding block",
  "A0 carries no condition: 12,103,680 variants (E4 top bits 000, W8 cell + 3 two-bit conditions); c7 classes (22,976 values), 64 classes of 3600 used",
  "per FB: 1 compression, 64 scalar W7 tests (640 ops), per passing class bit-sliced W6 (518..550 per 256), u scalar + 2^32-entry R16 table (53 ops per pair) [note]",
  "origin of the A0-variant line: 244.58 good pairs per FB [note], N_FB 2^60.09 [note]",
  "H1; H2 variant q3>=2^-74.02 (proof that q3 is variant-independent up to W24, preregistered 32 replicates); H3 first-block dependence (0 co-successes in 32,911); H4 A_C bounded against the r32 measured re-run; H5 bit-sliced W6 pricing", "")
e("9ea8039a", P2 + " bucket table", "2 blocks + padding block", "2^18 A0 variants",
  "as b947b377", "second attempt", "as b947b377",
  "visible in b947b377: failed at deterministic intake - an experiment emitted 18 observation keys per trial; the runner allows 16")
e("b947b377", P2 + " bucket table", "2 blocks + padding block", "2^18 A0 variants by a closed formula over the free W8 bits",
  "per FB 1 compression + 91 ops; 2^32-bucket table indexed by A_-1 (memory 2^51 [note]); W6 by one table load; 46 ops per valid pair [note]",
  "independent discovery of the A0 freedom; 278.28 valid pairs per FB [note]; Chen-Stein success argument",
  "H1; H2 q3_V>=2^-74.01 (8,192 replicates, Q_D upper bound); H3 cross-variant dependence <=2^30 (W16..W22 Hamming test, 17.7M pairs); H4 A_C against the r32 measurement", "")
e("087a18c4", P2, "2 blocks + padding block", "as 1c368173",
  "as 1c368173 (machine adopted verbatim)",
  "two readings only: H6 q3 at the printed bound 2^-74.0173; H7 exact success floor mu0 = 0.49466 [note]",
  "H1-H5 inherited + H6, H7 (r38 precedent 20dbd783)", "")
e("1f12a09a", P2, "2 blocks + padding block", "222 classes with >=3456 variants (782,800 variants)",
  "one bit-sliced W7 program over classes (375 ops/FB), W6 for up to 4 batches (459 per batch), 24-bit chunk lane scan, packed groups of four 64-bit lanes for u (34 ops/4), 256-entry presence word for row 16 [note]",
  "on 087a18c4: 830.99 good pairs per FB, 421 fixed + 44,137 data ops per FB, q3 re-estimated 2^-74.0252 [note]",
  "H1-H4; H5 bit-sliced filters + packed groups; H6; H7; rho budget 2^35", "")
e("9c809454", "GB organizer construction", "1 block", "none",
  "organizer merge-sort birthday, same algorithm", "tighter accounting 132 -> 131.804703", "none", "")
e("04441cbc", P2, "2 blocks + padding block", "222 classes",
  "as 7319bba9", "byte-identical note to 7319bba9", "as 7319bba9",
  "not visible; the identical note was refiled 52 minutes later as 7319bba9 and passed (GUESS: judge-step flake or a package-only fix)")
e("7319bba9", P2, "2 blocks + padding block", "222 classes",
  "decision-DAG W6 over the bits of A_-1 and C6-A_-2 (129.8 + 48 ops per batch vs 459), W7 DAG <=191 ops/FB, NOT-free adder, lane-safe packed pairs, presence word [note]",
  "265 fixed + 31,196 data ops per FB (W6 10,700, pairs 20,080) [note]; own q3 2^-74.03 (study B registered after study A was read) [note]",
  "H1-H4; H5 decision-DAG pricing (branch 1, jump 1, bit test 2; DAG code built by charged precomputation); H8 conditional DAG cost; implicit vbar bound", "")
e("d3ec5c41", P2 + " x-indexed table", "2 blocks + padding block",
  "222 classes; W6 fibres of phi(a0,x): 293.6 distinct values per class vs 3,526 variants [note]",
  "x=A_-1 table built in charged preprocessing: T0[x] lists W7-passing classes (5 ops); W6 on fibre planes (bit-serial add of broadcast cb + F6 test, 200 data-independent ops per 256 fibres, 1.55 batches per class); members of passing fibres read in place (14 ops per fibre); packed u, presence word, rows 16..36 unchanged [note]",
  "vs 7319bba9: per-FB 13.08 -> 7.23 units, data ops 31,196 -> 16,431.31 [note]; vs 1f12a09a: fixed 421 -> 51, data 44,137 -> 16,431 [note]; memory 2^32.7 -> 2^50; table build < 2^58 ops",
  "H1 (x uniform and independent of cb); H2/H3 quoted from 7319bba9, not re-run; H4 A_C 2^60, A_S 2^50; H5 new reading (2^50-byte table is ordinary memory, a read is 1 op); H7; H9 new (fibre statistics from three 1,500-x samples per class, x1.02)", "")
cols = ["id8", "user", "status", "board_score", "created", "family", "blocks", "dense_part_variants",
        "engine_batching", "what_changed", "premises_evidence", "ruling_if_failed"]
rows = []
for i8, s in sorted(meta.items(), key=lambda kv: kv[1]["createdAt"]):
    rows.append([i8, s["solverUsername"], s["status"], s.get("officialScore") or "", s["createdAt"][:16]] + list(E[i8]))
assert len(rows) == 34 and set(E) == set(meta), (len(rows), set(E) ^ set(meta))
with open("entries_r37.tsv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f, delimiter="\t"); w.writerow(cols); w.writerows(rows)
print("entries written:", len(rows))
