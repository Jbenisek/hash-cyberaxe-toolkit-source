
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

import json, sys, os
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/dig'))
import add_cell
OUT = _hca_public_path_text('__HCA_WORKSPACE__/research/dig/incoming2/sha256-38-G04-U03')
EV = ("research/dig/incoming2/sha256-38-G04-U03/work/scan38.c, scan38b.c, scan38c.c (our code, links tools/traillab unchanged); outputs in the same folder: "
      "val.out dep.out steer_base.out steer_big.out steer_fix_*.out steer_fixbig_*.out exact_k*.out exact*_more.out real_base.out; stats.py pools them")
VALID = ("Validation first (val.out): published 38-step pair reproduces the printed digest, x and y digests equal; Lemma 4.1 map on the published CV returns the published W0..W7; "
         "|F7| = 287,309,824 and |G| = 2^26 exhaustively; the 32-word E16 set = 481b02f9 + subset sums of 82405 with C16 = fe314838, C4 = ab1f01f0, W8C = a1be17b9 (all equal the R38M proof); "
         "forward stepping of the published CV and words gives rows 0..21 ok.")
BASE = ("Model scanned (R38M proof Sections 4-6): CV1 = F_38(IV,M0), a0 in G, gate W7x = c7(a0) - A_-1 in F7 (the only gate on the CV; no F6 gate in 38), W9..W15 = published S, "
        "row 16 passes iff E16x = C16 + W0 + s0(W1) is one of 32 words (2^-27). Sampler: E_-4 is solved so that E16x hits a uniformly chosen element of the 32-word set "
        "(exact weight 2^-27), the other CV words are uniform, the pair is stepped forward from the CV for both members and rows 0..21 checked against the chi38 cells.")
SRC = "our workflow: scan-once-wave2"
DEPTXT = ("DEP (200,000 random CVs with a0 in G, +delta on one CV word, fraction of trials in which W_i changes): E_-3 moves W0,W1 only (1.0000,1.0000, others 0.0000); "
          "E_-2 moves W0,W1,W2; E_-1 moves W0,W1,W2,W3; own-word check E_-k += d moves W_k by exactly -d: 0 violations of 3000. ")
FIXTXT = {
 1: "E_-3 := 315a2db3 or 00000000: pooled 2.28e9 draws (2^30 + 2^26 per constant), 17,460 rows-0..17 passes = P(row17|row16) 2^-16.9957 [2^-17.0171, 2^-16.9743]",
 2: "E_-2 := 5ed877a8 or ffffffff: pooled 2.28e9 draws, 17,217 passes = 2^-17.0159 [2^-17.0375, 2^-16.9944]",
 3: "E_-1 := 78a7f752 or 00000000: pooled 2.28e9 draws, 17,517 passes = 2^-16.9910 [2^-17.0124, 2^-16.9697]"}
BASETXT = "Baseline with all four words random: 8.86e9 draws (2^33 + 2^28), 67,567 passes = P(row17|row16) 2^-17.0004 [2^-17.0112, 2^-16.9895] (E17 cheap filter 8 fixed bits = 2^-8.000)"
UNIF = {
 1: "row16&17 passes (n = 65,516) E_-3 top byte chi2 p = 0.167, low byte p = 0.499; real first blocks (2^22 blocks x 256 a0): all-block top byte p = 0.255, stage-3a passes (n = 17,896) top p = 0.344, low p = 0.604",
 2: "row16&17 passes (n = 65,516) E_-2 top byte chi2 p = 0.854, low byte p = 0.718; real first blocks: all-block top byte p = 0.773, stage-3a passes top p = 0.245, low p = 0.873",
 3: "row16&17 passes (n = 65,516) E_-1 top byte chi2 p = 0.128, low byte p = 0.757; real first blocks: all-block top byte p = 0.384, stage-3a passes top p = 0.123, low p = 0.221"}
