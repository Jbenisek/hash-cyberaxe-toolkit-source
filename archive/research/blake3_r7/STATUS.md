# blake3 round 7 (pareto, full rounds) - first entry B3R7 - STATUS (2026-10-15, Sonnet agent)

STAGED, NOT SUBMITTED. Needs the owner's go, then `bash research/launch/submit_pareto_b3r7.sh` (refuses if a staged file or dependencies.json changed, or if a6ee439c / any dependency is not in our submissions list).

## Result (all from the program: bsrho.py --ledger, appA.py agrees)
- time_log2 **125.05397** (N = 64,910,179,912,936,312,329,273,318,889,044,979,031,328; unit C(7) = 1470 from the lane contract `pareto_candidate.py --family blake3 --rounds 7 --show-contract`; certificate 2^12505396 * 1470^100000 <= N^100000 < 2^12505397 * 1470^100000).
- memory **1,912,272 B = 2^20.86686** (claim memory_log2_bytes 20.86686). Above 2^20: the straight-line program (45,974 gates/step, 48,758 instructions x 36 B = 1,755,288 B) does not fit in 2^20 (portkit's "FIT FAIL"). The lane's scalar policy is time_log2 + max(0, memory_log2_bytes - 20), so the entry pays 0.86686 bit: scalar score 125.92083. Setup phase 1,874,152 B.
- Plan (re-optimised for the sum time + memory term, scan in proof Section 7 and note): table 11,500 entries x 10 B, Tp 161, B = 1.3808e36, c = 13 L, one cut at most, P_lower 0.39000 (Lemma 2 of b4d, `_lossq`/`_b256`). Scan (entries: time + memory term): 3000: 126.182; 6000: 125.967; 9000: 125.927; 11500: 125.921 (min); 14000: 125.924; 20000: 126.012.
- Not found / not built: a rolled round body (loop over rounds + message-index tables) would cut code to about 0.2 MB and save most of the 0.87 bit; it is a different machine plan, stated in the note limits, no number claimed.

## What was changed against B3R4d (b4d) / portkit output
1. `b3port.py --rounds 7 --unit 1470` (selftest PASS vs organizer blake3(M,7)), then the b4 -> b4d diff patched onto the generated bsrho.py (patch applied cleanly; `b4_to_b4d.diff`). MEM_LIMIT set to 1,912,336 (budget, not 2^20); `plan` Tp search range 120 -> 400 (it was binding).
2. C generator (gen_c/gen.c): use counts widened from 4 to 8 bits (a node is used up to 19 times at r7; 4 bits saturate at 15, err 6) and signal packing 15 -> 16 bit node ids (46,231 nodes > 32,767). Output byte-identical to the Python program (sha256 e2666815...); wasm run in a 29-page (1,900,544 B) VM copy (gen_c/vm_r7.py, build_r7.py), 1,437 compiled wasm instructions (GEN_CODE, was 1,522), scratch 50,748 B; native under prlimit --data=1,912,272 identical.
3. Experiments memory: the organizer sandbox allows 128 MB and 20 s per experiment; the straight-line step compiled as one 46,000-line function peaked at 145-187 MB (OOM, exit 137 at intake). Step now compiles in chunks of 2,000 lines (function chain), peak 51 MB / 64 MB, 4.4 s / 6.5 s for 256 trials. Source trimmed (comment dashes, 6 comments) to stay inside 64 KiB: bsrho.py 61,828 B + manifest 3,400 B = 65,228 B (308 B spare).
4. proof_t.md / note_t.md / build_all.py retargeted (diff against *_b4d copies in this folder): lineage a6ee439c first, new proof Section 3.8 (memory and the scalar score), Section 7 memory text, note: what changed, response to the 41b32afc findings (all 9 ids named), no Python-RSS lines.

## Checks run (all pass unless stated)
- selftest True (step vs scalar, 4,096 lanes chained 7 steps, allocation, packed circuit 1,540 ops, 0 shared / 0 dead gates).
- ext/ref_regress.out: one step 8,192 lanes, 7 chained steps 4,096 lanes, packed circuit 448, scalar 300: 0 differences vs organizer blake3(M,7); ref_check: r3, r4, r7 digest vs organizer 2,000 msgs each and r7 vs blake3 library 1.0.11: 0 differences.
- Intake in the slot (pareto_pipeline intake, Docker): mechanically_valid, both experiments finish inside the 20 s / 128 MB limits (33 s total wall incl. container); organizer outputs in organizer_report_b7.json (summary organizer_summary.txt).
- rulecheck: mem-gate PASS (45 stage peaks <= 2^20.8669), R21 PASS (9 ids), 15 PASS / 4 N/A / 3 EXPOSED (R05 extrapolation, R07 public seed, R19 not-shipped ext checks: the same three as b4d). prefile_check: all PASS except "experiment programs known-good" (bsrho.py, same as b4d; intake passed). Note 12.3 KB (>= 5 KiB), dependencies: a6ee439c first, then 41b32afc, 75d5e1f9, 62cfd777, 0a9640ed, 3356413f, 6ae36351.

## Slot
~/hashsmash/yukon/pos_b3r7/pareto (base pos_b3r4d): STAGED.sha256 8f4bb7e1e704a95d..., dependencies.json sha256 5b19001f403431805650e07fe225cbc2bbee501982d7159cd43398f578378648. Package: research/blake3_r7/b7/pkg. Submit script (NOT run): research/launch/submit_pareto_b3r7.sh. (A scratch slot pos_b3r7pre used for the first intake was deleted.)

## Not tested / risks (plain)
- Section 4 (Lemma 2) is b4d's, checked by its author only; the judges' reading of a6ee439c is not yet known; the same reading applies here.
- Memory is a convention-heavy 2^20.87: the setup-phase overlay (generator image + scratch on the table/register region) and the 36 B per instruction code charge are as in b4d; the Python tooling was not run under the claimed cap.
- Memory scan optimum is for this program only. Time 125.054 is ~equal to r4 (125.060) because the larger table offsets the extra round; the memory term is the real cost of r7.
- r6 and r5 prepared only as generated bsrho.py (blake3_r6/b6, blake3_r5/b5, portkit output, FIT FAIL at 1 MiB, same code-size situation: 1,488,276 B and 1,221,192 B of code); nothing built or staged for them yet. Recipe = the steps above (gen.c constants NMAX/CODE_BYTES/ROUNDS, wasm GEN_CODE, MEM_LIMIT from the opt.py scan, appA.py constants, text tokens).
