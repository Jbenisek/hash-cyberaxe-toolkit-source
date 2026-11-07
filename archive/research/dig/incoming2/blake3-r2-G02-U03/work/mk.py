import json,os
D=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KA=("Known answer reproduced first with work/calc.py from proof.md Sec 11/12/18 numbers: time_log2 62.4347098 (T=(2,674,847,206,571,284,730,500+S_old)/430+2^38), search-phase bytes 6,013,036,259,648 (2^42.45123), output phase 8,796,093,155,510 (2^43.0000000219), output at t=2^32-1 = 8,796,093,020,278, S=85.43472. "
    "Convention: word 32 B, code 32 B/instruction (< 2^32 instructions = < 2^37 B), ledger charges are the proof worst-case budgets (bound, not best-case executed). Filed rule: tables released before the output, so peak = output phase 2^43; search-phase objects have zero marginal memory cost unless B3-STREAM is ruled (peak -> search 2^42.45123, S 84.88594). ")
def rec(cell,obj,q,num,notes,lever=False,gain=None,basis=None,labels=("C",)):
    o,name,m=cell.split('|')[1],None,cell.split('|')[3]
    r={"hash":"blake3-r2","row_i":None,"row_j":None,"object":obj,"question":q,"labels":list(labels),"status":"COMPUTED","number":num,
       "source":"our workflow: scan-once-wave2","own_test":True,"evidence":"research/dig/incoming2/blake3-r2-G02-U03/work/calc.py (proof.md Sec 9.1, 11, 12, 18 of research/tools/build_pkg/scratch/pkgB3S2/pkg/blake3-r2; retest/b3m_maxphase/RESULT.md)",
       "date":"2026-10-12","lever":lever,"gain_bits":gain,"notes":"universe cell %s. "%cell+KA+notes}
    if basis: r["gain_basis"]=basis
    fn=cell.replace('|','_')+".json"
    json.dump(r,open(os.path.join(D,fn),"w",encoding="utf-8"),indent=1)
C="written-out code (< 2^32 instructions x 32 B = < 2^37 B = 137,438,953,472 B; 2.285% of the search phase)"
rec("blake3-r2|MEM.CODE3|MEM|M2",C,"M2: exact ledger time to regenerate/interpret the code instead of holding it?",
 "Lower bound only: the ledger executes about N = 2.6748e21 machine units (every unit is one executed instruction); regenerating each executed instruction costs >= 1 unit, so T >= (2N+S_old)/430+2^38: time_log2 62.43471 -> >= 63.43323, dT >= +0.99852 bits. A cursor/loop form (2 extra units per representative batch, 4,682 of 213,439 per context) is estimated +0.0313 bits, unmeasured and not validated (opened-cluster code per lane site is not shared).",
 "Bound/estimate, not an executed measurement. The 2^32 instruction count is itself a bound (actual written-out size not counted here).")
rec("blake3-r2|MEM.CODE3|MEM|M3",C,"M3: S-optimal hold-versus-recompute point for the code, others fixed?",
 "HOLD. Filed rule: code is not in the peak (output phase), memory gain 0, so any time cost loses. Under STREAM: dropping all code cuts memory 6,013,036,259,648 -> 5,875,597,306,176 B, -0.03336 bits, against time >= +0.9985 (regenerate) -> net >= +0.965 worse. Only the unmeasured cursor form (est. +0.0313 time vs -0.0334 memory, net about -0.002 at the very best, needs all 2^32 instructions to be shareable) is not clearly worse.",
 "Bound/estimate. Not a lever: the 0.002 best case is inside the slack of the instruction-count bound.")
rec("blake3-r2|MEM.CODE3|MEM|M4",C,"M4: breakpoint at 2^20 B for the code: S on both sides, is crossing worth it?",
 "Not reachable and not worth it. Code alone is 2^37 B, 17 bits above 2^20; the memory term is linear above 2^20 (1 bit of S per bit of memory), so there is no local breakpoint: the code is 0.03336 bits of S under STREAM, 0 under the filed rule. Reaching < 2^20 B for code means ~2^17-fold shared code, which is the loop form priced in M2 (about break-even).",
 "Exact arithmetic on the proof's byte table; code-sharing factor is a hypothesis.")
O="output F||A and F||B (1024 t + 55 / 63 bytes, t <= 2^32-1; at most 2^43 - 1,930 B)"
rec("blake3-r2|MEM.OUT3|MEM|M2",O,"M2: exact ledger time to stream the output instead of holding it?",
 "Zero extra compressions. The final step (write both messages + two full blake3 evaluations, < 2^37.1 compressions) is charged < 2^38 units in all (proof Sec 11); a streamed evaluation does the same compressions with a chunk stack of <= 33 chaining values (already in the 4,096 B of the routine's words). dT <= 0 (saves the stores): at most 2^38/T = 4.4e-8 relative, 6e-8 bits. Cap-t alternative (t <= 2^31.45) is net 0 (memory -0.549, time +0.550, per wave2_blake3).",
 "Exact-by-ledger bound. Whether a streamed (never held) output is counted as zero memory is the organizer-ruling question B3-STREAM; not tested here.")
rec("blake3-r2|MEM.OUT3|MEM|M4",O,"M4: breakpoint at 2^20 B for the output: is crossing worth it?",
 "Yes if streaming is ruled free: output 2^43 B -> a buffer < 2^20 B (routine 131,072 + words 4,096 B) at no time; peak moves to the search phase 2^42.45123, S 85.43472 -> 84.88594, gain 0.54878 bits (exact). The crossing itself is worth only 0.54878, not 23 bits, because the search tables (2^42.45) remain above. Reproduces B3-STREAM (0.549).",
 "Same rule question as B3-STREAM; nothing new beyond the exact digits 0.54878.",lever=True,gain=0.54878,basis="S")
S="preprocessing selection SEL (offline, one program at a time, halts at 2^34 B; 2^34+2^20 = 2^34.00009 B)"
rec("blake3-r2|MEM.SEL3|MEM|M2",S,"M2: exact ledger time to shard/stream SEL instead of holding 2^34 B?",
 "SEL is charged S_old = 5,486,510,246,044,225,536 units = 2^53.503 units of time, adding 0.00296 bits to log2 T; every extra pass over SEL's work costs up to +0.00295 bits (doubling SEL). Memory value of SEL: 0 under the filed rule (offline, not co-resident); <= 0.00412 bits (2^34+2^20 beside the search) or 0.00822 (the old 2^35 slack) if it were summed.",
 "Ledger arithmetic. No kissat memory log exists in the store, so the actual RSS of the 116 runs and the time cost of a smaller cap were not measured; the 2^34 is a halt limit, not a measured peak.")
rec("blake3-r2|MEM.SEL3|MEM|M3",S,"M3: S-optimal hold-versus-recompute point for SEL?",
 "Hold as is (SEL off the peak; marginal S value 0 under the filed rule). Even in the summed reading, halving SEL's memory (2^34 -> 2^33) saves 0.00206 bits and any slowdown of SEL above about 70% extra work (0.00206/0.00295) loses; kissat at a smaller cap may halt without a model, so the result could change.",
 "Bound; no run of SEL was made.")
rec("blake3-r2|MEM.SEL3|MEM|M4",S,"M4: breakpoint at 2^20 B for SEL: is crossing worth it?",
 "No. SEL is 14 bits above 2^20; crossing is worth 0 under the filed rule and <= 0.00412 bits in the summed reading, and would need every solver run to fit in 1 MB, unmeasured and implausible for the kissat instances.",
 "Exact arithmetic on bytes; plausibility of a 1 MB solver is unmeasured.")