REAL = ("Real first blocks (F_38 of random M0, 2^22 blocks x 256 a0 drawn from a 65,536-element pool of G, 1.07e9 evaluations): gate W7 in F7 = 2^-3.9017 [2^-3.9021, 2^-3.9014] (exact 2^-3.90197); "
        "stage 3a (12 shared bits of E16x) given the gate 17,896 = 2^-11.9709 [2^-11.9920, 2^-11.9498] vs exact 2^-12 (+2.0 percent, 2.7 sd by the Poisson count; the 256 a0 per block share one CV, so the true spread is larger; not read as a bias)")
EXACT = {
 1: "Exact enumeration, 12 contexts (random CV rest, a0 in G, gate passed) of all 2^32 values of E_-3, counting row-16 passes: counts 30 25 29 32 41 24 27 40 27 29 38 33, mean 31.25 sd 5.48 se 1.65 (analytic mean is exactly 32: E_-4 shifts W0 uniformly, so E16x is uniform for every value of any other word); no zero. E_-3 reaches W0 only on the bits where E_-1 is 0 (mean 16.1 of 32 bits over 16 contexts) and W1 linearly",
 2: "Exact enumeration, 16 contexts of all 2^32 values of E_-2: 15 contexts have 0 row-16 passes, one has 56; mean 3.5 (analytic mean is 32, so the count is heavy tailed). Reason: E_-2 reaches W0 and W1 only as the CH selector bits (E_-1 bit = 1 for W0, E_0 bit = 0 for W1); the bits that reach them are 25 20 24 23 19 22 25 22 21 30 24 21 28 24 23 25 per context (mean 23.5 of 32), so E_-2 takes only about 2^23.5 distinct (W0,W1) outcomes and the 32-word hit comes in blocks of 2^(32 - bits) equal values. Its full 32 bits enter only W2 (linear)",
 3: "Exact enumeration, 12 contexts of all 2^32 values of E_-1: counts 41 29 38 29 36 31 22 23 27 25 40 32, mean 31.08 sd 6.20 se 1.87 (analytic mean 32); no zero. E_-1 enters S1 and CH of W0, CH of W1 and W2, and linearly W3"}
