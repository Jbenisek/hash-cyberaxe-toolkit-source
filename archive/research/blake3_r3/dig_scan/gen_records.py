
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

import json, os
OUT = _hca_public_path_text('__HCA_WORKSPACE__/research/dig/incoming3')
EV = "research/blake3_r3/dig_scan/"
SRC = "our workflow: dig-scan-b3r3"
DATE = "2026-10-12"
CONV = ("Convention: filed rho.py ledger (research/blake3_r3/candidate_blake3/experiments/rho.py, 125.10856); our copy led() in dig_scan/common.py reproduces "
        "total 58516868528290066067270868803654989992793/2 exactly. KNOWN ANSWER reproduced first: verifier blake3 empty-input 7 rounds = af1349b9...f3262; "
        "rho.digest_words equals verifier blake3(64 B msg) at 7 and 3 rounds on 400 cases; rho.selftest True (595 ops/batch). Gains are POSITIVE = saving in bits of time_log2 (+memory term).")
U = {}
def rec(unit, loc, obj_kind, q, label, question, status, number, labels, evidence, held, reopen, notes, lever=False, gain=None, basis=None, own=True):
    d = dict(hash="blake3-r3", row_i=None, row_j=None, object=f"{loc} {label}", question=question, labels=labels, status=status, number=number,
             source=SRC, own_test=own, evidence=evidence, date=DATE, lever=lever, gain_bits=gain, notes=f"universe cell blake3-r3|{loc}|{obj_kind}|{q}. " + notes + " " + CONV,
             held_fixed=held, reopen_if=reopen)
    if basis: d["gain_basis"] = basis
    U.setdefault(unit, []).append((f"blake3-r3_{loc}_{obj_kind}_{q}".replace(".", "_"), d))

AM, BG, CT, DR = EV + "a_machine.json (a_machine.py)", EV + "b_generic.json (b_generic.py)", EV + "c_tests.json (c_tests.py)", EV + "d_regs.json (d_regs.py)"
CO = EV + "e_combo.json (e_combo.py)"

# ================= U82 IMM
rec("U82", "MACHINE.IMM", "MACHINE", "Q2", "immediates",
    "Is the 256-bit immediate necessary? Remove it (constants from registers or loaded per use) and recount the exact outcome.",
    "COMPUTED",
    "Straight-line batch (595 ops) has 183 ops with a 256-bit immediate (167 AND masks, 8 add, 8 xor) over 25 distinct 256-bit constants, plus 160 shifts with 7 distinct counts (16,12,8,7,20,24,25). "
    "No immediates, constants held in registers: zero loop cost when R>=48 registers (Belady, 0 spills), +0.0024 bit at R=40, +0.084 at R=32. "
    "No immediates and NO constant registers (every use a load): +183 loads/batch = +0.3843 bit; shift counts also loaded: +0.6527 bit.",
    ["N"], AM + "; " + DR, "straight-line code of the filed circuit (595 ops, unrolled, SSA order as emitted); 36-bit pitch, 7 lanes; Belady min-spill; machine = loads/stores each 1/638; table of 25 constants costs 800 B of memory (inside the 2^20 headroom of 82,304 B).",
    "The organizer states a register count below 48 (then constants cost loads), or rules that immediates are not offered AND the file has under 40 registers.",
    "Load/store of a constant counted as one op like any word op (M5). The note's remark 'fewer than about 40 registers needs loads and stores' is tightened: with immediates 25 registers give zero spills; with all 25 constants pinned in registers 48 give zero spills.")
rec("U82", "MACHINE.IMM", "MACHINE", "Q3", "immediates",
    "Degrees of freedom / score-optimal value of the immediate set.",
    "COMPUTED",
    "Distinct 256-bit constants = 25 (8 rotation masks pairs 4x2 plus the lane-clean mask REP*0xFFFFFFFF plus 16 folded add/xor immediates of round 0); shift counts 7. Minimum count is fixed by the 4 BLAKE3 rotation amounts and the round-0 constant folding; "
    "score-optimal value = 25 constants, 0 extra ops (every one is a single op with an immediate). Nothing to tune; score sensitivity 0.002409 bit per op per batch.",
    ["N"], AM, "same circuit and pitch as Q2.", "A layout with fewer distinct masks (another pitch) that also keeps 595 ops; none found (pitch sweep in MACHINE.ROT).",
    "Counted from the emitted lines by regex; the number 25 includes the two add and xor round-0 immediates (K+m8 etc.) that differ per G call.")
