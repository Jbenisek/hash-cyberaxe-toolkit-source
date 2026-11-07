
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
R = json.load(open('results.json'))
EV = ("research/dig/incoming2/sha256-38-G02-U02/work/g02u02.py; research/dig/incoming2/sha256-38-G02-U02/work/run_all.py; "
      "research/dig/incoming2/sha256-38-G02-U02/work/results.json; research/dig/incoming2/sha256-38-G02-U02/work/a0lean38.py (copy of pkgR38M3 experiments/a0lean38.py); "
      "research/tools/build_pkg/scratch/pkgR38M3/pkg/sha256-r38/proof.md Sections 5.1, 9.3, 11, 14")
KAT = ("Known-answer check: a0lean38.py ledger reproduces time_log2 87.90374 (log2(N/C) = 87.9037359544, N = 789779068018615953003308365799) and memory() reproduces 1,045,792 B = 2^19.9962 "
       "(r38 convention: 32 B per instruction; 57 instruction slots for the W7 loop, 9,946 for the seven plane programs, 600 other). Variants are the same ledger source with one hook changed; "
       "the no-change run gives the same N. Per first block 2728 + 35 + 132300.186 = 135,063.19 primitives. Exact HIT0 (none of the 90 classes passes) kept from the ledger; counts are exact ledger arithmetic, memory sizes exact sums, the bitmap test count is my own count.")
F, P, H = R['F7T'], R['PL90'], R['SHC']
T0 = 87.90373595441501


def rec(cell, obj, q, num, notes, labels=("N",), topic=None):
    return dict(hash="sha256-38", row_i=None, row_j=None, object=obj, question=q, labels=list(labels), status="COMPUTED", number=num,
                source="our workflow: scan-once-wave2", own_test=True, evidence=EV, date="2026-10-12", lever=False, gain_bits=None,
                notes="universe cell %s. %s %s" % (cell, notes, KAT), topic=topic)


recs = {}
c = "sha256-38|MEM.F7T|MEM|M3"
recs[c] = rec(c, "F7 decision tree (memory-free W7 test)", "M3: S-optimal hold-versus-recompute point for the F7 test with the others fixed",
              "Shipped tree loop is S-optimal: S = 87.90374 at 1,045,792 B (memory term 0). Hold bitmap (2^29 B): S = %.3f (T %.5f, -%.5f bit; memory term %.3f). Unrolled 90 trees: T %.5f (-%.5f), B %d, S %.5f. Free-test floor: T %.5f, at most -%.5f bit within the 2,784 B headroom." %
              (F['bitmap']['S'], F['bitmap']['T'], F['bitmap']['dT'], F['bitmap']['S'] - F['bitmap']['T'], F['unrolled']['T'], F['unrolled']['dT'], F['unrolled']['B'], F['unrolled']['S'], F['freetest_bound']['T'], F['freetest_bound']['dT']),
              "Hold = the base's 2^32-bit bitmap (2^29 B). The bitmap test is priced at 13 primitives per class (load c7, sub, shift, load word, and, shift, and, branch 2, counter, pointer, loop branch 2; vs 16.640625 for the tree) - my count, so the bitmap T is a model value; even a free W7 test (0 primitives incl. loop and counter) saves only 0.016069 bit, so no table of any size can beat the tree by more than that (bound). Headroom under 2^20 is 2,784 B; any table that fits there is worth at most 0.016 bit (not built or priced).", topic="MEM.F7T")
c = "sha256-38|MEM.F7T|MEM|M4"
recs[c] = rec(c, "F7 decision tree (memory-free W7 test)", "M4: breakpoint at 2^20 B for the F7 test code, S on both sides, is crossing worth it",
              "Crossing is not worth it. Below: loop, 1,045,792 B, S = 87.90374. Above: 90 unrolled trees (4 loop primitives per class saved, 360 per first block), B = 1,193,728 (+147,936), T = %.5f (-%.5f), S = %.5f (+%.5f vs shipped). Break-even: the unrolled gain pays only up to %.0f B total (about %.0f B over 2^20)." %
              (F['unrolled']['T'], F['unrolled']['dT'], F['unrolled']['S'], F['unrolled']['S'] - T0, F['breakeven_total_B_unrolled'], F['breakeven_total_B_unrolled'] - 2**20),
              "Marginal price of memory at 2^20 is 1.3759e-6 bit per byte; the unrolled variant costs 0.18319 bit of memory term for 0.00385 bit of time. Even a free W7 test (0.01607 bit) pays for at most %.0f B above 2^20." % (F['breakeven_B_freetest'] - 2**20), labels=("N", "Z"), topic="MEM.F7T")
c = "sha256-38|MEM.PL90|MEM|M2"
m2 = P['M2']
recs[c] = rec(c, "batch planes of the 90 classes (15 batches, one word per variable bit of a0)", "M2: exact ledger time to recompute / stream the planes of a passing class instead of holding all 90",
              "Rebuilding the planes of each passing class costs %.0f primitives per class (mean; %.0f member tests + 4 x 3840 x v plane builds, v = 15..17 variable bits), %.0f expected per first block (6.0205 passing classes) vs 135,063 now. time_log2 %.5f (+%.5f bit); B = %d (scratch %d B for one class); S = %.5f (+%.5f vs shipped 87.90374). Streaming is a loss of %.2f bit." %
              (P['M2_sub']['per_class_ops_mean'], P['M2_sub']['member_tests_mean'], P['expected_recompute_ops_per_FB'], m2['T'], m2['dT'], m2['B'], m2['scratch'], m2['S'], m2['dS'], m2['dS']),
              "Recompute uses the package's own precomputation formula (pre_terms: 2^|mask| candidates x 37 primitives, the longest path of member_test, plus 4 primitives per member-bit), charged to every passing class; the one-time 4.2e8-primitive precompute is removed from PRE (2^32 for program generation kept), and the cap constants (class max) include the rebuild. B falls below 2^20 so there is no memory term to gain: S rises by the full time loss. Not tried: a cheaper incremental way to enumerate the 3840 members (would need a new method).", topic="MEM.PL90")
