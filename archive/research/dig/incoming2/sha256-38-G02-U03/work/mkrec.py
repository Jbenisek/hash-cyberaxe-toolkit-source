import json, math, os
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results.json')))
slope = 1 / (math.log(2) * 2**20)
S0 = 87.903736
ev = ("research/dig/incoming2/sha256-38-G02-U03/work/analysis.py; research/dig/incoming2/sha256-38-G02-U03/work/results.json; "
      "research/dig/incoming2/sha256-38-G02-U03/work/analysis.out; research/dig/incoming2/sha256-38-G02-U03/work/ledger_repro.out; "
      "research/dig/incoming2/sha256-38-G02-U03/work/a0l_var.py (copy of research/tools/build_pkg/scratch/pkgR38M3/pkg/sha256-r38/experiments/a0lean38.py "
      "plus two override hooks dv/dvmax in ledger); research/tools/build_pkg/scratch/pkgR38M3/pkg/sha256-r38/proof.md Sections 9 and 14")
KA = ("Known-answer check passed first (WSL, a0lean38.py ledger on a scratch copy): N=789779068018615953003308365799, log2(N/2728)=87.9037359544, "
      "time_log2 87.90374; memory() returns 1,045,792 B = 2^19.99616 (2,784 B under 2^20), S0 = 87.903736 (memory term 0). "
      "Convention: r38 code = 32 B per instruction, 64 registers, machine model of proof.md 9.1 (the scalars HH..KP are registers; only the 224 stored planes are memory). "
      "Ledger values: hit probability per first block pany = 0.30319, 6.02 passing classes and 90.3 plane-program runs per first block on average (unconditional). ")

def rec(cell, obj, q, number, notes, lever=False, gain=None, basis=None, status="COMPUTED"):
    r = dict(id=cell, hash="sha256-38", row_i=None, row_j=None, object=obj, question=q, labels=[], status=status, number=number,
             source="our workflow: scan-once-wave2", own_test=True, evidence=ev, date="2026-10-12", lever=lever, gain_bits=gain,
             notes="universe cell %s. %s%s" % (cell, KA, notes), topic="sha256-38 MEM " + cell.split('|')[1] + " " + q.split(':')[0])
    if basis:
        r['gain_basis'] = basis
    fn = cell.replace('|', '_').replace('.', '_') + '.json'
    json.dump(r, open(os.path.join(D, fn), 'w', encoding='utf-8'), indent=1)

bu, rl, rr = R['BCAST_USEDONLY'], R['BCAST_R_LD'], R['BCAST_R_REG']
sp = R['SPILL']
OB = "per-first-block broadcast planes (7 x 32 words), filed r38 line pkgR38M3"
rec("sha256-38|MEM.BCAST|MEM|M2", OB, "M2: exact ledger time to recompute / stream / shard instead of holding",
    "EXACT (ledger arithmetic, shipped allocator): recompute each plane at every use inside the 7 plane programs (the 196-197 plane loads per program become 3-4 instructions each: shr, and, sub, plus a reload of the scalar). "
    "Scalar reloaded per use (R_LD): code +%d instructions, time_log2 %.5f (+%.4f bit), bytes %d. Scalar kept in a register (R_REG): code +%d instructions, time_log2 %.5f (+%.4f bit), bytes %d. "
    "Held planes cost 882 ops per hit first block (x0.30319 = 267 per first block); recompute costs about 90.3 runs x 579 (R_LD) or 382 (R_REG) extra ops per first block. Streaming or sharding does not apply (each plane is consumed once per run by the program that loads it)."
    % (rl['code_delta_instr'], rl['T'], rl['dT'], rl['bytes'], rr['code_delta_instr'], rr['T'], rr['dT'], rr['bytes']),
    "Plane census (new, exact): of the 224 stored planes only %d are ever loaded by any of the 7 programs (never loaded: PP 2, QQ 7, KP 15); every loaded plane is loaded once per run (196-197 loads per run). "
    "Recompute pricing: j=0 and j=31 cost 2 ops, other j 3 ops, plus 1 load of the scalar for R_LD, in place of the 1 plane load; code growth charged at 32 B per instruction. "
    "R_REG ignores the register pressure of 7 pinned scalars (the 64-register allocator would have to be rerun), so it is a floor for the time." % bu['n_used'])
