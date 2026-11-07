
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

import json, math, os
N = 10377085310562
dT = lambda x: math.log2((N + x) / N)
MiB = 1 << 20
CAND = 124.12 * MiB
mg = lambda b, P: math.log2((P + b) / P)
O3, O4 = 12924201, 4805937
OUT = _hca_public_path_text('__HCA_WORKSPACE__/research/dig/incoming2/sha3-r5-G02-U04')
W = "research/dig/incoming2/sha3-r5-G02-U04/work/"
EV = ("%sfinal.py; %scnt.py; %ssweepbuf.py (+sweepbuf.out); %sanf_struct.py; %sledger_I4.py (Appendix I.4 ledger program, extracted unchanged); "
      "%sr5_copy.py (byte copy of pkgR5T experiments/r5.py); research/tools/build_pkg/scratch/pkgR5T/pkg/sha3-256-r5/proof.md Sections 2.4, 7, Z.3, Z.5, Appendix B, I.4; "
      "research/sol_answer_D152_r5_memshrink.md; research/sol_answer_D161_r5_memory_tables.md") % ((W,) * 6)
KAT = ("Known-answer checks (all passed): ledger_I4.py reproduces N = 10,377,085,310,562 primitives, time_log2 32.83439; shipped r5.py e_block returns block 410,392 + prologue 87 (E_STEPS, E_PRO); "
       "own counter cnt.py (the shipped e_blk with block length, passes and resident list as parameters) gives 410,392 at 2048 steps and 207,920 at 1024 steps (= 208,007 - 87, proof Z.3); "
       "E stage 1 online 50 x 8192 x 410,479 = 168,132,198,400 prim = 2^26.8867 units (= G.6); G fetches in fes_setup.deriv counted 19,024 (= the ledger's 19,024 vector XORs). "
       "Conventions: primitive = 1/1355 target unit; memory = declared-object bytes of the shipped program, 32 B per 256-bit word, code allowance as in D152 (2 MiB) plus one echelon system 0.62 MiB; other phases from D152/D161 "
       "(candidate phase 124.12 MiB = 130,149,253 B after the stream-one-EM phase split, P phase 85.1 MiB, declared 2^30). 'All E spaces' = 582 (50 online + G2 530 + 2 self-tests, count read from the proof text, not re-derived); online-only = 50 (exact). "
       "Not run: no full-program rebuild of any variant; variants are priced from the counted programs only.")