c = "sha256-38|MEM.PL90|MEM|M4"
m4 = P['M4']
recs[c] = rec(c, "batch planes of the 90 classes (15 batches, one word per variable bit of a0)", "M4: breakpoint at 2^20 B for the class planes, S on both sides, is crossing worth it",
              "Crossing is not worth it. A marginal class costs %.0f B of planes+constants+table (min %d) and earns %.6f bit (best class %.6f, per KB %.2e); crossing 2^20 by it costs %.5f bit of memory term (%.5f net loss for the best class); price at the break is %.5f bit per KB." %
              (m4['avg_bytes'], m4['min_bytes'], m4['avg_gain'], m4['max_gain'], m4['gain_per_KB_avg'], m4['avg_pen_cross'], -m4['best_net'], m4['pen_per_KB']),
              "Marginal class measured by dropping each of the 90 classes in turn from the exact ledger (K = 89, N_FB recomputed, HIT0 kept so the 278.94-primitive per-first-block term moves by < 1e-6 bit) and pricing its bytes = 15 x v x 32 + shared words x 32 + 96 (table); adding a class is taken as the mirror image. Headroom under 2^20 is 2,784 B < any class (min 7,424 B), so the 90-class schedule sits on its boundary. The schedule note says a 91st class in the three shapes does not exist and a new shape needs ~45 KB of program: not priced here. Hold vs stream above 2^20: holding all planes at 2^20 would cost %.3f bit of memory term vs +6.78 bit to stream, so hold wins on both sides." % P['hold_pen_at_2e20'], labels=("N", "Z"), topic="MEM.PL90")
sm = H['M2']
c = "sha256-38|MEM.SHC|MEM|M2"
recs[c] = rec(c, "shared-constant words of the classes", "M2: exact ledger time to rebuild the shared-constant words of a passing class instead of holding them",
              "Rebuilding the 4 constant words per passing class (3 primitives to form 0 - ((base >> j) & 1) plus 1 store each; 360 words over the 90 classes) costs %.3f primitives per first block; time_log2 %.5f (+%.6f bit); B = %d (-11,520 + %d B scratch). S = %.5f (+%.6f)." %
              (sm['exp_ops_per_FB'], sm['T'], sm['dT'], sm['B'], sm['scratch'], sm['S'], sm['S'] - T0),
              "Words are the P:C<j> constants of ClassData (ONES or 0 per shape bit not in the mask); the class table already holds base, so they can be formed from it. The 4-primitive price per word is my own count (not an allocator listing); the plane programs still load the words from a small scratch as now. B is under 2^20 either way, so no memory term is gained.", topic="MEM.SHC")
c = "sha256-38|MEM.SHC|MEM|M3"
recs[c] = rec(c, "shared-constant words of the classes", "M3: S-optimal hold-versus-recompute point for the shared-constant words with the others fixed",
              "Hold is S-optimal at the shipped point: B = 1,045,792 < 2^20 so the 11,520 B are free; S(hold) = 87.90374 vs S(rebuild) = %.5f. Above 2^20 rebuild wins once the program exceeds 2^20 by %.0f B (hold minus rebuild S: %.5f at 2^20+5,000 B, %.5f at 2^20+20,000 B)." %
              (sm['S'], H['over_bytes_breakeven'], H['S_hold_minus_rec_at_2e20+5000'], H['S_hold_minus_rec_at_2e20+20000']),
              "Rebuilding frees 11,360 B net (headroom 2,784 -> 14,144 B) at a cost of 0.001027 bit; that headroom would only pay if spent on something worth more than 0.001027 bit (the best conceivable F7 table is worth <= 0.016 bit, not built).", topic="MEM.SHC")
c = "sha256-38|MEM.SHC|MEM|M4"
recs[c] = rec(c, "shared-constant words of the classes", "M4: breakpoint at 2^20 B for the shared-constant words, S on both sides, is crossing worth it",
              "Break-even is at %.0f B over 2^20: at or below 2^20 hold wins (memory free); once the program is above 2^20 by more than that, rebuilding (+0.001027 bit) beats holding (11,360 B net is worth up to %.5f bit of memory term). The shipped 1,045,792 B is 2,784 B below, so no crossing is made." %
              (H['over_bytes_breakeven'], H['full_cross_penalty']),
              "S(hold) - S(rebuild) = -0.001027 + [log2(B/2^20)]+ - [log2((B-11,360)/2^20)]+, from the exact ledger rerun; values in the M3 record.", labels=("N", "Z"), topic="MEM.SHC")

d = _hca_public_path_text('__HCA_WORKSPACE__/research/dig/incoming2/sha256-38-G02-U02')
ex = add_cell.load()
for cell, r in recs.items():
    fn = os.path.join(d, cell.replace('|', '_') + '.json')
    json.dump(r, open(fn, 'w', encoding='utf-8'), indent=1)
    print(os.path.basename(fn), add_cell.validate(json.load(open(fn, encoding='utf-8')), ex))