rec("U82", "MACHINE.IMM", "MACHINE", "Q4", "immediates",
    "Alternatives to the 256-bit immediate and their cost.",
    "COMPUTED",
    "A: constants preloaded once into registers (25 loads at start, 800 B): 0 ops in the loop if R>=48 (50 live incl. 25 constants, Belady 0 spills at 48; +0.0024 bit at 40). "
    "B: load per use: +0.3843 bit. C: build masks by shifts from one all-ones word: +1..2 ops per mask use, worse than A. Best alternative = A, cost 0.",
    ["N"], AM + "; " + DR, "same circuit; 64-register machine assumed only for the 'in-register' variant.",
    "Register count below 48 declared by the organizer.", "C is argued (an op per use), not run. A and B are measured.")

# ================= U83 ROT
rec("U83", "MACHINE.ROT", "MACHINE", "Q2", "rotation cost",
    "Is the 5-op rotation (shr, and, shl, and, or) necessary? Change its price and recount.",
    "COMPUTED",
    "80 variable rotations x 5 ops = 400 of 595 ops (67.2 percent); 16 round-0 rotations fold to constants. Each op per batch is worth 0.002409 bit. A 4-op rotation would be -0.2066 bit, a 3-op rotation -0.4479 bit (hypothetical prices, no such form exists at pitch 36: both masks are needed for r>4, see research/blake3_r3/levers_step_count.md). Lane pitch change recounted with the real tracer: pitch 33 = 684, 34 = 622, 35 = 603, 36 = 595 ops.",
    ["N"], AM, "7 lanes in a 256-bit word, circuit of rho.py build_hash with the pitch patched; same constants folded.", "A 7-lane layout whose rotation costs under 5 ops and adds stay unmasked.",
    "Pitch >= 37 gives 6 lanes (6*37=222; 7*37=259>256) so it is excluded.")
rec("U83", "MACHINE.ROT", "MACHINE", "Q3", "rotation cost",
    "Score-optimal lane pitch (degrees of freedom of the rotation layout).",
    "COMPUTED",
    "Pitch 36 is the optimum for 7 lanes: ops/instance 85.0 (595/7) against 86.1 (603/7, pitch 35), 88.9 (622/7, pitch 34), 97.7 (684/7, pitch 33). Guard bits 4 is the minimum that avoids extra overflow masks (3 internal masks remain). Score difference pitch 35 vs 36: +0.0108 bit.",
    ["N"], AM, "7 lanes; digest feed identity; same loop overhead.", "A proof of tighter lane bounds that removes the 3 internal masks (-3 ops = -0.0072 bit), not shown.",
    "Same result as the ATLAS-style hand count in levers_step_count.md (595); this adds the other pitches as exact counts.")
rec("U83", "MACHINE.ROT", "MACHINE", "Q4", "rotation cost",
    "Alternative lane layouts and rotation forms.",
    "COMPUTED",
    "8 lanes at pitch 32 with SWAR add (6 ops per add): 1095 ops = 136.9 per instance against 85.0 shipped (bound, +0.68 bit). 4 lanes at pitch 64 with a 4-op rotation (shr, shl, or, and): about 515 ops / 4 = 129 per instance (hand estimate, NOT traced), also worse. 7 lanes pitch 36 stays best.",
    ["N"], AM, "256-bit word, no wider words (M5), op price 1/638.", "The organizer prices a wider (512-bit) word as one op (gain about 0.99 bit, a pricing question, see levers_machine.md).",
    "The pitch-64 figure is an estimate and is labelled so; the 8-lane figure uses 6 ops per variable add as a bound (the shipped circuit has 100 adds).")

# ================= U84 CMPBR
rec("U84", "MACHINE.CMPBR", "MACHINE", "Q2", "compare and branch",
    "Is the 4-op stage-1 filter plus 3-op loop control necessary? Change them and recount.",
    "COMPUTED",
    "Score change by stage-1 ops per batch: 2 -> -0.0048, 3 -> -0.0024, 4 shipped 0, 5 -> +0.0024 bit. Loop ops per body of 16: 0 -> -0.00045, 1 -> -0.00030, 3 shipped, 6 -> +0.00045. Prefilter width s1<32 adds one AND per batch: s1=31 +0.00239, s1=16 +0.00255. Main loop share 0.9944; one op per batch = 0.002409 bit.",
    ["N"], AM, "filed ledger, U=16, DP bits 114, stage 2 charged 300 ops per event.", "A 3-op filter form proved correct (see Q4: a grouped filter reaches 2.1 ops per batch).",
    "Filter shipped: add REP*0xFFFFFFFF, and BIT32REP, compare, branch (z0 is already masked, so no AND for s1=32).")