def rec(obj, q, status, labels, number, notes, topic, cellid):
    r = dict(hash="sha3-r5", row_i=None, row_j=None, object=obj, question=q, labels=labels, status=status, number=number,
             source="our workflow: scan-once-wave2", own_test=True, evidence=EV, date="2026-10-12", lever=False, gain_bits=None,
             notes="universe cell %s. %s %s" % (cellid, notes, KAT), topic=topic)
    fn = cellid.replace("|", "_") + ".json"
    json.dump(r, open(os.path.join(OUT, fn), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    return fn


files = []
ctx = ("EVEC context: D1..D4 = 24 + 276 + 2,024 + 10,626 vectors x 24 words x 32 B = 18,432 + 211,968 + 1,554,432 + 8,160,768 = 9,945,600 B (exact, M1; D4 is 82.05%). "
       "Measured on a real instance (shipped fes_setup, 32 variables, 41,449 evaluations): every D4 word is 0 or all-ones - 10,626 x 24 words, 2 distinct values - because a degree-4 outer monomial has only the inner monomial 1, so D4 is 24 bits per row (u32, 42,504 B). "
       "D3 words are affine, D2 quadratic, D1 cubic in the 8 inner coordinates (sampled 200/200/24 vectors, all 24 words each).")
files.append(rec("E derivative vectors D1..D4 (r5 E stage 1)",
  "M2: exact ledger time to recompute/stream the derivative vectors instead of holding them",
  "COMPUTED", ["N", "E"],
  "Streaming D4 (8,160,768 B) as 24-bit mask rows (42,504 B) expanded to a 256-bit word per use: +5 primitives per (step, pass) (1 u32 load + 2 words x 3 (shift, and, negate) - 2 loads), i.e. +60 per step, +122,880 per 2,048-step block (410,392 -> 533,272, +29.9%), +1,006,632,960 prim per space. "
  "delta time_log2 = +0.006981 (50 online spaces, exact count) / +0.07923 (all 582 E spaces, count from proof text). With a 2-primitive mask (shift, arithmetic shift): +73,728 per block, +0.004192 / +0.04806. "
  "[formulas exact; the mask cost per word is my bound]. D1..D3 (1,784,832 B) stay resident; packing them (93 / 37 / 9 bits per equation word) is not priced: OPEN.",
  ctx + " Recomputing D4 from the ANF table is the same object as the mask rows (D4[K] = G[K], one table entry). The ledger charges the D4 load at 1 primitive per word (not resident).",
  "MEM.EVEC", "sha3-r5|MEM.EVEC|MEM|M2"))
files.append(rec("E derivative vectors D1..D4 (r5 E stage 1)",
  "M3: S-optimal hold-versus-recompute point for the derivative vectors, others fixed",
  "COMPUTED", ["N", "Z"],
  "At the real peak (candidate phase B', bound 130,149,253 B; P phase 89,233,818 B; declared 2^30) the E objects are off-peak: holding all of EVEC is S-optimal; any shrink changes the memory term by 0.000 and costs +0.0070 (online) to +0.0792 (all spaces) bits of time. "
  "Conditional (not the current state): if the B' and P phases were both brought under the E phase, then with the ANF table streamed (E phase 12,924,201 B) packing D4 cuts the E phase to 4,805,937 B: memory term 3.6236 -> 2.1964 (-1.4272 bits) for +0.0070 / +0.0792 bits of time, net S -1.420 / -1.348, so packing D4 would then be S-optimal.",
  ctx, "MEM.EVEC", "sha3-r5|MEM.EVEC|MEM|M3"))
files.append(rec("E derivative vectors D1..D4 (r5 E stage 1)",
  "M4: breakpoint at 2^20 B for the derivative vectors (S on both sides, is crossing worth it)",
  "COMPUTED", ["N", "Z"],
  "EVEC held = 9,945,600 B = 9.485 x 2^20 (object-alone memory term 3.2455). D4 packed: 1,827,336 B = 1.743 x 2^20 (term 0.80), still above the knee. All four levels bit-packed (D1 93, D2 37, D3 9 bits per equation word, D4 24 bits per row) is a storage floor of 134,484 B = 0.128 x 2^20, below the knee; the per-step expansion time of D1..D3 is not priced (OPEN). "
  "Crossing is not worth it today: the E phase also holds the code allowance (2 MiB) and one echelon system (0.62 MiB), 2.62 MiB > 2^20 by itself, and the program peak is the B' phase (27.0 bits), so the memory term stays above 0 on both sides.",
  ctx, "MEM.EVEC", "sha3-r5|MEM.EVEC|MEM|M4"))

ctx2 = ("EANF context: the table of fes.c / proof Section 7: 41,449 x 768 B = 31,832,832 B is a virtual size (G = calloc(41,449 entries), indexed by 32-bit colex rank). Only the 12,951 entries with outer weight <= 4 over 24 variables are ever written: 9,946,368 B touched (the Python fes_setup dict also holds only nonzero entries). "
        "G is never read after the derivative vectors are built, yet fes.c never frees it. Setup uses 19,024 G fetches (counted: 1, 24, 299, 2,530, 16,170 by outer weight 0,1,2,3,4).")
files.append(rec("E ANF setup table (fes.c)",
  "M2: exact ledger time to stream/recompute the ANF setup table instead of holding it",
  "COMPUTED", ["N"],
  "Streaming the table costs 0 extra charged time. Keep only the 41,449 evaluations / ANF coefficients as u32 (A array, 165,796 B, Moebius in place) and rebuild each G entry when deriv fetches it: 52,398 (coefficient, equation-vector) visits x 72 + 52,398 loads = 3,825,054 primitives per space (bound: 24 equations x 3 per visit), against the ledger setup components it replaces (41,449 x 24 x 3 truth-table words + 19,024 x 72 vector XORs = 4,354,056): -529,002 prim per space. "
  "Moebius 617,089 + 3,825,054 stays inside the charged 2^23 = 8,388,608 primitive setup bound (the 41,449 evaluations are unchanged, 41,449 units). So delta time_log2 = 0 (charged); the table drops from 31,832,832 B (virtual) / 9,946,368 B (touched) to 165,796 B. [visit and fetch counts exact; 72 per visit is the ledger's own bound]. Simply freeing G after the vectors are built costs the same 0 and leaves a setup peak of G + D.",
  ctx2, "MEM.EANF", "sha3-r5|MEM.EANF|MEM|M2"))
files.append(rec("E ANF setup table (fes.c)",
  "M3: S-optimal hold-versus-recompute point for the ANF setup table, others fixed",
  "COMPUTED", ["N", "Z"],
  "Stream (or free) it: the time cost is 0, so this is a free move, but at the real peak (B' phase 130,149,253 B, P phase 89,233,818 B, declared 2^30) it changes S by 0.0000 because the E phase is not the peak. "
  "Conditional on the B' and P phases dropping below it: E phase 44,591,237 B (log2 25.4103, term 5.4103) -> ANF freed after setup 12,758,405 B (term 3.6049) or streamed from the A array 12,924,201 B (term 3.6236): -1.787 bits of memory term at 0 time. If G is only freed after the build, the setup peak is G + D touched = 22.7 MB (term 4.44), so the streamed form is what removes the setup peak.",
  ctx2, "MEM.EANF", "sha3-r5|MEM.EANF|MEM|M3"))
files.append(rec("E ANF setup table (fes.c)",
  "M4: breakpoint at 2^20 B for the ANF setup table (S on both sides, is crossing worth it)",
  "COMPUTED", ["N"],
  "Held: 31,832,832 B virtual = 30.36 x 2^20 (object-alone term 4.9222); touched 9,946,368 B = 9.49 x 2^20 (3.2461). Streamed from the A array: 165,796 B = 0.158 x 2^20, below the knee (term 0): crossing is free in time (M2) and worth 4.92 bits for the object alone, but the program-level term does not move while the B' phase (27.0 bits) and P phase (26.4 bits) exceed the E phase; the whole E phase after streaming is 12,924,201 B (term 3.62) and cannot reach 2^20 because EVEC alone is 9,945,600 B.",
  ctx2, "MEM.EANF", "sha3-r5|MEM.EANF|MEM|M4"))

ctx3 = ("EBUF context: shipped r5.py e_blk keeps buf = [0]*2048 (one 256-bit partial-OR word per step of a 2,048-step block) = 65,536 B (exact, M1); proof Z.3 text and D161 speak of 1,024-step blocks and 32,768 B (the 208,007-primitive design); the shipped counted block is 410,392 + 87 per 2,048 steps (E_STEPS, E_PRO), 12 passes of 2 equation words, 29 resident vectors. The buffer is the only state carried between passes.")
files.append(rec("E pass buffer (e_blk partial-OR buffer)",
  "M2: exact ledger time to drop or shrink the pass buffer",
  "COMPUTED", ["N"],
  "Per space = 8192 blocks of 2048 steps at the shipped 410,392 + 87 (own counter on the shipped e_blk; prologue assumed 87 for other block lengths). No buffer (single pass, 24 words resident): 543,128 per 2,048 steps = 265.20 per step vs 200.39, +1,087,373,312 prim per space, delta time_log2 +0.007539 (50 spaces) / +0.085405 (582). "
  "Half the buffer (1,024-step blocks, 32,768 B, 12 passes, 29 resident): 207,920 per 1,024 steps = 203.05 per step, +45,342,720 per space, +0.000315 / +0.003664. "
  "Double the buffer (4,096-step blocks, 131,072 B): 819,536 per 4,096 = 200.08 per step, -5,468,160 per space, -0.0000376 / -0.000443 bits. Best (passes, resident) per block length from a small search; counts exact for those layouts, prologue 87 assumed for lengths other than 2,048.",
  ctx3, "MEM.EBUF", "sha3-r5|MEM.EBUF|MEM|M2"))
up = mg(65536, CAND)
dn = mg(-32768, CAND)
files.append(rec("E pass buffer (e_blk partial-OR buffer)",
  "M3: S-optimal hold-versus-recompute point for the pass buffer, others fixed",
  "COMPUTED", ["N", "Z"],
  "At the candidate-phase peak (130,149,253 B) the shipped 2,048-step buffer is S-optimal among the tested lengths: 4,096 steps saves 0.000443 bits of time (582 spaces) but adds 65,536 B = +%.6f bits of memory term, net %+.6f; 1,024 steps saves %.6f bits of memory term for +0.003664 of time (net %+.6f); no buffer is +0.0854 with no memory gain. "
  "At the declared 2^30 the memory term is fixed (10 bits), so the 4,096-step block would be 0.000443 bits better (0.0000376 online-only): the only positive number in this unit, and tiny. "
  "If the E phase were the peak (12,924,201 B), 1,024 steps changes the memory term by %.6f bits for +0.003664 of time: net %+.6f." % (
      up, dT(582 * -5468160) + up, -dn, dT(582 * 45342720) + dn, mg(-32768, O3), dT(582 * 45342720) + mg(-32768, O3)),
  ctx3, "MEM.EBUF", "sha3-r5|MEM.EBUF|MEM|M3"))
files.append(rec("E pass buffer (e_blk partial-OR buffer)",
  "M4: breakpoint at 2^20 B for the pass buffer (S on both sides, is crossing worth it)",
  "COMPUTED", ["N", "Z"],
  "65,536 B (shipped) = 0.0625 x 2^20 and 131,072 B (4,096 steps) = 0.125 x 2^20 are both far below the knee: object-alone term 0 on both sides, so there is no breakpoint to cross. The buffer enters S only as a marginal add to the program peak (+%.6f bits per 65,536 B at the 130,149,253 B candidate peak, +%.5f at a 12.9 MB E-phase peak). The buffer would reach 2^20 B only at 32,768-step blocks (not priced); no crossing worth making." % (up, mg(65536, O3)),
  ctx3, "MEM.EBUF", "sha3-r5|MEM.EBUF|MEM|M4"))
print(files)