rec("sha256-38|MEM.BCAST|MEM|M3", OB, "M3: S-optimal hold-versus-recompute point for this object, others fixed",
    "EXACT: S-optimal is HOLD, storing only the %d planes some program loads (not 224): time_log2 %.5f (%.5f bit; planes_of 882 -> %d ops per hit first block), bytes %d (-768 B), S %.5f against S0 87.90374. "
    "Hold all 224 (shipped): S 87.90374. Full recompute: R_LD S %.5f (+%.4f), R_REG S %.5f (+%.4f)."
    % (bu['n_used'], bu['T'], bu['dT'], bu['planes_ops'], bu['bytes'], bu['S'], rl['S'], rl['S'] - S0, rr['S'], rr['S'] - S0),
    "Per plane the decision is hold when runs per first block (90.3) x extra ops per use (2 to 3) exceeds pany x store-and-build cost (0.30319 x 3 to 4): always; recompute would pay only below 0.4 runs per first block. "
    "The only gain is skipping the 24 never-loaded planes in planes_of (93 ops per hit first block, 2.2e-4 of the first-block cost); lever size 0.0003 bit, memory -768 B (no S effect). One measurement, not chased: whether other routines (lane scan, step3b) read these planes was not checked beyond the model, in which scalar_e16 and step3b take the scalars HH..KP (registers), not the stored planes.",
    lever=True, gain=round(-bu['dT'], 5), basis="T")
rec("sha256-38|MEM.BCAST|MEM|M4", OB, "M4: breakpoint at 2^20 B, S on both sides, is crossing worth it",
    "EXACT: total memory is 2^19.99616 (slack 2,784 B), so removing the object gains 0 in S. Crossing by recompute is NOT worth it: R_LD goes to %d B (over 2^20 by %d B), S %.5f vs 87.90374 (+%.4f bit: time +%.4f, memory term +%.4f); "
    "R_REG %d B, S %.5f (+%.4f). Above 2^20 the price is %.4e bit per byte, so holding the full 7,168 B would cost %.5f bit if memory were already charged, against a recompute time cost of %.3f to %.3f bit (33x to 48x more)."
    % (rl['bytes'], rl['bytes'] - 2**20, rl['S'], rl['S'] - S0, rl['dT'], math.log2(rl['bytes']) - 20, rr['bytes'], rr['S'], rr['S'] - S0, slope, math.log2(1 + 7168 / 2**20), rr['dT'], rl['dT']),
    "The breakpoint is crossed only because the unrolled recompute code is larger than the planes it removes (+%d or +%d instructions = +%d or +%d B against -7,168 B)." % (rl['code_delta_instr'], rr['code_delta_instr'], 32 * rl['code_delta_instr'], 32 * rr['code_delta_instr']))
OS = "spill slots of the plane programs, filed r38 line pkgR38M3"
rec("sha256-38|MEM.SPILL|MEM|M2", OS, "M2: exact recompute time instead of holding",
    "COMPUTED (this allocator; the time is a LOWER bound for removal, not an optimum over allocators): replacing spill slots by rematerialisation (drop the evicted value, rebuild it from its operands when needed) is infeasible. "
    "With 15 slots the 7 programs reproduce the shipped 1410..1426 instructions (0 rematerialisations); with 14 slots programs 2..6 exceed the 400,000-instruction cap (53,327 to 78,887 rematerialisations each); with 0 to 12 slots all 7 do. "
    "At the cap the run time rises by at least +7.43 bit (14 slots, programs 2..6) and +8.06 bit (0 slots, all 7 programs): the serial carry chain of W1 makes rematerialisation grow with the chain length.",
    "The 15-slot figure is exact: the shipped Belady allocator uses 14 stores (programs 0, 1) and 15 (programs 2..6) with no slot reuse; the proof's 40 words is a budget (bound), 15 x 32 = 480 B is the exact allocation. "
    "The rematerialising allocator is our own variant of Prog.schedule (analysis.py, operand-order heuristic); a better heuristic could lower the cost but spill removal saves only 480 B, which S does not price below 2^20.")
