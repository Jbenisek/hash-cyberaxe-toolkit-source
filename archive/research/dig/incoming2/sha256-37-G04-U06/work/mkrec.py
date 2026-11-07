
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
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/dig'))
import add_cell
out = _hca_public_path_text('__HCA_WORKSPACE__/research/dig/incoming2/sha256-37-G04-U06')
W = 'research/dig/incoming2/sha256-37-G04-U06/work/'
TOOL = ("Tool " + W + "blk.c (own; common.h = own SHA-256 trace + chi37 parser copied from retest/dense_boring; chi37.txt copy). "
  "Validated on known answers first: 64-step chain of a 128-byte message with the FIPS padding block equals Python hashlib sha256 (d2742f1f...8cf6); "
  "the 37-step block-2 digests of the published pair equal the printed digest a856d46e...80954580 and the equal padding block gives equal block-3 digests (68f6e1a5...3a5b); "
  "own G enumeration gives 12,103,680 variants / 22,976 c7 classes (printed values); closed-form W6/W7 gate equals a full recompute on 2,000,000 random (CV, a0) with 0 mismatches, "
  "and redrawing CV words 2..7 changes W6/W7 in 0 of 200,000. Assumption: sha256-37 = 37-step compression with feed-forward, Merkle-Damgard, IV, FIPS 180-4 padding (as the unit brief states). ")
base = dict(hash="sha256-37", row_i=None, row_j=None, source="our workflow: scan-once-wave2", own_test=True,
            date="2026-10-12", lever=False, gain_bits=0.0, gain_basis="T")
recs = {}
def R(cell, **kw):
    d = dict(base); d.update(kw); d['notes'] = "universe cell " + cell + ". " + d['notes']; recs[cell] = d

R("sha256-37|CV.BLKn|CV|Q1", status="COMPUTED", labels=["N"],
  object="CV.BLKn block count and layout of the colliding messages",
  question="Q1 count/size of the layout as the attack uses it: how many data blocks, padding blocks and compressions, and what is in each.",
  topic="G04 block layout count",
  evidence=W+"blk.c; "+W+"val.out; "+W+"lens.out; "+W+"gdist_k0.out",
  number="EXACT: 128-byte messages M0||M1 and M0||M1' = 2 data blocks + 1 FIPS padding block = 3 compressions per member (block 1 shared, so 5 distinct F_37 calls for a verified pair, 6 if block 1 is recomputed). Block 3 = W0=80000000, W1..W13=0, W14=00000000, W15=00000400 (bit length 1024), identical in both members. Block 2 uses all 16 words as data: required dW14=fc3ff800, dW15=e0000000 (y-x) are nonzero. Published pair as block 2 under the printed CV: both digests a856d46e4b46eb284935248c92a2fc98e0fb261010a9951f54264f5b80954580 (equal); after the equal padding block both are 68f6e1a5e971d8b49547465afe49430652dcf6b6a0a7dbcc3aa7dd4c992a3a5b (equal). Cost per first-block trial: 1 compression (block 1 only); blocks 2 and 3 are run only on a hit: 4 compressions (2 members x 2 blocks), about 2^-59 of T = 2^61.18, i.e. under 1e-17 bit. Time and memory effect of the layout: 0 bit, 0 bytes (score = time_log2 + max(0, log2(mem)-20) is not moved).",
  notes=TOOL+"Method: val mode (compress 37 and 64 steps, padblock), published pair run through the 3-block layout. Not tested: an organizer harness run of the 3-block hash on a real collision (none exists below 2^61); the 37-step-per-block reading of the hash is the brief's, not independently confirmed here.")

R("sha256-37|CV.BLKn|CV|Q2", status="KILLED", labels=["K","Z"],
  object="CV.BLKn necessity: drop the first block or put the padding in the colliding block",
  question="Q2 necessity: replace the layout (a) padding inside the colliding block (2 compressions, no pad block), (b) colliding block directly on the IV (no M0), and recompute the exact event.",
  topic="G04 block layout necessity",
  evidence=W+"blk.c; "+W+"lens.out; "+W+"iv.out; "+W+"ivcheck.out",
  number="(a) EXACT 0: padding can share the colliding block only if the member has a tail <= 55 bytes in it, so W14/W15 are the length words. Over all 12,544 ordered length pairs (L,L') in 0..119 bytes with padding inside the final block, 0 give dW14=fc3ff800 and dW15=e0000000 (equal lengths, 112 pairs, give dW14=dW15=0; the largest reachable |dW15| is 952 bits vs the required 3,758,096,384). So a third (padding) block is forced. (b) EXACT: with CV = IV (a=6a09e667, b=bb67ae85) no c7 class of the 22,976 passes F7 (g_all(IV)=0, g_222(IV)=0, classes passing 0 of 22,976), so a colliding block directly on the IV has no good variant at all; mean over random CV is g_all=12,848.77. M0 is necessary for this characteristic family. A single CV also cannot supply the search: expected collisions per live CV = g x q3 = about 2^13 x 2^-74 = 2^-61 (q3 from own S37-DB-P0FACTS SMC 2^-73.994 +- 0.015), so about 2^61 first blocks are needed regardless.",
  notes=TOOL+"Method: lens mode (enumeration of length pairs, high length word 0 for L<2^29), iv mode (gate on A_-1=6a09e667, A_-2=bb67ae85 over all 22,976 classes, then all variants of passing classes). The statement covers the chi37 / G family (E4[31:29]=000) only; another characteristic could allow other layouts (not tested). Alternative of a nonzero dCV (CV.diff cell) not part of this unit.")

