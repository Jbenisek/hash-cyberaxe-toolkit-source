# const x alg on the counter base (GAPS section 2 row 1): which pin is best for the counter path?

Folder `research\newpaths\untried\const_alg`. Run 2026-10-09 23:46 to 2026-10-10 01:04 (WSL clock). Research only:
no yukon command, nothing filed or posted, no network, `workspace\.key` not opened, nothing written outside this
folder (the atlas scripts were imported unchanged with their output paths pointed here). At most 2 CPU processes of
mine at a time, every run under 20 minutes, kissat always with `--time=N`, only my own processes (none had to be
stopped; none left running). No tool call or command was refused or stopped.
Labels: **COMPUTED** = run here (file named), **DERIVED** = follows from a named source or a short argument,
**GUESS** = judgement, not checked. Scores use the CENSUS one formula at margin 2.0 (board's 1.4 in brackets).

## 0. Verdict

1. **New best counter pin: N6a, a delta-6 pin found here by the night's pin solver rerun with the counter
   objective.** Its beta 13140f5f (k 15) has part 18,939,904.00, so C_ctr >= 18,939,904 x 2^15 = 2^39.175 ->
   **82.80** (82.28), **2.08 bits better than H8** (84.88) and 4.00 better than L16a (86.80). A second beta, 133c0f5f
   (k 16, 6,232,064.00), alone gives 83.40.
   Labels: pin valid in plain arithmetic, part from two different calculators, kissat SAT with its model checked in
   plain arithmetic: COMPUTED. Score: DERIVED. Cost per trial 6.5 ops (H8's machine): GUESS. **The counter
   construction itself was not built or run with N6a** (section 5); that is the first thing to check.
2. **Among the pins that were already scored (the question as asked): H8 is best, 84.88** (84.96 with its sub-class
   C15, as CENSUS); COMPUTED max, DERIVED score, GUESS ops.
3. **Yes, two of them beat L16a: L4b and L8b, 85.93 each** (85.41), 0.87 bit better than L16a. Both COMPUTED here
   (per-beta files made with the atlas pipeline, every beta with k <= 18 settled); DERIVED score; GUESS ops.
   L4b: beta 907df8c2, k 15, part 2,162,688.00. L8b: beta 82d58088, k 10, part 69,206,016.00. L4b is weak at the
   root (its k <= 14 recount found nothing; all its mass sits at k 15 and 17), the reordering GAPS K4 predicted.
   The third pin computed, L8c, does not: 86.93.
4. Pin solver, delta 8: one run UNKNOWN (counter bound 88, 1,080 s); one run SAT at bound 90 -> new pin N8a, but its
   returned beta is weak: 92.57 (COMPUTED part, two calculators). Its other betas were not counted.

Each new pin, and each of L4b and L8b on the counter path, would be its own entry (GAPS: "Any new pin is its own
entry"). Nothing is filed; the owner decides.

## 1. Which scored pins have a per-beta file (COMPUTED from census `pins.py`)

- With one (8): H8, B, L4a, L6a, L6c, L10a, L12a, L16a.
- Without one (11): L8b (screened only), L8c, L8d, L4b, L4c, L6b, L10b, L12b, L16b, L16c, L120a. L4b has an empty
  file (`paths\counts\L4b_parts.txt`: its k <= 14 recount found no SAT beta).
- Made here: L4b, L8b, L8c (the three strongest missing pins), and N6a (new) -> `counts\NAME_parts.txt`.

## 2. Ranking by the counter objective C_ctr = max over beta of part x 2^k

Score = log2(0.5) + 128 - log2(C_ctr / 2.0) + log2(6.5 / 430) + 0.02 (penalty 0). Calibration reproduces CENSUS
exactly: H8 sub-class 84.96, L6c 87.14, L16a 86.80 (COMPUTED, `rank_counter_out.txt`). Every max is a LOWER BOUND
where SAT betas are uncounted (last-but-one column).

| rank | pin | best beta | k | part | log2 C_ctr | counter score | coverage of the max | label |
|---|---|---|---|---|---|---|---|---|
| 1 | **N6a** (new) | 13140f5f | 15 | 18,939,904.00 | 39.175 | **82.80** (82.28) | 5 of 17 SAT betas (k <= 16) counted | COMPUTED here / DERIVED |
| 2 | H8 | 18b0e098 | 11 | 71,698,432.00 | 37.095 | **84.88** (84.36); sub-class C15 84.96 | atlas recount to k 21; the FULL count's remainder, 1.585, cannot reach it | COMPUTED / DERIVED |
| 3 | **L4b** | 907df8c2 | 15 | 2,162,688.00 | 36.044 | **85.93** (85.41) | settled k <= 18 | COMPUTED here / DERIVED |
| 3 | **L8b** | 82d58088 | 10 | 69,206,016.00 | 36.044 | **85.93** (85.41) | settled k <= 18 | COMPUTED here / DERIVED |
| 5 | L16a | f990e10a | 14 | 2,355,712.00 | 35.168 | 86.80 (86.29) | LX16: 110 betas to k 18, SAT betas left | COMPUTED (file) / DERIVED |
| 6 | L8c | 08b04c89 | 10 | 34,630,854.00 | 35.046 | 86.93 (86.41) | settled k <= 17 | COMPUTED here / DERIVED |
| 7 | L6c | e91e11a6 | 14 | 1,863,680.00 | 34.830 | 87.14 (86.63) | k <= 14 filter only | COMPUTED (file) / DERIVED |
| 8 | B | 481c6852 | 10 | 14,038,016.00 | 33.743 | 88.23 (87.71) | night's k <= 14 count, class e7c1815f | COMPUTED (file) / DERIVED |
| 9 | L6a | 48157e12 | 13 | 1,079,123.38 | 33.041 | 88.93 (88.42) | LX6: complete to k 15; 450 SAT betas k 16-29 uncounted | COMPUTED (file) / DERIVED |
| 10 | L12a | b9748048 | 12 | 344,560.00 | 30.394 | 91.58 (91.06) | settled k <= 14 | COMPUTED (file) / DERIVED |
| 11 | L4a | 81384e44 | 10 | 1,370,240.00 | 30.386 | 91.59 (91.07) | 271 SAT betas uncounted | COMPUTED (file) / DERIVED |
| 12 | N8a (new) | 8f1e3580 | 13 | 86,604.00 | 29.403 | 92.57 (92.06) | returned beta only | COMPUTED here / DERIVED |
| 13 | L10a | 89139496 | 13 | 80,256.00 | 29.292 | 92.68 (92.17) | k <= 14 filter only | COMPUTED (file) / DERIVED |

H8's whole-class max is the FULL count's own beta: the 14 SAT betas its file lacks add up to 1.585 in H8_count.txt,
and 1.585 x 2^31 < 2^32 (DERIVED). L4b and L8b give the same integer, 70,866,960,384 = 33 x 2^31; both parts were
printed earlier by two other night tools (cand_exact_lx.txt, lx_totals.txt), so this is a coincidence of the counts.

The eight pins still without a per-beta file, by their best SCREENED beta (lower bounds; COMPUTED from the night's
screens named in ATLAS Table 1b, k computed here): L8d 90.82, L16b 91.12, L120a 91.22, L12b 91.86, L4c 92.80,
L6b 93.03, L16c 93.19, L10b 94.97. None reaches L16a on these figures (`rank_counter_out.txt`, Table 2).

## 3. The three per-beta files for missing pins (COMPUTED)

Chosen by the screened counter lower bound: L4b 85.93, L8b 85.93, L8c 86.93 (next: L8d 90.82). Steps per pin
(`run_pin.sh`, 2 processes): filter every beta with k <= 18 (h8_pair_list), kissat on every beta with a passing
outcome plus a sample of the others, the calculator (h8_pair_calc_batch, sha256 29fd2b3d0ef51605 = the atlas's
`calculator.sha`) on every SAT beta, report.

| pin | betas k <= 18 | with a passing outcome | SAT (models checked) | counted | settled for | R found | wall time |
|---|---|---|---|---|---|---|---|
| L4b | 48,898 | 3,162 | 4 (4) | 4 | k <= 18 | 2,387,968.01 (screen 2,162,688) | 26 s + 150 s |
| L8b | 30,867 | 2,631 | 16 (16) | 16 | k <= 18 | 90,794,241.61 (screen 74,928,128) | 537 s |
| L8c | 48,046 | 9,759 | 86 (86) | 61 | k <= 17 | 36,988,512.97 (screen 36,600,988) | 1,097 s |

Filter samples (betas without a passing outcome): all UNSAT. The betas that carry each maximum went through no
random-subset branch (exact enumerations). Side result, root path: L8b's R >= 90.79 million gives about 95.78
(DERIVED, CENSUS root ops 7.7 a GUESS), 0.28 below CENSUS's screened 96.06.

## 4. Pin solver with the counter objective, deltas 8 and 6

Tool: `trailmin5_ctr.py`, a copy of the night's pin solver `research\night\main\trailmin5.py` (the solver behind
cand_exact_lx.txt and R17) with one change of objective. Its cost is the number of active bit positions at six
additions, A1 (c1: x5) + A4 + A5 + A3 + A6 + A7, and A1 is exactly the beta's weight k (beta = ROR(x5, 12)). On the
counter path the beta is prescribed, so the bound now covers A4..A7 only ("counter cost"); A1 is bounded on its own
(k <= 24). Every (D3, D11) already known for the length XOR is excluded (night's trail5_lx.log, the server's
trail5_server.log, pins.tsv, earlier runs here), so every answer is a NEW pin. kissat --sat --time=1080.
Calibration from the night's own lines (DERIVED, cost - A1): L8c 88, L8b 88, H8 89 (its search beta 18b0e098 is also
its counter-best beta), L6c 91.

| run | family | counter bound | result | time |
|---|---|---|---|---|
| s51 | delta +-8, length XOR 8 (55/63), W13 top byte 0 | 88 | UNKNOWN | 1,080 s (limit) |
| s61 | delta +6, length XOR 6 (57/63) | 90 | **SAT: N6a**, counter cost 88, full cost 103, k 15, class 2^16 | 529 s |
| s52 | delta +-8, length XOR 8 (55/63), W13 top byte 0 | 90 | SAT: N8a, counter cost 90, full cost 103, k 13, class 2^18 | 795 s |

**N6a** = (X3, X7, X11, X15, W4, W13) = (3d55e40c, ca84e63c, 4fff43fc, a7882079, 782535ba, 3fbb7ffd); D3 c972a031,
D11 bf0ab0ef, delta 00000006, Y3 9b472fe7, Y11 e035a78c, eta a031fb8f. Checks, each COMPUTED:
- plain arithmetic (`paths_lib.pin_outputs`, length XOR 6): a valid pinned call, b and d outputs equal, delta 6, Y3,
  D3, Y11, D11 as returned; class (Y3 + Y4) AND 7b8fa031 = 190e8000 valid, 2^16 members; 13140f5f is a valid beta
  of D11 with k 15. Length pairs 57/63, 58/60, 56/62, 59/61 take delta 6 with W13 free, as for L6c.
- part of 13140f5f = 18,939,904.00 from TWO calculators: the atlas's h8_pair_calc_batch (`exact_beta.py`, then again
  inside the pipeline) and the night's night_pair_calc (`cross_night.sh`, sha256 927921564e4cb7e5, one thread, its
  EXACT-E1 line); no random-subset branch, no formula fallback (`exact.log`).
