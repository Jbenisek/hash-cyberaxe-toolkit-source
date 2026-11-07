# blake3 round 4 (pareto) - first entry B3R4 - STATUS (2026-10-14 22:30, Sonnet agent)

STAGED, NOT SUBMITTED. Needs the owner's go, then: `bash research/launch/submit_pareto_b3r4.sh` (refuses if any staged file or dependencies.json changed).

## Certified result
- time_log2 **125.35348** (N = 45,975,348,661,915,794,155,860,938,138,573,316,801,453 operations; unit C(r4) = 846; log2(N/846) = 125.3534705; integer-power certificate in proof Appendix A, output equals claim).
- memory 1,048,568 B (<= 2^20, 8 B spare; setup phase 1,042,104 B); claim memory_log2_bytes 20 -> pareto memory term 0. Success lower bound 0.3903 (>= 0.39), single attempt, no advice, preprocessing_log2 14.9 (inside time).
- r4 normalization: organizer `pareto/targets.py:reference_cost('blake3', r)` = 222, 430, 638, 846 for r = 1..4 (computed in the slot's repo, commit 599dd14; profile `blake3-r4-prefix-v1` exists). Compare r3 B3R3PV 124.8123 (+0.5412).
- Program: the B3R3PV program at 4 rounds. Step 24,422 gates (95.40/trail), 771 registers, batch 24,459 ops, 26,502 instructions = 954,072 B, table only 1,744 entries x 26 B (Tp = 17, L = 2^117.91), recovery circuit 836 ops.

## Where things are
- Package (final): research/blake3_r4/b4/pkg (blake3/{claim.json, proof.md, experiments/{bsrho.py, manifest.json}, certificates/manifest.json}, submission-note.md, dependencies.json). Builders: b4/build_all.py (+ proof_t.md, note_t.md, appA.py/appA.out), regenerate with `python3 -B build_all.py` after gen_c/cport.json, stats_out.txt, organizer_summary.txt, timing.json, ext/pygen_rss.json, gen_c/native/native.json.
- Slot: ~/hashsmash/yukon/pos_b3r4 (WSL; base pos_b3r3pv; `mechanically_valid`, package sha256 e85976e2...7dd5, STAGED.sha256 32290b33..., dependencies.json sha a6d331fd...). Submit script (NOT run): research/launch/submit_pareto_b3r4.sh.
- Dependencies (all pareto-blake3, same challenge): 62cfd777-5613-463f-b561-e2340e00e528, 0a9640ed-558a-4f0a-aba8-45e89ffcfd7c, 3356413f-cd60-410c-8847-2266d6444ac5, 6ae36351-5836-4a46-ad34-227688264123 (all four show `review` on the API 22:18). No scalar-board id (cf8b0e92, e479cbbf are credited in text only).

## What was run (all 0 mismatches / identical)
1. Reference: program `digest_words` vs organizer verifier `blake3(M, r)` at r = 3 (first), 4 and 7 (2,000 msgs each); at r = 7 program and organizer vs the `blake3` library 1.0.11 (2,000 msgs, ten lengths 0..3,000 for the organizer): 0 differences (ext/ref_check.py).
2. Step: bit-sliced step vs organizer `blake3(M,4)`: 8,192 lanes one step, 4,096 lanes (16 x 256) chained 4 steps, packed recovery circuit 448, scalar 300 (ext/ref_regress.py/.out); program selftest (4,096 lanes, 4,096 lanes chained 4 steps, allocated code on a register file, n=18 chain, packed circuit, 0 shared / 0 dead gates): True.
3. Generator: new two-pass C generator without node table (gen_c/gen.c, embedded in bsrho.py as GEN_C): WebAssembly in the 1 MiB VM (16 pages, 987,312 B static, 23.4M wasm ops) and native static binary under `prlimit --data=1048576 --stack=65536` both emit a program byte-identical (sha256 90d580d0...) to the Python Step/allocate (24,422 instr, 771 regs, same q). Generator image charged 1,522 wasm instructions x 36 B = 54,792 B (llvm-objdump of the -Os build), scratch 16,856 B.
4. Organizer pipeline in the slot (`pareto_pipeline.py intake --family blake3`, Docker): mechanically_valid, bsrho-n18 174/256 pairs, proj-k0-w256 159/256, 256 trials each, stdout byte-identical on replay; judge-evidence 139,825 B (< 524,288).
5. rulecheck: 12 PASS, 4 N/A, 3 EXPOSED (R05 extrapolation, R07 public-seed wording, R12 "not charged" wording) - the same wording as the r3 entries, read, no change. prefile_check: all PASS except "experiment programs known-good" (hash list has no entry for bsrho.py; the experiments run 3.6 s / 5.2 s for 256 trials).

## What changed against B3R3PV and why (so a reviewer of the diff is not surprised)
- 4 rounds in digest_words, packed tracer, trace, GEN_C; unit 846.
- Generator rewritten (two passes, 4-bit use counts, registers carried in the signals): the old hash-consing generator needs 283 KB scratch + 73 KB image, which does not fit beside a 954 KB program (setup phase would be 1.3 MB). Hash-consing hits and dead gates are 0 at r4 (selftest prints it), so no node table is needed. The image is charged by the compiled instruction count of the C program (1,522), not by Python bytecodes.
- Table entry 26 B (a trail length reaches 2^121.4 -> 16 B). OTHER_CODE is computed (handlers 1,000 + recovery circuit + 47 + 160) instead of 1,810.
- `--ledger` CLI prints smaller-register-file rows without crashing (512: plan below 0.39; 256: no table fits).

## Not tested / residual risk (say it plainly)
- Python tooling (ledger, selftest, ext checks, organizer pipeline) ran uncapped (ulimit -v 2 GB), not under prlimit 1 MiB: a Python interpreter cannot. Only the generator, the one component that defines the circuit, q, the register count and the instruction count, was run under the 1 MiB caps (WASM guest cap; native `--data`; native `--as` needs 1.125 MiB because kernel stack/vdso mappings count). If a judge applies "development runs must be capped at the claimed peak" to the Python reference generator (111.3 MB, proof 3.6 (iii)), this entry and B3R3PV are exposed the same way.
- The generator image convention (compiled wasm instruction count x 36 B) is new relative to 3356413f/B3R3PV (Python bytecode count); the machine has no instruction set. Disclosed in the note limits and H3.
- Setup-phase total 1,042,104 B counts the 16,384 B of counters on top of the overlay region (conservative); the search phase is 8 B under 2^20.
- H1 (random-function model) is the same declared premise as the accepted r3 entries; not testable at width 256.

## Cheap follow-up levers (computed with the program's own ledger, none built or staged)
- Declare R = 800 registers instead of 1,024 (771 needed): 125.27008 (-0.083 bit), tmax 2,020. One-line convention change in the H3 text and REGISTERS.
- kappa 10 instead of 11: -0.009 bit (P_lower 0.39015); tail 3e-3 with lambda 0.503: -0.027 bit.
- Smaller table entries (the stored 16 B length is the big item; recomputing lengths in the recovery costs about 2x more recovery work): entry 18 B -> 125.176; 10 B -> 125.016 before re-pricing recovery.
- Exceeding 2^20 B by about 4% would net roughly -0.1 bit if the memory term max(0, log2 B - 20) is applied; the instruction was memory <= 2^20, so not done.