R("sha256-37|CV.BLKn|CV|Q3", status="SAMPLED", labels=["N","B"],
  object="CV.BLKn freedom left per first block",
  question="Q3 log2 freedom left: how many good (a0) variants g does one random first block give, and how is g distributed (the gate depends on which CV words)?",
  topic="G04 g per first block",
  evidence=W+"blk.c; "+W+"gdist_k0.out; "+W+"gdist_k2.out; "+W+"ivcheck.out",
  number="First block M0: 512 free bits, CV 256 bits, but the gate F7/F6 reads only A_-1 and A_-2 (64 bits; 0 changes of W6/W7 in 200,000 redraws of the other six words). Over 2^18 real first blocks F_37(IV,M0) (seed 101): mean g_all = 12,839.0 +- 77.5 (1 se) vs exact E = 12,103,680 x 2^-5.978 x 2^-3.902 = 12,848.77 (matches, -0.13 se). Dispersion is huge: sd 39,669, cv 3.09; P(g_all=0) = 0.7196 (so 28.04% of first blocks carry all pairs; 62.7% have no F7-passing class, mean classes passing 365.6 vs exact 364.6, sd 657.7); top 5% of blocks carry 61% of all pairs, top 10% carry 84%. For the 222 classes >= 3456 (782,800 variants): mean g_222 = 833.0 +- 8.6 (exact 782,800 x p7 x p6 = 831 per the unit text), P(g_222=0) = 0.9249, cv 5.26, max 155,112. Maximum g_all seen 1,037,928. log2 mean g_all = 13.65, log2 mean g_222 = 9.70.",
  notes=TOOL+"Method: gdist mode, 2 threads, 155 s. The class-only stand-in with CV 0..0.4 used by the earlier w7_xskip smoke is far below the real dispersion 3.09; whether skipping helps depends on how much of the per-block cost does not scale with g (in the ledger the data-dependent part is charged per passing class, so a gain is not implied and none is claimed). SAMPLED: intervals above are 1 se of the mean; 2^18 blocks.")

R("sha256-37|CV.BLKn|CV|Q4", status="SAMPLED", labels=["Z"],
  object="CV.BLKn alternatives: layouts compared",
  question="Q4 alternatives: difference block as block 3 of a longer message, free extra block between, CV=IV, padding in block 2: counted per layout.",
  topic="G04 block layout alternatives",
  evidence=W+"blk.c; "+W+"lens.out; "+W+"iv.out; "+W+"gdist_k0.out; "+W+"gdist_k1.out; "+W+"padcorr.out",
  number="Layouts (cost per CV trial in F_37 compressions; all equal where feasible): L2 current M0||M1||pad = 1 per trial, 3 per member at the end. L3 M0*||X||M1||pad with M0* fixed and X free = 1 per trial (compress of X from the cached CV of M0*), 4 per member at the end; the g distribution of its CVs equals L2 (2^18 each: mean g_all 12,872.5 +- 77.9 vs 12,839.0 +- 77.5, P(g=0) 0.7192 vs 0.7196, two-sample KS D=0.00123, p=0.989). Uniform (A_-1,A_-2) draws also match (KS p=0.996). L1 colliding block on the IV (2 compressions): infeasible, g(IV)=0. L0 padding inside the colliding block: infeasible, 0 of 12,544 length pairs. A difference block placed as block 3 of a longer message is L3 with the free block before it: same trial cost 1, no gain. Net: no layout lowers the per-trial cost below 1 compression; gain 0.",
  notes=TOOL+"Method: gdist kinds 0,1,2 (real F37(IV,M0), F37(F37(IV,M0*),X), uniform words), scipy ks_2samp on the per-CV g_all lists. Prefix reuse between sibling X (shared words) is a separate lever already in LEVERS.md (w7_fb_prefix, -0.007 bit); not rerun. A layout with a nonzero chaining-value difference is the CV.diff cell, outside this unit.")