NAME = {1: "E-3", 2: "E-2", 3: "E-1"}
WORD = {1: "E_-3", 2: "E_-2", 3: "E_-1"}
ROW = {1: -3, 2: -2, 3: -1}
recs = []
for k in (1, 2, 3):
    n = NAME[k]; w = WORD[k]
    def mk(q, question, status, labels, number, notes, topic):
        cid = "sha256-38|CV.%s|CV|Q%d" % (n, q)
        return cid, {"hash": "sha256-38", "row_i": ROW[k], "row_j": None, "object": "CV word %s of the first block (sha256-38 ordinary collision)" % w,
                "question": question, "labels": labels, "status": status, "number": number, "source": SRC, "own_test": True, "evidence": EV,
                "date": "2026-10-12", "lever": False, "gain_bits": 0.0, "gain_basis": "q3", "topic": topic,
                "notes": "universe cell %s. %s" % (cid, notes)}
    # Q1
    recs.append(mk(1, "How many values of %s, and which W words and conditions does the attack tie to it?" % w, "COMPUTED", ["D"] + (["S"] if k == 2 else []),
        "%s: 2^32 values, 0 cell or two-bit conditions (rows -4..-1 carry none in chi38), no gate; it enters only the words %s (measured and algebraic)" % (w, {1: "W0, W1", 2: "W0, W1, W2", 3: "W0, W1, W2, W3"}[k]),
        DEPTXT + EXACT[k].split(';')[-1].strip() + ". " + BASE + " " + VALID + " The only CV gate of the 38-step attack is on A_-1 (F7, p7 = 2^-3.90197); there is no F6 gate and no condition on any E word. " + REAL,
        "r38.cv.%s.q1" % n))
    # Q2
    recs.append(mk(2, "Is %s needed: replace it by a constant and recompute the event (rows 16..17 given the sampler)?" % w, "LOCAL_ONLY", ["D", "Z"],
        "Not needed as a free variable: replaced by constants the rate is unchanged, " + FIXTXT[k].split(': ', 1)[1] + " vs baseline 2^-17.0004; row 16 itself is exactly 2^-27 for every value of %s because E_-4 shifts W0" % w,
        FIXTXT[k] + ". " + BASETXT + ". Replace test run with six runs of 2^26 to 2^30 draws; per-run results are in steer_fix*.out, all within about 2 sd of 2^-17. " + BASE + " " + VALID +
        " LOCAL_ONLY: rows 0..17 only (rows 18..37 not sampled: row 18 was reached by 8 of 65,508 row-17 passes in the baseline, so the deep tail is not tested here). Gain 0: the CV is the output of the first block, not a choice, so a constant is not an option for the attacker.",
        "r38.cv.%s.q2" % n))
    # Q3
    recs.append(mk(3, "How many values of %s remain consistent with the event, and is %s uniform among passes?" % (w, w), "LOCAL_ONLY", ["D"] + (["S"] if k == 2 else []),
        {1: "32 row-16 passes per 2^32 values of E_-3 on average (5 bits left of 32; exact enumeration 12 contexts mean 31.25 se 1.65); uniform among row16&17 passes (chi2 p 0.17/0.50) and real blocks",
         2: "about 2^23.5 distinct effective values toward row 16 (selector bits, 16 contexts: 19..30 bits); 15 of 16 contexts have 0 row-16 passes among all 2^32 values; uniform among row16&17 passes (p 0.85/0.72) and real blocks",
         3: "32 row-16 passes per 2^32 values of E_-1 on average (exact enumeration 12 contexts mean 31.08 se 1.87); uniform among row16&17 passes (p 0.13/0.76) and real blocks"}[k],
        EXACT[k] + ". " + UNIF[k] + ". " + REAL + " " + BASE + " LOCAL_ONLY: row 16 exact, row 17 sampled; no deeper row. Freedom of the whole path is bounded by 2^32 per word and is not narrowed by these rows beyond the 2^-27 and 2^-17 factors already in the ledger. No bias found (every p above 0.05).",
        "r38.cv.%s.q3" % n))
    # Q4
    alt = {1: "E_-3 is an alternative row-16 solver to E_-4: W1 = c - E_-3 is a bijection, mean 31 solutions per 2^32 (E_-4 gives exactly 32)",
           2: "E_-2 cannot replace E_-4 as the row-16 solver: 15 of 16 contexts give no solution among 2^32 values (selector-only effect on W0,W1)",
           3: "E_-1 is an alternative row-16 solver to E_-4: mean 31 solutions per 2^32 (E_-4 gives exactly 32)"}[k]
    recs.append(mk(4, "Alternatives: can %s replace E_-4 as the word that steers row 16 or a later row, or can the CV be shaped differently?" % w, "LOCAL_ONLY", ["D", "Z"] + (["S"] if k == 2 else []),
        alt + "; no gain: the CV is fixed by the first block, so no steering variable exists in the ordinary attack",
        alt + ". " + EXACT[k] + ". " + DEPTXT + "Which word steers is irrelevant to the cost because the CV is an output of F_38(IV,M0) for random M0 (real-block uniformity above), not an input; the attack filters by the gate and rows 16.. and takes the CV as it comes. " + BASE + " LOCAL_ONLY: row 16 exact counts, rows 17 sampled. Nonzero chaining-value differences are a separate cell (G04-U06).",
        "r38.cv.%s.q4" % n))
ex = add_cell.load()
for cid, r in recs:
    fn = os.path.join(OUT, cid.replace('|', '_') + '.json')
    json.dump(r, open(fn, 'w', encoding='utf-8'), indent=1)
    errs = add_cell.validate(json.load(open(fn, encoding='utf-8')), ex)
    print(cid, 'OK' if not errs else errs)
