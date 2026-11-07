
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

import json, sys, math, os
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/dig'))
import add_cell
D = _hca_public_path_text('__HCA_WORKSPACE__/research/dig/incoming2/sha256-38-G04-U04')
EV = "research/dig/incoming2/sha256-38-G04-U04/work/scan1.py, scan1.json, gprime.c, scan2.py, scan2_400.json, scan3.py, scan3.json, scan4.py, scan4.json (own code; a0lean38.py = copy of pkgR38M3 experiments/a0lean38.py)"
p7 = 287309824 / 2**32
G = 67108864
allF7 = G * p7
common = dict(hash="sha256-38", row_i=None, row_j=None, source="our workflow: scan-once-wave2", own_test=True,
              evidence=EV, date="2026-10-12", lever=False, gain_bits=None)
KNOWN = (" Known-answer first: both members of the published pair give equal 38-step digests, rows 0..33 cells and two-bit conditions hold, "
         "rows 34..37 equal; the Lemma 4.1 rebuild from (CV, published A0) returns the published W0..W13 of both members; the published a0 is in G, "
         "c7 = 8f6c89c5, W7x in F7; a0lean38 ledger arithmetic reproduces 135,063.19 ops per first block (2728 + 35 + 132300.19), T = 87.90374.")
recs = {}


def R(cid, **kw):
    d = dict(common)
    d.update(kw)
    d['notes'] = "universe cell " + cid + ". " + d['notes']
    recs[cid] = d


OBJ_A = "a0 family and the bijection W0..W5 <-> a0 (Lemma 4.1)"
OBJ_C = "class table of the first-block family"
R("sha256-38|CV.a0|CV|Q1", object=OBJ_A,
  question="Q1 count: how large is the A0-variant family G the attack draws from, the filed subset, and is W0..W5 <-> a0 a bijection?",
  labels=["D", "S"], status="COMPUTED", topic="CV.a0.count",
  number=("|G| = 67,108,864 = 2^26 (exact, all 2^32 values of W8x tested; a0 = W8C - C4 - W8x); 102,696 distinct c7 classes in G, largest size 3840, "
          "exactly 180 classes of size 3840; filed table = 90 of them (distinct c7, each full G-class has exactly 3840 members) = 345,600 = 2^18.40 variants; "
          "|F7| = 287,309,824 = 2^28.0977 (p7 = 2^-3.902), 6.0205 passing classes expected per first block (sampled 6.0149 over 3e6 random A_-1); "
          "W0 = a0 + k(CV): a0 recovered from W0..W5 and CV in 76,800 of 76,800 members (20 random CVs x one filed class of 3840), W0..W5 distinct per member, dW0..dW6 = 0 in 200 of 200."),
  notes=("Exact: G, F7, class sizes (full enumeration, numpy and C), the 90-class check. Sampled: passing classes per CV. G has 2^26 members, not the 12,103,680 of r37 (different W8 cell). "
         "The 90 filed classes are half of the 180 size-3840 classes." + KNOWN))
R("sha256-38|CV.a0|CV|Q2", object=OBJ_A,
  question="Q2 necessity: is the a0 family needed, and which of the conditions that define G does the collision need?",
  labels=["E", "S"], status="SAMPLED", topic="CV.a0.necessity",
  number=("(a) vary nothing (a0 = published only, V = 1): at least +12.80 bit (>= (2728 + 35 + 16.6)/p7 = 41,540 ops per good variant vs 5.84 shipped; lower bound, later work ignored). "
          "(b) The W8 XOR cell (mask 04400800 value 04400000 diff 04400800) is NOT needed: the modular set s0(W8+fbc00800)-s0(W8) = fe7f8000 has 68,157,440 members = G + 2^20 (+1.5625%); "
          "all 2^20 extra words satisfy the three printed W8 two-bit conditions and fail only the cell. SMC tail from the published rows (400 replicates x 24,576 tail trials, 512 variants each): "
          "log2 q3 = -97.757 +- 0.058 (G) vs -97.662 +- 0.055 (G' minus G); 3785 successes, all rebuilt to verified pairs (0 failed rebuilds). "
          "(c) W8 outside the modular set: 0 successes in 400 replicates (512 random words)."),
  notes=("Sampled (SMC of a0lean38.smc_replicate with VARIANTS replaced; shipped q3_used -97.7838). No gain at the memory line: variants are bound by 1 MiB (B = 1,045,792, headroom 2,784 B, "
         "7,509 B of planes per class), so +1.56% variants cannot be used without a memory penalty; ceiling if memory were free = log2(1.015625) = 0.0224 bit. "
         "Window: tail/SMC from the published S rows only (LOCAL to the published dense part), not a new search for S." + KNOWN))