- atlas pipeline on N6a (`pins_new.tsv`; `run_pin.sh N6a 16`, then `n6a_more.sh`): 18,829 betas with k <= 16, 4,315
  with a passing outcome, 17 SAT (17 models right in plain arithmetic), filter sample 300/300 UNSAT (run_pin 1,095 s
  in all). The calculator is slow on this pin: 1 beta counted in run_pin's 682 s step (313c0f55 then held the only
  process to the limit) and 4 more in n6a_more's 480 s, nearest to 13140f5f first; one process each time. Counted: 13140f5f (k 15) 18,939,904.00; 133c0f5f (k 16) 6,232,064.00; 31140f5f (k 15) 434,176.00;
  133c0f55 (k 14) 6,533.00; 331c0f5f (k 16) 142.50. R >= 25,612,819.5, settled only for k <= 13.
- Root, for comparison: R >= 25.6 million -> about 97.61 (DERIVED, root ops 7.7 a GUESS), already better than every
  delta-6 pin in CENSUS (L6a 99.82, L6c 101.37).

**N8a** = (880ee512, 6f67d2f1, bfbe6214, fba72e9e, 688947f8, 00bc6401); D3 aac82f8d, D11 5d37f74f, delta fffffff8,
Y3 aa9c4839, Y11 f2a00058, eta 30f35548; valid in plain arithmetic (COMPUTED), W13 top byte 0 (fits 55/63). Returned
beta 8f1e3580 (k 13): part 86,604.00 from both calculators (COMPUTED) -> 92.57. Its counter cost 90 overstated it by
about 8.6 bits, while N6a's 88 was within 0.8 bit: the solver's cost is a loose guide, an exact count must follow
every answer (DERIVED from these two cases and the calibration above).