R("sha256-37|CV.BLK3|CV|Q1", status="COMPUTED", labels=["N"],
  object="CV.BLK3 third block (the FIPS padding block) as the attack uses it",
  question="Q1 count/size of the third block: contents, number of compressions, when it is computed.",
  topic="G04 third block count",
  evidence=W+"blk.c; "+W+"val.out",
  number="EXACT: 1 block of 64 bytes, constant: W0=80000000, W14=00000000, W15=00000400, the rest 0. Computed twice (once per member) and only on a hit; input CV2 equal in both members iff the 8 digest words of block 2 are equal, and then the output is equal: published pair, block 2 digest a856d46e...80954580 (equal), block 3 digest 68f6e1a5e971d8b49547465afe49430652dcf6b6a0a7dbcc3aa7dd4c992a3a5b (equal). Cost 2 compressions = 2^1 of T = 2^61.18 (about 2^-60.2 relative, 1e-18 bit).",
  notes=TOOL+"The padding block built by padblock(128) was checked against hashlib on a 128-byte message with 64 steps.")

R("sha256-37|CV.BLK3|CV|Q2", status="LOCAL_ONLY", labels=["K","Z"],
  object="CV.BLK3 necessity of the third block; can it act as a correction block",
  question="Q2 necessity: drop the third block (impossible under FIPS padding, shown in the BLKn Q2 cell) or replace its role: can the equal padding block absorb a small chaining-value difference left by block 2?",
  topic="G04 third block necessity",
  evidence=W+"blk.c; "+W+"padcorr.out; "+W+"lens.out",
  number="Drop: EXACT impossible for a 128-byte message (0 of 12,544 length pairs fit the padding into the colliding block). Replace by a correction block: 9,873,600 tests (300 random CV2; per CV2 all 32,896 XOR differences of weight 1-2 plus the 16 +-1 per-word differences) through F_37 with the fixed padding block: 0 equal outputs, minimum output XOR weight 87 of 256, mean 128.00. So block 3 only carries an existing collision forward (dCV2 must be 0); it cannot reduce a near-collision. 0 bit.",
  notes=TOOL+"Method: padcorr mode. LOCAL_ONLY: low-weight differences on random CV2 only; large structured dCV2 and chosen CV2 not tested (that is CV.diff, outside this unit).")

R("sha256-37|CV.BLK3|CV|Q3", status="SAMPLED", labels=["N"],
  object="CV.BLK3 freedom of an extra free block",
  question="Q3 log2 freedom left if a free extra block X is inserted: how many bits it adds and whether the CV it produces is as good as a first block.",
  topic="G04 extra free block freedom",
  evidence=W+"blk.c; "+W+"gdist_k1.out; "+W+"gdist_k0.out",
  number="Padding block: 0 free bits (constant). Extra free block X after a fixed M0*: 512 free bits, but only 64 bits (A_-1, A_-2) are read by the gate; needed about 2^61 first blocks (g x q3 = 2^-61 per live CV), available 2^512 X values and 2^64 gate states. Quality: 2^18 CVs F_37(F_37(IV,M0*),X): mean g_all 12,872.5 +- 77.9 (exact 12,848.8), P(g_all>0) = 0.2808, P(g_222>0) = 0.0760, equal to the one-block case (0.2804, 0.0751): KS D=0.00123 p=0.989. Live set: 28.0% of CVs. No freedom is lost or gained by the extra block.",
  notes=TOOL+"SAMPLED, 2^18 per kind, one fixed M0* (seed 101); a second M0* not tried. Gate-state count 2^64 vs 2^61 blocks needed is plain arithmetic from the ledger q3.")

R("sha256-37|CV.BLK3|CV|Q4", status="SAMPLED", labels=["Z"],
  object="CV.BLK3 alternatives for the third block",
  question="Q4 alternatives: another third-block content or place (extra free block between, difference block as block 3, longer message) and their cost.",
  topic="G04 third block alternatives",
  evidence=W+"blk.c; "+W+"gdist_k1.out; "+W+"padcorr.out; "+W+"lens.out",
  number="(i) Free extra block between M0* and M1: trial cost 1 compression (cached prefix), g distribution identical (KS p=0.989), end-state 4 compressions per member: 0 bit. (ii) Difference block as block 3 of a longer message: identical to (i) (the block before it is the free block): 0 bit. (iii) Padding content cannot be changed (FIPS length 1024 bits fixed by the 128-byte message; a longer message only changes W15 and the block count, both equal in the two members): 0 bit. (iv) Padding block as correction block: 0 of 9,873,600 low-weight tests. No alternative lowers T or memory.",
  notes=TOOL+"Same limits as the Q2/Q3 cells; prefix-sharing of sibling X blocks is in LEVERS.md (w7_fb_prefix).")

for cell, d in recs.items():
    fn = cell.replace('|', '_') + '.json'
    p = os.path.join(out, fn)
    json.dump(d, open(p, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    errs = add_cell.validate(json.load(open(p, encoding='utf-8')), add_cell.load())
    print(fn, errs)
