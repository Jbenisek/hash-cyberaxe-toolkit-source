import json, re, os
os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/..")
EV = ("research/dig/incoming2/sha3-r5-G02-U03/work/ (meas.py, live.py, meas_k37.json, meas37.log); "
      "package research/tools/build_pkg/scratch/pkgR5T/pkg/sha3-256-r5/experiments/r5.py (imported read-only, scratch run); "
      "research/sol_answer_D152_r5_memshrink.md; research/sol_answer_D161_r5_memory_tables.md")
KA = ("Known-answer check: D152 ledger arithmetic reproduced, T0 = 2014712256488305708573/271000000000 gives time_log2 32.791562 "
      "(stated 32.79157), T_split 32.791872 (stated 32.79188), R5M 32.874286. The r5 package has no executable ledger program "
      "(lowm.py is the r37 one), so this check is exact-rational arithmetic on the stated numerators, not a re-run of a ledger script. ")
MEAS = ("Measurement: r5.py (pkgR5T) run unchanged on label R7 run 37 (B' cand 0, DF 36, 11,398,459,443 WK prim, 13 s), then 453 connector "
        "attempts with the shipped coin seeds: 50 accepted (369 lowdf, 34 cond), accept rate 0.110 on this label (R7 overall 0.305), accepted "
        "EM rank 1566-1567 (mean 1566.78), DF 33-34, 128,379-171,299 work units (mean 146,861), 4,409 coin draws per attempt. ONE label only. ")
CONV = ("Conventions: 'packed' = one echelon row of 1601 bits in 26 x 64-bit words = 208 B, structural cap rank <= 1567 because DF >= 33 is "
        "enforced; 'py' = sys.getsizeof of the shipped Python objects; 'tm' = tracemalloc. Proof convention is the stated 31/50 MiB and "
        "< 2^23 B bounds; D152 uses a 2 MiB code allowance (r5 proof: <2^18 instructions), not used here. ")
SUMM = ("Phase liveness (sampled, tracemalloc, same label): during bprime() Python peak 54.70 MB over base, live after bprime returns 0.63 MB, "
        "so the B' working set is released before the connector starts (algorithm() keeps only r = (beta1, beta0, c, j, DF)); spaces=[] is "
        "reset per advice round. D152's candidate-phase sum 113.5 + 8 + 2 + 0.62 = 124.12 MiB (26.9556) adds objects the shipped program does "
        "not hold together; phase-exact peak is B' + code = 115.5 MiB (26.8517), connector phase about 41 MiB + st (25.36), E phase 44.65 MiB (25.48). ")


def rec(cell, obj, q, status, number, notes, lever=False, gain=None, basis=None):
    r = {"hash": "sha3-r5", "row_i": None, "row_j": None, "object": obj, "question": q, "labels": ["N"],
         "status": status, "number": number, "source": "our workflow: scan-once-wave2", "own_test": True,
         "evidence": EV, "date": "2026-10-12", "lever": lever, "gain_bits": gain,
         "notes": "universe cell %s. " % cell + notes, "topic": cell}
    if basis:
        r["gain_basis"] = basis
    return r


R = []
R.append(rec("sha3-r5|MEM.CONN|MEM|M1", "connector scratch (one attempt: E_D + E_M echelon systems, A2sel, aff, row-form lists)",
 "M1 bytes held at peak", "SAMPLED",
 "BOUND (packed, structural): 3,200 rows x 208 B = 665,600 B = 2^19.34 (both echelon systems at rank 1600; measured peak rank sum ED+EM 3,171 -> 659,568 B). "
 "SAMPLED Python tracemalloc peak over base 1,412,141-1,424,393 B (5 re-run attempts incl. the max-work one, 180,171 units) = 2^20.43. "
 "Proof bound < 2^23 B = 8,388,608 B is 12.6x the packed figure and 5.9x the Python figure",
 KA + MEAS + CONV + "Peak is flat in work units (1.41-1.42 MB over 147k-180k units): rank sum saturates near 3,170. Sampled on one label; the packed bound 665,600 B is structural (rank <= 1600 each) and does not depend on the sample. Python figure includes dict/list/frozenset overhead."))