## 5. What could not be tested, plainly

- **The counter construction with N6a was not built.** CENSUS checked the counter lever on 10 pin/pair cases (L6c at
  57/63 and 62/64 among them, 300/300, beta forced every time); N6a, L4b and L8b were not run through census
  `construct.py` here (outside this brief's reading list). This is the first check before N6a's 82.80 means anything.
- **Cost per trial.** Every counter score uses H8's counted counter machine, 6.5 ops (GUESS for every other pin, as
  in CENSUS). N6a and L4b force a 15-bit beta cube against H8's 11: whether that costs the same was not checked.
- **Heavier betas and unfinished betas.** N6a: 12 SAT betas with k 14-16 not counted, nothing above k 16 examined.
  L4b, L8b: nothing above k 18; L8c: 25 SAT betas at k 18 not finished; N8a: only its returned beta. Older files:
  L6c and L10a stop at k <= 14, L16a and L4a have uncounted SAT betas. These maxima can only go up.
- **Classes.** Only each pin's returned class was used; no sub-class sweep (as H8's C15) for any pin here.
- **Search breadth.** Three solver runs in all (one UNKNOWN). Delta -6, delta 2, 4, 16 and other seeds or bounds
  were not run under the counter objective; N6a came in 529 s, so more runs look cheap (GUESS).
