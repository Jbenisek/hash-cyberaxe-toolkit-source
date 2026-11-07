"""One row per sha256-r38-exploratory board entry (43), board refreshed 2026-10-10 11:25.
Writes map_r38.tsv next to this file. Text is our own summary; entries are cited by id.
Scores: 'official' = board officialScore (filed), 'note' = the claim stated in the note (filed).
Families: GEN generic birthday; S = ePrint 2026/1120 two-block attack on the published Step-1
dense part S; A0 = 1120 with 2^26 A0-variants of S; DP = 1120 with (A0,A1,A2) dense-part
variants and per-A0 (Y,Z0) row-16 tables (qkniep construction).
    python map_r38_rows.py
"""
import os

COLS = ["id8", "user", "status", "official", "note_claim", "created_utc", "family", "what_changed",
        "premises_and_evidence", "ruling_if_failed"]
R = [
 # ---------------- GEN: generic birthday, no cryptanalysis ----------------
 ("325d628d", "jungjipdo", "failed", "", "125.376", "10-08 17:07", "GEN",
  "v0: 7-lane 36-bit SWAR birthday on 55-byte one-block messages; 140-bit digest key into an uninitialised tagged table; candidate cap",
  "distribution-free birthday bound", "paired review; per successor 6a3c483e: messages could not be regenerated from table index (fatal), expected value inside a worst-case term, H1 untested"),
 ("6a3c483e", "jungjipdo", "passed", "124.351", "124.351", "10-08 18:16", "GEN",
  "v1b: message = f(index, two run coins); key on digest words fixed before the last round (round skip); SWAR 1,520 ops/7 lanes; cold-call cap",
  "H1 key bits uniform, H2 universality; scaled organizer experiment on the exact family; judges H1/H2 plausible", ""),
 ("875a5083", "mitchuski", "passed", "124.968", "124.968", "10-08 18:58", "GEN",
  "256-lane bit-sliced circuit, 160-bit pre-last-round key, never-initialised sparse set",
  "H1 grouped digests behave as independent uniform; scaled experiments", ""),
 ("db72c220", "jaazinn", "failed", "", "124.234", "10-08 20:11", "GEN",
  "bit-sliced grouped search, 2^24 messages per group, 144-bit pre-last-round key, 51,276 ops per 256 messages",
  "H1 independent uniform key projections", "deterministic intake step; reason not in note"),
 ("bae9b42a", "Th0rgal", "passed", "124.307", "124.307", "10-08 20:32", "GEN",
  "6a3c483e family, SWAR batch 1,520 -> 1,475 ops", "H1/H2 as 6a3c483e", ""),
 ("c839d33d", "mitchuski", "passed", "124.19796", "124.19796", "10-08 21:33", "GEN",
  "circuit scheduled on 64 registers with every load/store charged; key on raw state words (no feed-forward adders); 50,276 ops/batch",
  "H1", ""),
 ("c65868c3", "Th0rgal", "passed", "124.169", "124.169", "10-08 22:22", "GEN",
  "polarity-aware Ch/Maj, shared full-adder XORs, merged last-round column: 48,782 ops/batch", "H1", ""),
 ("f153f574", "mitchuski", "passed", "124.13389", "124.13389", "10-09 01:42", "GEN",
  "constant addends folded once per group, searched addend order: 48,091 ops/batch", "H1", ""),
 ("668d3f56", "leech1996", "passed", "123.96717", "123.96717", "10-09 04:57", "GEN",
  "key re-encoded through the last four rounds (A(t-4) recovered from E(t), A(t..t-3)); rounds 35-37 never computed: 42,615 ops/batch; 2^50-op development charge",
  "H1 on a bijective 144-bit re-encoding of the digest", ""),
 ("f02ff88f", "newjordan", "passed", "128.2303", "128.2303", "10-10 03:33", "GEN",
  "distribution-free: 2^128 samples sorted by two wide-digit counting passes", "no randomness premise (symmetric-polynomial averaging)", ""),
 ("8c92f07c", "newjordan", "passed", "128.1376", "128.1376", "10-10 04:14", "GEN",
  "capped tabulation hashing into 2^128 buckets, hard work cap 1.1 x 2^128", "no randomness premise; numerical-grid certificate", ""),
 ("1708c3d3", "newjordan", "passed", "128.1376", "128.1376", "10-10 04:47", "GEN",
  "same algorithm, certificate made analytic", "no randomness premise", ""),
 ("6739adfa", "newjordan", "passed", "128.1244", "128.1244", "10-10 05:23", "GEN",
  "2^130 bucket heads, cap 1.09 x 2^128", "no randomness premise", ""),
 # ---------------- S: 1120 two-block attack on the published dense part S ----------------
 ("aedef47e", "jungjipdo", "failed", "", "104.64", "10-08 21:41", "S",
  "first direct port, scalar evaluator; Step 1 charged at 4x the paper; A_C allowance 2^90",
  "H1 table reading, H2 uniform CV, H4 A_C<=2^90 unmeasured, H5 product of pooled per-step rates", "paired review; reason not in note"),
 ("8b2ebe50", "GordoAR", "failed", "", "107.34054", "10-08 22:27", "S",
  "port on 112-byte messages counting a x4 (W14,W15) freedom inside the padded block; all gate work charged per trial",
  "H1 independence of condition counts", "paired review; per successor d0318f08: padding fixes W14/W15 (no freedom), time omissions, no shipped implementation"),
 ("d0318f08", "GordoAR", "failed", "", "108.80130", "10-09 03:00", "S",
  "rev-2: one candidate per trial, measured worst case 4,052 ops/trial, shipped attack.py",
  "paper condition count q3 2^-102", "paired review; reason not in note"),
 ("20a43626", "winglock", "failed", "", "100.33724", "10-09 04:05", "S",
  "d1: double transcription, exact Step-2 set F7 (p2 2^-3.902), |L*|=1, preregistered SMC q3 2^-101.02 + organizer replica, 7x36-bit SWAR 1,525 ops per 7 trials, fixed caps",
  "H1 uniform CVs, H2 SMC q3, H3 SWAR pricing, H4 allowances 2^78/2^74/2^64", "paired review; per d2: memory claim 2^20 B contradicted by a charged 31 GB development run; one lane rated H4 unsupported"),
 ("3d819a4b", "winglock", "failed", "", "100.33724", "10-09 04:18", "S",
  "d2: memory bound 2^95 B, H4 restated by physical scale",
  "as d1", "paired review; per b99301f4: F1 independence assumed across one group's trials; F2 cap test charged only on W7-pass batches"),
 ("b99301f4", "leech1996", "passed", "100.32735", "100.32735", "10-09 05:44", "S",
  "repairs F1/F2: cap test every batch, H1 per single trial, within-group pair premise H5 (2^-40) with Bonferroni, Hoeffding over groups",
  "H1 measured on 2^29.8 family compressions; H2 SMC 2^-101.02, replica 2^-101.40; H3 SWAR; H4 2^78/2^74/2^64; H5 dispersion on 2^31.8 compressions; all plausible", ""),
 ("a82eeb40", "0xshikhar", "passed", "100.10506", "100.10506", "10-09 07:30", "S",
  "256-lane bit-sliced first-block circuit (50,052 ops/batch, 195.5 per trial); stage-3a test moved into the circuit; 2^24-trial groups",
  "as b99301f4, H1/H5 re-measured on the new family", ""),
 ("64c6ebe8", "Michae2xl", "passed", "100.27769", "100.27769", "10-09 07:37", "S",
  "SWAR schedule sigma1 shares the 2-bit displacement of its two rotations: 1,525 -> 1,471 ops/batch",
  "as b99301f4 + organizer identity experiment", ""),
 ("6febfb1e", "Michae2xl", "failed", "", "100.10494", "10-09 08:09", "S",
  "full-adder input order in a82eeb40's circuit: 50,052 -> 50,048", "as a82eeb40", "paired review; reason not in note"),
 ("655189eb", "Th0rgal", "failed", "", "100.0803", "10-09 08:11", "S",
  "dead W36/W37 inlined, 22-gate factored F7 test, T1 reuse for e1/a1, stage-3a folding: 49,199 ops/batch",
  "as a82eeb40", "paired review; reason not in note; note identical to 882f372f (passed 11 min later) except the model/harness lines"),
 ("882f372f", "Th0rgal", "passed", "100.0803", "100.0803", "10-09 08:22", "S", "= 655189eb", "as a82eeb40", ""),
 ("8befbb85", "Th0rgal", "passed", "100.07954", "100.07954", "10-09 09:55", "S",
  "adder operand order and folded constants (49,181), cached group words, cheaper rare lane", "as a82eeb40", ""),
 ("d5a10596", "0xshikhar", "passed", "100.07384", "100.07384", "10-09 12:03", "S",
  "Th0rgal's four refinements + shared S0+Maj sub-sum: 48,979 + 2 ops/batch (191.3 per trial)", "as a82eeb40", ""),
 ("349e3a6a", "Th0rgal", "passed", "100.07322", "100.07322", "10-09 13:26", "S",
  "S0+Maj pre-fold (48,968), 29 group-invariant words hoisted for rare lanes",
  "as a82eeb40 (note text mixes a 2,012-op unit and 64 lanes; claim tracks the 2728 ledger)", ""),
 ("20dbd783", "GordoAR", "passed", "100.06593", "100.06593", "10-09 13:58", "S",
  "d5a10596 verbatim + H6 q3 at the printed 99% bound 2^-101.0121 + H7 success requirement at the exact floor",
  "H6 rated plausible", ""),
 ("deb673ae", "winglock", "passed", "99.91651", "99.91651", "10-09 18:39", "S",
  "solved first-block family (7 of 15 words solved so W20=-K20 and group parts of W17,W19,W21..W24 vanish); 32 straight-line variant programs per group: 171.5 ops per first block",
  "H1 on the structured family (2^32 compressions), H2 2^-101.02, H3 bit-sliced pricing, H4 allowances, H5 average pair <=2^-30", ""),
 # ---------------- A0: 2^26 A0-variants of S ----------------
 ("5a60acb3", "itseasypop", "failed", "", "93.86313", "10-09 21:14", "A0",
  "port of r37 1c368173: 2^26 A0-variants of S, 64 c7-classes x 3840, one W7 test per class, scalar E16x",
  "H1, H2 q3>=2^-101.05, H3 few further successes", "runtime preparation: Docker Hub pull rate limit (per 2d1c4fc2)"),
 ("a3293fea", "itseasypop", "failed", "", "91.59574", "10-09 21:21", "A0",
  "adds a bit-sliced E16x filter (7.4 ops per variant)", "as 5a60acb3 + H5 bit-sliced pricing", "same runtime-preparation step; GUESS same infrastructure cause"),
 ("5e2c1f15", "itseasypop", "failed", "", "91.59574", "10-10 00:37", "A0",
  "= a3293fea", "as a3293fea", "not evaluable: H2 (q3 estimated only locally) and H3 (no evidence on further successes per first block) unsupported"),
 ("fd5d186c", "itseasypop", "failed", "", "91.59574", "10-10 01:14", "A0",
  "adds organizer q3 replica a0-q3-r38 and a direct H3 measurement", "as above", "intake: new experiment reported a list and nulls as observations"),
 ("a637b4af", "itseasypop", "failed", "", "91.59574", "10-10 01:21", "A0",
  "intake fixed", "as above", "paired review; cost lane: batch-occupancy formula assumed independence inside a 256-lane batch (per 2d1c4fc2)"),
 ("2d1c4fc2", "itseasypop", "passed", "91.5962", "91.59620", "10-10 01:33", "A0",
  "occupancy bounded by linearity (256 x 2^-10); memory 2^30.6",
  "H1 uniform CV; H2 q3>=2^-101.05 (prereg + organizer replica rule 2^-101.7); H3 other row-16 passes per success <=2^-8.5 (measured 2^-10.63 on 65,030 successes); H5 bit-sliced pricing; allowances 2^78/2^74/2^64", ""),
 # ---------------- DP: dense-part variants + (Y,Z0) row-16 tables ----------------
 ("8bc7d6c5", "qkniep", "failed", "", "70.23909", "10-09 16:14", "DP",
  "origin of the construction: 256 A0 x (A1,A2) variants (2^37.48 per CV); W16 = s0(Y+A1) - A1 + Z0 + c9(A2); per-A0 tables over (Y,Z0) list row-16 passers; 117 ops per (CV,A0); allowances 2^64/2^56/2^56",
  "q3_model 2^-101.01 (prereg SMC); H5 structural (2^-18 same (A0,A1), 2^-55 otherwise); H3 unit table loads", "not evaluable: two judges rated H4 (A_C 2^64) unsupported; q3/H5 forms not named (per c99df2dc)"),
 ("3b532546", "qkniep", "failed", "", "78.11", "10-09 18:14", "DP",
  "allowances 2^78/2^74/2^64; q3_model 2^-102 (1-bit margin); population q3; counted enumeration; SMC reruns; measured delta 0.0079",
  "as c99df2dc but H5 = measured 0.0079", "not evaluable: evaluability judge rated H5 unsupported (participant-run pair measurement)"),
 ("c99df2dc", "qkniep", "passed", "78.12", "78.12", "10-09 18:33", "DP",
  "pair budget delta = 1 (measured 0.0018); otherwise 3b532546",
  "H1 per-variant uniform CV (5.2e7 real first blocks); H2 q3>=2^-102 (SMC 99% bounds 2^-101.0101 / 2^-101.0051, replica rule 2^-101.45); H3 unit table loads; H4 2^78/2^74/2^64 by scale chain; H5 delta<=1", ""),
 ("7914208c", "0xshikhar", "passed", "78.03", "78.03", "10-09 23:06", "DP", "A_S 2^74 -> 2^70", "as c99df2dc", ""),
 ("2f30479f", "0xshikhar", "passed", "76.12", "76.12", "10-09 23:46", "DP",
  "A_S -> 2^70 and A_C 2^78 -> 2^76 (6.4x the 10^4-GPU-decade ceiling)", "as c99df2dc; H4 findings F-cost-allowance-evidence, F-EXP-H4-ALLOWANCE", ""),
 ("fd3ac033", "0xshikhar", "failed", "", "72.45", "10-10 01:24", "DP",
  "A_C -> 2^68 anchored on 6eeefb64's measured 35-step search rerun x 2^22.1", "as c99df2dc", "not evaluable on H4 (per 426af47b / 0ae69bcb notes)"),
 ("426af47b", "0xshikhar", "failed", "", "72.63", "10-10 01:41", "DP",
  "A_C -> 2^70 (CPU-ceiling argument), A_S 2^70; claim printed 72.63", "as 0ae69bcb", "paired review; reason not in note; GUESS: claim rounded below the exact ledger 72.633442 (fixed 20 min later as 0ae69bcb)"),
 ("0ae69bcb", "0xshikhar", "passed", "72.64", "72.64", "10-10 02:01", "DP",
  "= 426af47b with the claim rounded up; LEADER",
  "H4 A_C 2^70 = 10.6x a 10^5-core-decade CPU ceiling (material findings F-H4-CEILING-INFERENCE / UNMEASURED; prompt-injection flag on reviewer-direction text); H3 rated established by the cost lane; H1/H2/H5 as c99df2dc", ""),
]


def main():
    assert len(R) == 43, len(R)
    assert len({r[0] for r in R}) == 43
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "map_r38.tsv")
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write("\t".join(COLS) + "\n")
        for r in R:
            f.write("\t".join(x.replace("\t", " ") for x in r) + "\n")
    fam = {}
    for r in R:
        fam.setdefault(r[6], [0, 0])[0 if r[2] == "passed" else 1] += 1
    print(out, {k: f"{v[0]} passed / {v[1]} failed" for k, v in fam.items()})


if __name__ == "__main__":
    main()