rec("U84", "MACHINE.CMPBR", "MACHINE", "Q3", "compare and branch",
    "Score-optimal unroll U (degrees of freedom of the loop control).",
    "COMPUTED",
    "Code is charged 39 B x 600 ops per batch copy (374,400 B at U=16). Table 589,824 + counters 2,048 leave room for U=19 (memory 1,036,472 B <= 2^20): delta -0.0000709 bit. U=20 exceeds 2^20 (1,059,872 B): +0.0154. U=8 +0.00045; U=1 +0.0067; U=32 +0.354; U=64 +0.994.",
    ["N"], AM, "code size model 39 B per op x 600 ops per batch (derived from the filed 374,400 B); table 32 B per key, 18,432 keys.", "Code bytes per op declared differently by the judge.",
    "The 39 B per op is inferred from the filed figure 374,400 = 16 x 600 x 39, not read from a source; gain is far below any filing threshold.", lever=True, gain=0.00007, basis="T")
rec("U84", "MACHINE.CMPBR", "MACHINE", "Q4", "compare and branch",
    "Alternatives to testing the DP filter on every batch.",
    "COMPUTED",
    "GROUPED FILTER: AND the 16 flag words u_i = z0_i + REP*0xFFFFFFFF of one unrolled body, then one AND with BIT32REP, one compare, one branch: 16 adds + 15 ands + 1 + 2 = 34 ops per body instead of 64. Per body 9557 against 9587 ops: delta -0.004496 bit (U=16), -0.004615 bit (U=19). "
    "Stage-2 then recomputes the body from its 8 preserved inputs: 16 x 595 extra ops per event costs 5e-8 relative (delta -0.004496 including it). Logic tested: 200,000 random packed groups (k=2,4,16, zeros planted), 0 mismatches against 'some lane low 32 bits zero'. "
    "Registers: 25 + 8 preserved + 1 accumulator = 34 with immediates; without immediates (constants in registers) 56 for zero spills (Belady), 48 gives 4 stores.",
    ["N", "E"], AM + "; " + CT + "; " + DR, "filed circuit and ledger; DP rule and table unchanged (a lane that passes a DP inside the body is replayed from the preserved inputs; it wastes at most 15 lane-steps per DP, about 2^14 x 15 steps).",
    "Whole program built and its n=22/32 experiment passing with the grouped filter; or the judge reading the replay as an uncharged cost.",
    "NOT built end to end: only the filter logic and the ledger arithmetic are tested. Needs the stage-2 replay coded (about 20 lines in rho.py search) and the proof sections 3.3 and Lemma 2 restated. Stacks with the other small levers (see GENERIC cells); safe combination -0.0068 bit.",
    lever=True, gain=0.0045, basis="T")

# ================= U85 MEMTRAF
rec("U85", "MACHINE.MEMTRAF", "MACHINE", "Q2", "memory traffic (loads / stores)",
    "Is a register-resident main loop necessary? Reduce the register count and recount the exact loads and stores.",
    "COMPUTED",
    "Peak live values of the emitted 595-op order = 26 (8 inputs included); Belady optimal spilling: 0 spills at R>=28 (25 suffices), R=24: 1 store + 2 loads = +0.0072 bit, R=20: 6+10 = +0.0380, R=16: 17+22 = +0.0909, R=12: 35+42 = +0.1743 bit. "
    "With the 25 constants also held in registers: R=48 -> 0 spills, R=40 -> 1 load (+0.0024), R=32 -> 11 stores + 25 loads (+0.0841). The note's 'about 40 registers' is therefore a safe over-statement (true threshold 25 with immediates, 48 without).",
    ["N"], AM + "; " + DR, "emitted instruction order of build_hash; inputs i8..i15 live-in, 8 digest words live-out (feed to next batch is identity); one load or store = 1/638 each.",
    "The organizer states fewer than 25 registers, or counts register-to-register moves.",
    "Loop-carried outputs assumed to land in the registers that the next copy reads (note says no moves charged).")