rec("sha256-38|MEM.SPILL|MEM|M3", OS, "M3: S-optimal hold-versus-recompute point",
    "EXACT: S-optimal is hold exactly 15 slots (480 B, not the 1,280 B budget): time_log2 87.90374 unchanged, bytes 1,044,992, S 87.90374 (memory term 0 either way). Fewer than 15 slots costs at least +7.4 bit. The 25 unused budget words (800 B) can be given up for free.",
    "Shipping 1,280 B is a bound, not an exact count; the proof total 1,045,792 would be 1,044,992 with the exact allocation (3,584 B under 2^20 instead of 2,784).")
rec("sha256-38|MEM.SPILL|MEM|M4", OS, "M4: breakpoint at 2^20 B, S on both sides, is crossing worth it",
    "COMPUTED: the object is below 2^20 (1,280 B budget, 480 B used). If memory were charged, holding it would cost at most %.5f bit (1,280 B at %.4e bit/B above 2^20) against a recompute cost of at least +7.4 bit: hold wins by a factor of 4000 or more. "
    "No crossing is reachable from this object: removing all of it moves memory from 1,045,792 to 1,044,512 B, still below 2^20." % (math.log2(1 + 1280 / 2**20), slope),
    "Same allocator caveat as M2.")
hu = R['SCAL_HITLIST_UNCOND']; sc = R['SCAL_RECOMP_PER_LANE']
OC = "scalars, counters, hit list, F7 constants (64 words), filed r38 line pkgR38M3"
rec("sha256-38|MEM.SCAL38|MEM|M2", OC, "M2: exact recompute/stream time instead of holding",
    "EXACT (ledger): (a) hit list streamed (no list: handle each class as the W7 loop finds it, with a first-hit flag so scalars and planes are built once per first block): the append (2 ops per hit) is replaced by a flag test (2 ops per hit), net 0 ops, time_log2 87.90374 unchanged; "
    "(b) streamed with scalars and planes built unconditionally before the scan (no flag): +%.1f ops per first block, time_log2 %.5f (+%.5f bit); "
    "(c) the 8 scalars recomputed from CV1 at every lane instead of held: 5.644 lanes per first block x 38 ops = +%.1f ops, time_log2 %.5f (+%.5f bit), memory saved 0 (CV1, 8 words, must be held for step3b)."
    % (hu['dv'], hu['T'], hu['dT'], sc['dv'], sc['T'], sc['dT']),
    "The itemisation of the 64-word lump is not in the package (it names scalars, counters, hit list and F7 constants); the F7 constants are immediates of the decision tree (instruction fields, 0 words in the model). "
    "The model uses the fb_scalars values without a load charge (registers), so holding them is free in time and (c) is the price of replacing that.")
rec("sha256-38|MEM.SCAL38|MEM|M3", OC, "M3: S-optimal hold-versus-recompute point",
    "EXACT: S-optimal is the shipped hold for scalars and counters (any recompute adds time and frees no byte that S prices); hold or stream for the hit list gives identical time. S stays 87.90374; with the hit list at one word per class (+832 B) memory is 1,046,624 B and S is still 87.90374.",
    "Observation, not chased: the 64-word lump holds at most 64 hits while a first block with a hit has on average about 19.9 passing classes (6.02 / 0.30319) of 90; the proof sets the full list at +832 B, still under 2^20. Streaming the hit list removes any overflow question at zero time.")
rec("sha256-38|MEM.SCAL38|MEM|M4", OC, "M4: breakpoint at 2^20 B, S on both sides, is crossing worth it",
    "EXACT: below the breakpoint, slack 2,784 B. Growing this object to the full hit list (+832 B, 1,046,624 B) stays below 2^20, S 87.90374 (no charge). Removing it entirely saves at most 2,048 B and 0 bit of S. "
    "Above 2^20 the price is %.4e bit per byte (2,048 B = %.5f bit), against recompute costs of +0.00229 bit (scalars, frees 0 B) and +0.0067 bit (unconditional build): neither is worth it." % (slope, math.log2(1 + 2048 / 2**20)),
    "No crossing is reachable from this object alone.")
print('ok')