R("sha256-38|CV.a0|CV|Q3", object=OBJ_A,
  question="Q3 freedom: how many bits of a0 freedom remain after the F7 gate and the row-16 filter, and is the row-16 pass count over G uniform?",
  labels=["N"], status="SAMPLED", topic="CV.a0.freedom",
  number=("a0 freedom: 26.00 bit in G (exact), 18.40 bit in the filed table. After the F7 gate (-3.902): %d = 2^%.2f variants per first block over all of G (exact product), 23,118.75 = 2^14.50 for the filed table. "
          "After row 16 (32 passing E16x words of 2^32): all of G expects 0.5 passes per CV before the gate and %.4f = 2^%.2f after it; filed table 1.72e-4 = 2^-12.5. "
          "Sampled row-16 passes over all of G, 36 random CVs: mean 0.556 (20 hits; expected 0.5), variance 0.52 (Poisson 0.5), none in the 90 filed classes (expected 0.1). Rows 0..3 free: 0 bit (A1..A3 fixed by S)."
          % (allF7, math.log2(allF7), 0.5 * p7, math.log2(0.5 * p7))),
  notes=("Exact: the products. Sampled: row-16 count (all 2^26 a0 evaluated for each of 36 CVs, every hit re-checked with the scalar e16x); small sample, no bias seen within +-0.12 (1 se). "
         "Freedom is not the limit: cost per good variant is 5.84 ops times the variants processed; using all of G would give 194x more good pairs per first block at 194x the plane work. "
         "Window: published S rows and its row-16 pass set (32 words)." + KNOWN))
R("sha256-38|CV.a0|CV|Q4", object=OBJ_A,
  question="Q4 alternatives: other ways to use the a0 family (larger G', other classes, cheaper evaluation)?",
  labels=["Z"], status="SAMPLED", topic="CV.a0.alternatives",
  number=("G' (modular-only W8 set) = 68,157,440 = 1.015625 x G: q3 unchanged within +-0.08 bit (see Q2); any larger family needs more plane memory (7,509 B per size-3840 class on average; headroom 2,784 B), "
          "so every added class loses at the 2^20 line (+0.0063 bit net for the 91st, see CV.classes Q4). Ceiling with unlimited memory 0.0329 bit. "
          "180 classes of size 3840, 816 of 3072, 2448 of 2048 exist in G (exact). No evaluation cheaper than 5.84 ops per good variant was found or tried (95.4% of the per-first-block ops are the class plane programs)."),
  notes=("Alternatives priced by the shipped ledger terms (per first block: w7 tests 1497.66, hit list 12.04, scalars+planes 278.94, classes 128,796.72, lanes 1714.34, row 16 0.49; 2728 + 35 fixed). "
         "Not tested: a solving (instead of scanning) route to a0 from the row-16 equation; E16x is nonlinear in a0 through S0(a0), MAJ(a0,a,b), S1(E0), CH(E0,e,f)." + KNOWN))
R("sha256-38|CV.classes|CV|Q2", object=OBJ_C,
  question="Q2 necessity: is the grouping of the filed variants by c7 (90 classes) needed, and what does it buy?",
  labels=["S", "Z"], status="COMPUTED", topic="CV.classes.necessity",
  number=("No grouping (each of the 345,600 variants tests its own W7 gate at 16.64 ops): at least 5,754,056 ops per first block vs 135,063 = +5.41 bit (lower bound: all later work ignored). "
          "The gate needs only c7 = W7x + A_-1, so equal c7 means one test (90 tests per first block = 1,497.7 ops = 1.109% of the per-first-block ops; the class plane work is 95.36%). Per good variant 5.84 ops. "
          "Measured gate clustering: over 3e6 random A_-1 the number of passing classes has mean 6.015 (6.0205 expected) but variance 111.9 (Poisson 6.0); P(none) = 0.69692 vs HIT0/2^32 = 0.69681."),
  notes=("Ledger arithmetic (COMPUTED) on a0lean38 ledger terms plus a 3e6-sample check of the gate (SAMPLED part: mean, variance, P(none)). "
         "Sharing the 90 W7 tests (pass events are strongly correlated) could save at most 1.109% = 0.0161 bit; not built, not tested." + KNOWN))
R("sha256-38|CV.classes|CV|Q4", object=OBJ_C,
  question="Q4 alternatives: more or fewer classes, other class sizes, other class selection?",
  labels=["Z"], status="COMPUTED", topic="CV.classes.alternatives",
  number=("Change in S = T + max(0, log2 B - 20) vs shipped (90 classes, B = 1,045,792 = 2^19.996), positive = worse: K=45 +0.0321; 60 +0.0162; 80 +0.0041; 89 +0.0004; "
          "91 +0.0063 (T -0.00036, penalty +0.0066); 100 +0.094; 120 +0.273; 150 +0.506; 180 +0.706 (T gain only -0.0163). Unlimited K with free memory: T -0.0329 only. "
          "90 is the memory-line optimum; classes of other sizes (3072: 816 exist, 2048: 2448) cost the same ~5.6 ops per variant and ~2 B of planes per variant, so they do not change this."),
  notes=("Ledger arithmetic: T ~ log2((2728 + 35 + 278.94 + K x 1466.90)/K); memory per class = 7,509 B planes average + 96 B table (from the 90 filed masks: 675,840 B planes). "
         "Assumes a new class costs the average of the filed ones. Not built, not run through the full ledger calibration." + KNOWN))
for cid, r in recs.items():
    fn = os.path.join(D, cid.replace('|', '_').replace('/', '_') + '.json')
    json.dump(r, open(fn, 'w', encoding='utf-8'), indent=1)
    print(fn, add_cell.validate(json.load(open(fn, encoding='utf-8')), add_cell.load()))