rec("U85", "MACHINE.MEMTRAF", "MACHINE", "Q3", "memory traffic (loads / stores)",
    "Score-optimal register count (degrees of freedom of the schedule).",
    "COMPUTED",
    "Zero-spill minimum = 25 registers in the emitted order (Belady); a greedy minimum-live reschedule of the same DAG gives peak 26, no better. So the schedule is already at its minimum for practical purposes; the score cost of traffic in the shipped program is exactly 0 at any R>=28.",
    ["N"], AM, "same DAG; no instruction duplication.", "A scheduler that gets under 25 live values (only matters if R<25 is declared).",
    "Greedy reschedule is a heuristic upper bound on the true minimum, not a proof of optimality.")
rec("U85", "MACHINE.MEMTRAF", "MACHINE", "Q4", "memory traffic (loads / stores)",
    "Alternatives: keep constants in registers, preserve group inputs, table accesses.",
    "COMPUTED",
    "Constants pinned in registers: needs R>=48 for zero traffic. Grouped filter (MACHINE.CMPBR Q4) adds 9 live values: with immediates 34 registers; with constants pinned plus the 2 filter constants R=56 gives 0 spills, R=48 gives 4 stores (+0.0096 bit), R=40 gives 11 stores + 1 load (+0.0286). "
    "Table/recovery traffic is charged in the filed ledger (events 700 ops each, 18,432 events: 1.03e9 ops, negligible against 2.9e40).",
    ["N"], DR, "same DAG plus permanent extra values.", "Fewer than 56 registers together with no immediates and the grouped filter.",
    "Third row of d_regs.json (const_regs False) counts every constant use as a load and is not a meaningful scenario; ignore it.")

# ================= U86 DPFRAC
rec("U86", "GENERIC.DPFRAC", "GENERIC", "Q2", "distinguished-point fraction",
    "Is d = 114 necessary? Change it and recount the exact score (time plus memory term).",
    "COMPUTED",
    "Score by integer d (table 32 B x tmax, tmax scaled 2^(114-d)): d=110 128.325 (mem 9.8 MB), 111 127.380, 112 126.484, 113 125.6728 (mem 1,556,096 B, +0.5642), 114 125.10856 (966,272 B), 115 125.11908 (+0.01052), 116 +0.0313, 117 +0.0720, 118 +0.1502. "
    "Expected finished trails at halt 16,364.7; P(table full at 18,432) = 8.6e-57, i.e. the 12.6 percent table margin is far larger than needed. Recovery is 0.5614 percent of the ledger and scales with 2^d.",
    ["N"], BG, "filed ledger formulas with L=2^d; INFLIGHT, cutloss, kappa as filed; success proof not re-derived for other d.",
    "A table-entry smaller than 32 B or a different memory rule.", "d below 114 is blocked by the memory term (slope 0.6 bit of memory per bit of d against 0.008 bit of recovery).")
rec("U86", "GENERIC.DPFRAC", "GENERIC", "Q3", "distinguished-point fraction",
    "Score-optimal DP density; is the density free to be non-integer?",
    "COMPUTED",
    "The memory term pins d at the boundary: use the whole 2^20 budget. Table room: (2^20 - 374,400 - 2,048)/32 = 21,004 keys. Non-integer density 2^-113.70 (DP = low 113 bits zero plus a comparison of the next bits, done only in stage 2, 0 extra main-loop ops) gives mean 20,147 finished trails and P(table full) below 1e-9: "
    "delta -0.001982 bit (1e-6 tail: d=113.688, -0.002057; 1e-12: d=113.711, -0.001920). With 25 B entries (key 8 + t 2 + length 15 B) 26,885 keys fit: d=113.34, delta -0.003894 bit.",
    ["N", "E"], BG, "filed ledger; INFLIGHT=28 L, cutloss 1.5e-4, kappa 12 as filed (their units shrink with L, which is part of the gain); entry layouts per note (32 B) or compressed (25 B, not built).",
    "Judge rejects non-integer density or the compressed entry; or a lower table bound enters via the proof's Lemma 2.",
    "Requires restating proof Lemma 2 for density 2^-113.7 (trail count 20.1k instead of 16.4k) and the memory ledger. Entry width of 25 B follows from length < 12 x 2^114 (15 bytes) and t < 2^16 (2 bytes) plus an 8 B key; unbuilt.",
    lever=True, gain=0.00198, basis="T")
