
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
R = json.load(open('res05.json')); V = R['variants']
W = "research/dig/incoming2/sha256-38-G02-U05/work/"
EV = (W+"g02u05.py; "+W+"run05.py; "+W+"res05.json; "+W+"base.json; "+W+"a0lean38.py (copy of pkgR38M3 experiments/a0lean38.py); research/tools/build_pkg/scratch/pkgR38M3/pkg/sha256-r38/proof.md Sections 5.3, 8, 14")
KAT = ("Known-answer check: a0lean38.py ledger reproduces time_log2 87.90373595 (N = 789779068018615953003308365799, C = 2728) and memory() reproduces 1,045,792 B = 2^19.9962 (r38 convention: 32 B per instruction and per word); asserted before use. "
       "Ledger precompute terms (pre_terms): 5,373,952 member-test candidates x 37 ops = 198,836,224; 5,406,720 member-bits x 4 = 21,626,880; program generation 2^32 flat; total 4,515,430,400 = 2^32.072 = 2^-67.2 of N. "
       "Working-set sizes are my model: the proof table (Section 14) has NO row for the precomputation working set and states 15 KB (3840 x 4 B) for one class; under the 32 B-per-word convention the same list is 122,880 B. The generator DAG size is from the shipped Prog class (max 1,535 nodes over the seven programs, 1,426 emitted instructions), priced at one 32 B word per node (a bound that ignores the scheduler's use lists). Nothing here was run as the real precompute on a counting machine.")
def rec(cell, q, num, notes, labels=("N",)):
    return dict(hash="sha256-38", row_i=None, row_j=None, object="working set of the precomputation", question=q, labels=list(labels), status="COMPUTED", number=num,
        source="our workflow: scan-once-wave2", own_test=True, evidence=EV, date="2026-10-12", lever=False, gain_bits=None,
        notes="universe cell %s. %s %s" % (cell, notes, KAT), topic="MEM.PRE38")
p = V['list_packed4B']; w = V['list_word32B']; g = V['gen_dag']; b = V['list_packed4B+gen_dag']; ww = V['list_word32B+gen_dag']
recs = {}
c = "sha256-38|MEM.PRE38|MEM|M2"
recs[c] = rec(c, "M2: exact ledger time to stream / recompute the precomputation working set instead of holding it",
  "Streaming is free in the ledger: the precompute is charged 4,515,430,400 ops (member tests 198,836,224 + plane writes 21,626,880 + generation 2^32) and that already writes each survivor straight into the planes (4 ops per member-bit), so a stream-only precompute adds 0 ops and time_log2 stays 87.90374. Holding the 3,840-member list instead adds 1 store + 1 load per survivor = 691,200 ops over 90 classes, i.e. < 2^-67 bit of time_log2 (below float resolution at 87.9); bytes added 15,360 (packed 4 B, the proof's '15 KB') or 122,880 (32 B per word).",
  "Time side is exact ledger arithmetic; the 691,200-op count for holding is my own count. Because the whole precompute is 2^-67.2 of the total, no recompute or stream choice for this object can move time_log2.")
c = "sha256-38|MEM.PRE38|MEM|M3"
recs[c] = rec(c, "M3: S-optimal hold-versus-recompute point for the precomputation working set with the others fixed",
  "Stream / reuse is S-optimal: S = 87.90374 at 1,045,792 B (headroom 2,784 B, memory term 0). Dedicated scratch costs S: member list packed 15,360 B -> B = %d, S = %.5f (+%.5f); list at 32 B/word 122,880 B -> B = %d, S = %.5f (+%.5f); generator DAG 49,120 B (1,535 nodes x 32) -> B = %d, S = %.5f (+%.5f); list(packed)+DAG -> S = %.5f (+%.5f). Time gain of holding < 2^-67 bit, so every hold loses." %
  (p['B'], p['S'], p['S']-R['S0'], w['B'], w['S'], w['S']-R['S0'], g['B'], g['S'], g['S']-R['S0'], b['S'], b['S']-R['S0']),
  "Exact peak stays 1,045,792 B only if the scratch is placed in memory that is dead at that moment: order the precompute so the plane region (675,840 B) is still unwritten while the programs are generated, and the code region (318,272 B) is still unwritten while the member lists are built; dead online scratch (broadcast planes 7,168 + spill 1,280 + scalars 2,048 = 10,496 B) plus headroom 2,784 = 13,280 B alone is NOT enough for the packed list (15,360 B). This reuse ordering is an argument, not a tested program; if the shipped program holds the list in a dedicated array the proof's 1,045,792 B total is short by that array and the figure would be a bound that fails (the +0.0172 bit row).", labels=("N","E"))
c = "sha256-38|MEM.PRE38|MEM|M4"
recs[c] = rec(c, "M4: breakpoint at 2^20 B for the precomputation working set, S on both sides, is crossing worth it",
  "Crossing is not worth it. Free room below 2^20 is 2,784 B. A dedicated packed list (15,360 B) crosses by %d B and costs %.5f bit (S %.5f vs 87.90374); the 32 B/word list crosses by %d B, %.5f bit; the generator DAG %.5f bit. Price at the break is 1.3759e-6 bit per byte; holding buys < 2^-67 bit, so the break-even working set is 2,784 B plus a negligible amount: no crossing pays." %
  (p['over'], p['mem_term'], p['S'], w['over'], w['mem_term'], g['mem_term']),
  "Below 2^20: stream or reuse dead memory, S = 87.90374. Above: S rises by log2(B/2^20) with no time return. The only open point (not tested) is whether the shipped precompute really streams or places its list in dead space; a package that holds the list as its own 15 KB array would sit at 1,061,152 B = 2^20.0172 and lose 0.0172 bit of S.", labels=("N","Z"))
os.makedirs('..', exist_ok=True)
sets = add_cell.load()
for cell, r in recs.items():
    fn = os.path.join('..', cell.replace('|', '_') + '.json')
    json.dump(r, open(fn, 'w', encoding='utf-8'), indent=1)
    add_cell.validate(json.load(open(fn, encoding='utf-8')), sets); print('ok', fn)