R.append(rec("sha3-r5|MEM.CONN|MEM|M2", "connector scratch", "M2 exact recompute / stream time instead of holding", "SAMPLED",
 "Rebuild = one attempt: measured mean over 453 attempts 14,213,742 prim (work units x 96 + 4,409 draws x 64; 10,490 units; 2.0e-6 bit of T0); ledger bound per attempt 121,634,816 prim (2^20 x 96 + 2^15 x 2^9 + 2^22). "
 "Spilling the scratch once per attempt (write+read 665,600 B at 1 prim per 4 B) = 332,800 prim = 2.3% of an attempt = 4.8e-8 bit. Streaming inside the attempt is not priced: the rows are rewritten about 146k times per attempt",
 KA + MEAS + CONV + "Draw charge 64 prim (S5T rule: 4 small + 4 swap); the 512/draw bound gives 16,356,095 mean over accepted attempts. About 9.06 attempts per accepted EM on this label (453/50): replay from the label costs one attempt only if the accepted index is stored (2 B); scanning costs about 1.29e8 prim."))
R.append(rec("sha3-r5|MEM.CONN|MEM|M3", "connector scratch", "M3 S-optimal hold-versus-recompute point", "COMPUTED",
 "HOLD (no spill, no recompute). The S value of the connector is its allowance, not its bytes: in D152's summed phase (124.12 MiB, 26.9556) the 8 MiB bound costs log2(124.12/116.12) = 0.0961 bit; at the Python peak 1.42 MB 0.0167 bit; at the packed bound 665,600 B 0.0079 bit. "
 "A spill costs 4.8e-8 bit, but replacing the bound by the packed structural bound (a proof text change, zero time) already gives 124.12 -> 116.78 MiB (26.8867), 0.069 bit. Under phase-exact liveness the connector is not on the peak phase and S is unchanged either way",
 KA + MEAS + SUMM))
R.append(rec("sha3-r5|MEM.CONN|MEM|M4", "connector scratch", "M4 breakpoint at 2^20 B (S on both sides)", "COMPUTED",
 "Packed structural bound 665,600 B = 2^19.34 is BELOW 2^20 (term 0); sampled Python peak 1.42 MB = 2^20.43 is above (0.43 bit on the object alone); the stated bound 2^23 is above (3 bit). "
 "Crossing is not worth chasing: the whole-program peak is the B' phase (2^26.85), so the memory term is 6.85 on both sides of the connector's own breakpoint",
 KA + MEAS + CONV + SUMM))
R.append(rec("sha3-r5|MEM.EM1|MEM|M1", "one accepted echelon system EM", "M1 bytes held at peak", "COMPUTED",
 "EXACT cap (packed): rank <= 1567 x 208 B = 325,936 B = 0.3108 MiB (2^18.31); measured 50 accepted EMs rank 1566-1567, mean 325,890 B. Python getsizeof 410,232-416,004 B (mean 413,119); tracemalloc live per EM 590,684 B (0.563 MiB). "
 "Stated 31/50 MiB = 650,117 B = 0.62 MiB: 1.99x the packed cap, 1.10x the Python tracemalloc figure",
 KA + MEAS + CONV + "The stated 0.62 MiB matches Python-object accounting (0.563 MiB) and is double the packed model. The packed cap 1567 rows is exact from the DF >= 33 rule (rank = 1600 - DF); stored beta0 (200 B) is extra."))
R.append(rec("sha3-r5|MEM.EM1|MEM|M3", "one accepted echelon system EM", "M3 S-optimal hold-versus-recompute point", "COMPUTED",
 "HOLD the one current EM. Streaming one EM out and back (packed 325,936 B x 2 / 4 B per prim) = 162,968 prim = 2.3e-8 bit of T0; recompute from the label = one accepted attempt, mean 14.38e6 prim (2.06e-6 bit) given the stored index. "
 "Memory value of removing one EM from D152's summed phase: log2(124.12/123.5) = 0.0072 bit (stated size), 0.0036 bit (packed); phase-exact: 0 (EM1 is not on the B' peak). "
 "Spilling is S-better only in the summed model; for one EM alone the optimum is hold",
 KA + MEAS + SUMM + CONV))