rec("U86", "GENERIC.DPFRAC", "GENERIC", "Q4", "distinguished-point fraction",
    "Alternatives to distinguished points (cycle finding) and to the 32-bit prefilter.",
    "SAMPLED",
    "Random mappings n=18, 300 runs: 39 percent quantile of evaluations over sqrt(2N): Floyd (3 evals per step) 1.611, Brent detection only 1.094 (recovery of the pair excluded), exact rho length mu+lambda 0.678, filed DP search q = 0.705 sqrt(2N). Floyd costs +1.19 bit, Brent at least +0.63 bit against DP. "
    "Prefilter width: s1=32 is the only value with no extra AND; s1=31 +0.00239 bit, s1=16 +0.00255 bit.",
    ["N", "Z"], BG, "plain random mappings (numpy), not the BLAKE3 chain; time unit = evaluations, same cost per evaluation.", "A cycle-finding variant that finds the pair in under 0.75 sqrt(2N) evaluations at 39 percent.",
    "300 runs: quantile standard error about 0.04 on the Floyd/Brent figures; the DP figure is the filed formula. Sign and size of the gap are far outside that.")

# ================= U87 CHAINLEN / SUCC
rec("U87", "GENERIC.CHAINLEN", "GENERIC", "Q3", "trail (chain) length",
    "Score-optimal age cap kappa and in-flight allowance (degrees of freedom of the trail length rules).",
    "COMPUTED",
    "Cut-loss allowance scaled as 2.034 x kappa e^-kappa (filed: 1.5e-4 at kappa 12 over mean 7.37e-5). Delta by kappa: 6 +0.0399, 8 +0.00495, 9 +0.00101, 10 -0.00024, 11 -0.00035 (best), 12 0, 13 +0.00055, 14 +0.00117, 16 +0.00249, 20 +0.00517 bit. "
    "In-flight allowance 28 L (P(Gamma(7)>28)=5.8e-7 under exponential ages): 20 L -0.00070 (tail 2.6e-4), 15 L -0.00114 (tail 7.6e-3), 7 L (mean) -0.00184 bit.",
    ["N"], BG, "filed ledger; success proof's loss terms taken as the formulas; tails assume 7 independent exponential residual ages.",
    "The proof's Lemma 2 restated with kappa=11 / a smaller in-flight bound and still spending under the 1.65e-3 margin.",
    "kappa=11 gain (0.00035) and in-flight gains eat into the same 1.65e-3 probability margin as GENERIC.SUCC, so they do not add on top of the lambda gain without a joint check.",
    lever=True, gain=0.00035, basis="T")
rec("U87", "GENERIC.CHAINLEN", "GENERIC", "Q4", "trail (chain) length",
    "Alternatives to the age cap for bounding recovery and trail length.",
    "COMPUTED",
    "No cap (kappa 20 stands in): +0.00517 bit and an unbounded recovery that cannot be charged. Cap by halting instead of cutting: same arithmetic as the kappa sweep. Fixed-length trails (no DP): detect only merges at equal depth, so they miss collisions (argued, not run). "
    "Brent/Floyd instead of DP: see GENERIC.DPFRAC Q4 (+0.63 / +1.19 bit).",
    ["N", "Z"], BG, "filed formulas.", "A detection scheme for unequal-depth merges without DP.",
    "Fixed-length trails argument: end(A)=f^(l-i)(m), end(B)=f^(l-j)(m) differ when i != j; not simulated.")
rec("U87", "GENERIC.SUCC", "GENERIC", "Q3", "success probability",
    "Score-optimal lambda (degrees of freedom of the success target).",
    "COMPUTED",
    "Floor: 1-e^-lambda = 0.39 gives lambda 0.494296; filed lambda 0.497 gives P 0.391647 (margin 0.001647, of which 1.2e-4 is spent on losses). Delta: lambda for P=0.39+1.2e-4 (0.49449) -0.003621 bit; for 0.39+3e-4 -0.003194; for 0.39+1e-3 -0.001533. "
    "Together with in-flight 8 L and recovery extra 29: -0.005947 bit. Time depends on P as 0.5 log2(-ln(1-P)): P 0.30 -0.237, 0.45 +0.132, 0.50 +0.238, 0.63 +0.497 (P below 0.39 is not allowed by the cost model).",
    ["N", "E"], BG, "filed ledger; loss terms as filed; minimum_success_probability 0.39 from cost-models/collision-frontier-v5.json.",
    "The note's 0.0015 safety margin for an H1 rate deficit is declared unneeded (a 0.46 percent rate deficit already breaks 0.39).",
    "The margin is deliberate: removing it trades 0.0036 bit for robustness against H1. Owner decision.",
    lever=True, gain=0.0036, basis="T")
