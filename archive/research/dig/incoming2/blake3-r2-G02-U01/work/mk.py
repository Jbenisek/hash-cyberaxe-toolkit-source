
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

import json, os, sys
D = _hca_public_path_text('__HCA_WORKSPACE__/research/dig/incoming2/blake3-r2-G02-U01')
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/dig'))
import add_cell
ex = add_cell.load()
EV = ("research/dig/incoming2/blake3-r2-G02-U01/work/g02u01.py (+ledger.py extracted from "
      "research/tools/build_pkg/scratch/pkgB3S2/pkg/blake3-r2/proof.md Section 18; extra.py)")
COMMON = (
    "Convention: pkgB3S2 proof 12/18 ledger, machine units (430 per time unit), words 32 B, code 32 B/instruction. "
    "KNOWN ANSWER reproduced first: ledger N=2,680,333,835,014,828,941,956 -> time_log2 62.43471; search-phase bytes "
    "171*2^30*32+2,563,914*32+2^32*32 = 6,013,036,259,648 (2^42.45123), output phase 8,796,093,155,510 (2^43.00001); "
    "shipped S=62.43471+23.00001=85.43472. "
    "REGIMES: A = shipped (peak is the OUTPUT phase 2^43, search-phase memory is NOT the peak, so cutting any search table "
    "changes the memory term by 0 and any added time is a pure loss); B = output streamed/freed (open row B3M 249, itself "
    "-0.549 S, S=84.88594), where the search phase is the peak. Lookup counts are the charged bounds of the ledger "
    "(T2' lane tests <=10 per opened cluster +31 per straddling surcharge = 8.12e19; E-lane T1 loads 3.48e19; gate tests "
    "exactly 7*2340+4 per context = 1.997e19); 'est' assumes lanes uniform (share of lane tests needing a shift = (7-k)/7), "
    "'bound' assumes every such test needs it. Shift cost: +1 machine unit for a lane i>=1 test that reads the base table "
    "instead of its replica (shift right 36i, then AND). Not run: the program itself (ledger arithmetic only); register "
    "pressure and the load addressing mode are as the proof states them.")


def rec(cell, num, status, lever, gain, notes, q, obj):
    h = cell.split('|')[0]
    r = dict(hash=h, row_i=None, row_j=None, object=obj, question=q, labels=["N"], status=status, number=num,
             source="our workflow: scan-once-wave2", own_test=True, evidence=EV, date="2026-10-12", lever=lever,
             gain_bits=gain, notes="universe cell " + cell + ". " + notes + " " + COMMON)
    if gain is not None:
        r['gain_basis'] = 'S'
    r['topic'] = cell
    return r


Q = {"M2": "Exact ledger time to recompute/stream/shard the object instead of holding it",
     "M3": "S-optimal hold-versus-recompute point with the other objects fixed",
     "M4": "Breakpoint at 2^20 B: S on both sides, is crossing worth it"}
T2G = "T2' (3*2^32 words), T1 (2^32), gate table (2^30) base band = 18,253,611,008 words = 584,115,552,256 B"
REPL = "six lane replicas of T2', T1, gate = 109,521,666,048 words = 3,504,693,313,536 B"
PXF = "PXF' 3*2^32 words = 412,316,860,416 B"
R = []
R.append(rec("blake3-r2|MEM.T2G|MEM|M2",
 "Drop base band, lane-0 reads shift a lane-1 replica (+1 mu per lane-0 read): +1.94e19 mu (est, lanes uniform) = +0.01042 bit "
 "time (62.43471 -> 62.44513), or +1.19e20 mu (bound, every lane test) = +0.0626 bit (-> 62.49731). Single-copy T2' base only "
 "(2 of 3 copies dropped by a 32-bit lane mask): +0 mu. Full recompute by automaton (<=31 extra mu per read): T2 +0.956 bit, "
 "T1 +0.488, gate +0.368 (bounds). Exact ledger arithmetic on charged bounds.",
 "COMPUTED", False, None, "M1 for reference: " + T2G + " in the search phase; peak is the output phase.", Q["M2"], "MEM.T2G " + T2G))
R.append(rec("blake3-r2|MEM.T2G|MEM|M3",
 "Regime A (shipped): HOLD, S stays 85.43471. Regime B (output streamed): dropping the base band gives S 84.74893 est / "
 "84.80111 bound vs 84.88594 hold (gain 0.137 est / 0.085 bound); single-copy T2' base only: S 84.8184, gain 0.0675 at 0 added time.",
 "COMPUTED", True, 0.0675,
 "gain_bits = conditional regime-B single-copy gain 0.0675 (base band only). Premise not tested in a program: the lane-test mask "
 "can be 32 bits (Lemma MB reads T2' at omega + 2^32*guard bits, so the 3 copies only absorb guard bits). Counts only if output is streamed (open B3M 249).",
 Q["M3"], "MEM.T2G " + T2G))