- **Trust.** One solver (kissat 4.0.3) and one encoding (h8_sat.py) for SAT/UNSAT, no proof certificates; two
  calculators agree on the parts that carry the result; double precision.
- **Process notes.** The two s51/s61 runs appended to `pinctr.log` at the same instant and the s51 header line was
  lost (mounted research volume appends are not atomic); its result line survived, and `pinctr.sh` now writes a per-run file first.
  A seconds-long Windows parse (`rank_counter.py`) ran once beside the 2-process count. Another agent's kissat job
  (folder `untried\b3-trail`) shared the machine; it was not touched.

## 6. Files (this folder)

| file | what | run |
|---|---|---|
| rank_counter.py -> rank_counter_out.txt, rank_counter.csv | the ranking (sections 1, 2; Table 3 = new pins) | `python -B rank_counter.py` (Windows, seconds) |
| ctr_count.py, run_pin.sh, queue1.sh, n6a_more.sh | atlas pipeline (research\paths, imported unchanged) with outputs here | `wsl -d Ubuntu -- setsid -w bash .../queue1.sh` |
| counts\NAME_parts.txt, NAME_count.txt, NAME_sat_betas.txt, NAME_filter.txt | per-beta files and reports: L4b, L8b, L8c, N6a | - |
| trailmin5_ctr.py, pinctr.sh, queue2.sh, pinctr.log, scratch\pinctr_*.out | pin solver with the counter objective | `bash pinctr.sh LX DELTA TOP0 BOUND MAXK SEED TIMEOUT` |
| pins_new.tsv | N6a and N8a in the atlas's pins.tsv format | - |
| exact_beta.py, exact_new6.sh, exact_new8.sh, cross_night.sh, exact.log | both calculators on the returned betas | - |
| status.txt, pids.txt, run.err | one line per step, own PIDs, errors (empty) | - |
| env_check.sh, peek.sh, peek2.sh, leftover.sh | read-only checks | - |
| scratch\ | raw filter, solver and calculator output | - |