rec("U87", "GENERIC.SUCC", "GENERIC", "Q4", "success probability",
    "Alternative check: measured success of the shipped search at small widths.",
    "SAMPLED",
    "rho.search with plan(n): n=22, 1500 attempts: 697 pairs found (0.4647; 87 budget halts); n=32, 40 attempts: 17 (0.425, standard error 0.078). Every pair verified x!=y and f(x)=f(y). Both above 0.39 but dominated by finite-size slack (28 L is 11 percent of q at n=32, 0.17 percent at 256), so this does not test the 256-bit margin.",
    ["Z"], CT, "shipped rho.py search and plan, n=22 and 32, seeds fixed in c_tests.py.", "A test at width where 28 L / q is under 1 percent (needs n>=64: about 1e9 batches).",
    "Earlier T3 (4000 attempts n=32: 0.443 against 0.4535 ideal) is consistent; this adds n=22 only.")

# ================= U88 ATT
rec("U88", "GENERIC.ATT", "GENERIC", "Q2", "attempts / restarts / amplification",
    "Is the single attempt necessary? Use a attempts at lambda/a each and recount.",
    "KILLED",
    "a=1 125.10856; a=2 +0.4986 bit; a=3 +0.7909; a=4 +0.9984; a=8 +1.4993 (ideal 0.5 log2 a). Each attempt repays in-flight, stage 2 and init; recovery once. More attempts only cost time at fixed success 0.39.",
    ["N"], BG, "filed ledger, P_total = 0.39165 (lambda total 0.497).", "Never at P fixed to 0.39.",
    "Closed by number: killed for a>1.")
rec("U88", "GENERIC.ATT", "GENERIC", "Q3", "attempts / restarts / amplification",
    "Score-optimal attempt count and success target.",
    "COMPUTED",
    "a=1 with lambda at the floor of P=0.39 is optimal; see GENERIC.SUCC Q3 for the margin (up to -0.0036 bit). Time vs target P: 0.30 -0.237, 0.39 -0.0039 (exact floor), 0.45 +0.132, 0.5 +0.238, 0.63 +0.497.",
    ["N"], BG, "minimum_success_probability 0.39 of the cost model.", "The organizer lowers the minimum success probability.", "Same arithmetic as GENERIC.SUCC.")
rec("U88", "GENERIC.ATT", "GENERIC", "Q4", "attempts / restarts / amplification",
    "Alternatives: restarts after table-full / cut trails, stored collision, continuing run.",
    "COMPUTED",
    "No restart is used: a table-full halt has probability 8.6e-57 and a stage-2 halt about 0; one fresh 256-bit word (1 op). A stored collision or continuing one run to higher P only raises q: P 0.45 costs +0.132 bit over the floor. 'Success amplification' is listed as charged time in the cost model.",
    ["N", "Z"], BG, "filed program.", "A rule that scores expected rather than budgeted time (then all halts would be re-costed).", "Expected-time scoring is not what the filed claim or the judge uses.")

# ================= U89 RECOV
rec("U89", "GENERIC.RECOV", "GENERIC", "Q2", "recovery of the colliding pair",
    "Is the recovery charge of 64 extra ops per batch necessary? Recount at the needed extra.",
    "COMPUTED",
    "Recovery is 0.5614 percent of the ledger (1.6424e38 of 2.9258e40 ops, capr = 12 x 2^114 + 2^48 batches at PH+64 = 659). The proof's own count of the extra is 29 (8 shr + 8 xor + 7 or + 1 and + compare + branch + 3 loop). Extra 29: -0.000430 bit; 30 -0.000418; 32 -0.000393; 40 -0.000295. "
    "The earlier ruling (77715f8b) refuted the first package for omitting at least 4 ops per batch; the filed extra of 64 already includes a 35-op margin.",
    ["N"], BG + "; research/blake3_r3/ruling_77715f8b/reports/tracks/blake3-pareto/judge-dossier.json", "filed ledger; capr as filed.", "A judge ruling that 29 ops is itemised and enough.",
    "Gain is smaller than the risk that one miscount re-triggers the lane_cost/F1 finding; not recommended on its own.", lever=True, gain=0.00043, basis="T")