R.append(rec("blake3-r2|MEM.T2G|MEM|M4",
 "2^20 B unreachable: object 2^39.1 B, search-phase floor is the code alone 2^37 B (137,438,953,472); S is on the slope (1 bit per bit) "
 "on both sides of any realistic cut. Break-even for dropping the whole band: added time < 0.1474 bit (B), < 0 (A). Shift-based drop costs 0.0104 (est) to 0.0626 (bound).",
 "COMPUTED", False, None, "Breakpoint arithmetic on ledger numbers.", Q["M4"], "MEM.T2G " + T2G))
R.append(rec("blake3-r2|MEM.REPL|MEM|M2",
 "Shift instead of six replicas (1 copy, lanes shift): +1.166e20 mu (est) = +0.0614 bit time (-> 62.49612) or +1.331e20 mu (bound) = "
 "+0.0699 bit (-> 62.50465). Per table (est/bound bit): T2 +0.0370/+0.0431, T1 +0.0160/+0.0186, gate +0.0092 (exact: 6 shifts per full representative batch, 3 in the last). "
 "Replica build saved (2^40+2^38+2^36 mu) is <1e-8 of N.",
 "COMPUTED", False, None, "M1 for reference: " + REPL + ".", Q["M2"], "MEM.REPL " + REPL))
R.append(rec("blake3-r2|MEM.REPL|MEM|M3",
 "Regime A (shipped): HOLD (replicas are in the search phase, not the peak). Regime B: SHIFT, 1 copy of each table: memory 2,508,342,946,112 B, "
 "S 83.68599 est / 83.69452 bound vs 84.88594, gain 1.200 est / 1.192 bound (memory -1.261, time +0.061/+0.070). Per table in B (S): T2 replicas only 84.158 (gain 0.728), "
 "T1 only 84.689 (0.197), gate only 84.845 (0.041).",
 "COMPUTED", True, 1.19,
 "Conditional on regime B (output not co-resident; open row B3M 249 = -0.549). Prices the OPEN B3-replica cell: memory up to -1.26 bit, time +0.061..0.070 bit, net -1.19..-1.20. "
 "Extra shift code and registers beyond one op per lane test not modelled. gain is S bits over the regime-B hold.",
 Q["M3"], "MEM.REPL " + REPL))
R.append(rec("blake3-r2|MEM.REPL|MEM|M4",
 "2^20 B unreachable (object 2^41.7 B; code floor 2^37 B). On the slope. Break-even for removing replicas in B is 1.2614 bit, cost 0.061-0.070, worth ~1.19 bit; in A break-even is 0 and it is a loss.",
 "COMPUTED", False, None, "Breakpoint arithmetic.", Q["M4"], "MEM.REPL " + REPL))
R.append(rec("blake3-r2|MEM.PXF|MEM|M2",
 "Replace PXF' (DB + 4 PX[x mod 512]) by the 512-word PX read at ix AND 511: +1 mu per opened cluster = 8.115e18 mu = +0.004361 bit time (62.43471 -> 62.43908); "
 "build 2^37 mu saved is negligible. 0 mu if the base folds into the load. Bound (one extra op in the descriptor selection, proof 9.9 charges 2 for address+load).",
 "COMPUTED", False, None, "M1 for reference: " + PXF + ". PXF'[x] depends on x mod 512 only (proof 12), so the 3*2^32 table is a 512-word function.", Q["M2"], "MEM.PXF " + PXF))
R.append(rec("blake3-r2|MEM.PXF|MEM|M3",
 "Regime A (shipped): HOLD, no S change (time +0.004, memory 0; S 85.43908). Regime B: DROP to 512 words: memory 5,600,719,415,616 B, S 84.78783 vs 84.88594, gain 0.0981 (memory -0.1025, time +0.0044).",
 "COMPUTED", True, 0.0981,
 "Conditional on regime B. Stacks with the replica and single-copy cuts: all three in B give memory 1,821,148,195,136 B, time_log2 62.5003 est / 62.5088 bound, "
 "S 83.2283 est / 83.2368 bound vs 84.8859 (gain 1.658 / 1.649); with streaming itself (-0.549 from 85.4347) about -2.2.",
 Q["M3"], "MEM.PXF " + PXF))
R.append(rec("blake3-r2|MEM.PXF|MEM|M4",
 "2^20 B unreachable for the program (object 2^38.6 B; code floor 2^37 B); the 512-word replacement is itself 16 KiB, below 2^20. Break-even for dropping PXF' is 0.1025 bit in B (cost 0.0044), 0 in A.",
 "COMPUTED", False, None, "Breakpoint arithmetic.", Q["M4"], "MEM.PXF " + PXF))
bad = 0
for r in R:
    cell = r['topic']
    fn = cell.replace('|', '_').replace('.', '_') + '.json'
    json.dump(r, open(os.path.join(D, fn), 'w', encoding='utf-8'), indent=1)
    e = add_cell.validate(r, ex)
    if e:
        bad += 1
    print(fn, e)
print("bad", bad)