R.append(rec("sha3-r5|MEM.EM1|MEM|M4", "one accepted echelon system EM", "M4 breakpoint at 2^20 B (S on both sides)", "COMPUTED",
 "One EM is BELOW 2^20 B in every model: packed cap 325,936 B (2^18.31), Python 413,119 B getsizeof / 590,684 B tracemalloc (2^19.17), stated 650,117 B (2^19.31); 2^20 = 1,048,576 B is 1.6x the stated size. "
 "No memory term on its own; 2 EMs (stated) or 4 EMs (packed) cross 2^20",
 KA + MEAS + CONV))
R.append(rec("sha3-r5|MEM.EM50|MEM|M1", "the K = 50 accepted echelon systems held before E", "M1 bytes held at peak", "COMPUTED",
 "EXACT cap (packed): 50 x 325,936 = 16,296,800 B = 15.54 MiB (2^23.96); measured 16,294,512 B. Python getsizeof 20,655,948 B (19.70 MiB); tracemalloc 50 x 590,684 = 29,534,200 B (28.17 MiB, 2^24.82). "
 "Stated 31 MiB = 32,505,856 B: 1.99x packed, 1.10x tracemalloc. LIVENESS: spaces is local to the advice round and the B' tables are freed when bprime returns (Python peak 54.70 MB in bprime, 0.63 MB live after), "
 "so EM50 is never live together with the B' working set in the shipped program: connector phase about 8 + 31 + 2 MiB + st (25.36) versus B' phase 115.5 MiB (26.85)",
 KA + MEAS + SUMM + CONV + "This does not contradict D152, which only says the sum is not established as simultaneous. POSSIBLE LEVER (one measurement, not chased): declare memory as the max over phases instead of spooling EM to disk: 26.8517 (rounds 26.9) vs D152's 26.9556 (27.0) and the current 27.2, no spool charge (D152 charges +0.000310 bit). S gain 0.1 on the filing field (0.104 exact) plus 0.00031 time. Needs the proof's memory section to state release-before-connector for the shipped program, and B' 113.5 MiB to be an exact bound.",
 lever=True, gain=0.1, basis="S"))
R.append(rec("sha3-r5|MEM.EM50|MEM|M4", "the K = 50 accepted echelon systems held before E", "M4 breakpoint at 2^20 B (S on both sides)", "COMPUTED",
 "EM50 is above 2^20 in every model (packed 2^23.96, tracemalloc 2^24.82, stated 2^24.98): 3.96 to 4.98 bit alone. Crossing down (spool, 1 prim per 32-bit word): packed 2 x 16,296,800 / 4 = 8,148,400 prim = 1.2e-6 bit; D152's stated-size bound 16,252,928 prim plus 2^31 process allowance = +0.000310 bit. "
 "In the summed model spooling EM50 alone gains little (B' phase 113.5 + 8 + 2 = 123.5 MiB still sets the peak, 26.9477 vs 26.9556, 0.0072 bit); D152's 27.2 -> 27.0 comes from separating B' from EM50. "
 "Phase-exact (shipped program): EM50 is not on the peak, memory term 6.85 whether held or spooled, so spooling costs +0.000310 bit and saves 0. Crossing is NOT worth it",
 KA + MEAS + SUMM + CONV + "Recompute instead of hold: 50 accepted attempts from stored indices = 719,043,135 prim = 1.03e-4 bit, dearer than spooling (1.2e-6 bit packed)."))
for r in R:
    safe = re.sub(r'[^A-Za-z0-9]+', '_', r["topic"]).strip('_') + ".json"
    json.dump(r, open(safe, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(safe)