rec("U89", "GENERIC.RECOV", "GENERIC", "Q3", "recovery of the colliding pair",
    "Score-optimal charge: worst-case split of the recovery walk.",
    "COMPUTED",
    "Alignment steps (la-lb) need one lane and no compare: PH+3 = 598 ops each; matching steps (lb+1) PH+29 = 624. With la = lb+(la-lb) <= capr the worst case is all matching: capr x 624. Savings against 659: 35 ops x capr = 0.0295 percent of the ledger = 0.000430 bit. The cap capr itself (kappa) is the free parameter: see GENERIC.CHAINLEN Q3 (kappa 11: -0.00035).",
    ["N"], BG, "proof 3.3 itemisation of 29 ops.", "The two phases counted separately in a restated proof.", "Per-op itemisation relies on the note/proof's 29; not recounted from code.")
rec("U89", "GENERIC.RECOV", "GENERIC", "Q4", "recovery of the colliding pair",
    "Alternatives: parallel or checkpointed recovery, scalar compression.",
    "COMPUTED",
    "The walk is sequential (x -> f(x)), so 7 lanes cannot split it; a scalar compression costs 638 ops against 595 for the 7-lane batch used with 1-2 lanes, so the batch is cheaper. Checkpoints need memory: headroom 82,304 B holds 2,572 entries of 32 B for 18,432 trails, which cannot shorten the walk of the one trail pair in general. No alternative beats the shipped walk.",
    ["N", "Z"], BG, "filed recover().", "A cheap way to locate the merge without walking from the start.", "Argument by counts, no program run for checkpoints.")

# ================= U90 SETUP
rec("U90", "GENERIC.SETUP", "GENERIC", "Q2", "setup / table build",
    "Is the setup charge (2,000 ops) necessary? Change it and recount.",
    "COMPUTED",
    "Setup 2000 ops = 3.135 units = 2^1.65 of preprocessing (claim 2^2). Replacing 2000 by 0 or by 1e9 ops moves time_log2 by under 1e-31 bit (ledger total 2.9258e40). The setup is irrelevant to the score; only its itemisation matters to the judge (1 random word, 7 starts, counters, folded constants = 287+25+336 +1 per the filed comment).",
    ["N"], BG, "filed ledger.", "A judge finding that setup is itemised wrongly by more than the 2^2 preprocessing claim allows (2^2 = 4 units = 2552 ops).", "Calculation: log2(2000/638)=1.65.")
rec("U90", "GENERIC.SETUP", "GENERIC", "Q3", "setup / table build",
    "Score-optimal table size (halt at 18,432 keys) and setup parameters.",
    "COMPUTED",
    "Needed table: mean 16,364.7 finished trails at halt, so 18,432 gives P(full)=8.6e-57; 17,000 would give about 1e-7 failure; no gain below 2^20 bytes unless the freed room is used for a smaller d (GENERIC.DPFRAC Q3: -0.00198 bit at 21,004 keys). Stage-2 halt e2max = 2 x mean; events cost 1.03e9 ops.",
    ["N"], BG, "filed formulas.", "Memory rule changed.", "17,000 keys figure from Poisson tail by log-gamma sum, not a proof of the table bound in the proof's Lemma.")
rec("U90", "GENERIC.SETUP", "GENERIC", "Q4", "setup / table build",
    "Alternatives: compress table entries; claim preprocessing exactly.",
    "COMPUTED",
    "Entry 32 B -> 25 B (8 B key, 2 B trail id, 15 B length) frees room for 26,885 keys and a density 2^-113.34: -0.003894 bit (GENERIC.DPFRAC Q3). Claim preprocessing_log2 as 1.65 instead of 2: no score effect (preprocessing is inside time).",
    ["N", "E"], BG, "filed ledger.", "Entry layout rejected by the judge.", "25 B layout not built.", lever=True, gain=0.0039, basis="T")

for unit, items in U.items():
    uid = f"blake3-r3-{unit}"
    d = os.path.join(OUT, uid); os.makedirs(d, exist_ok=True)
    for name, rec_ in items:
        json.dump(rec_, open(os.path.join(d, name + ".json"), "w"), indent=1)
print(sum(len(v) for v in U.values()), "records")
