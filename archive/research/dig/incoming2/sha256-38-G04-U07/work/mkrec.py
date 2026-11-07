
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

import json, os, sys, re
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/dig'))
import add_cell
out = _hca_public_path_text('__HCA_WORKSPACE__/research/dig/incoming2/sha256-38-G04-U07')
W = 'research/dig/incoming2/sha256-38-G04-U07/work/'
k2 = ''
try:
    t = open(out + r'\work\out38.txt', encoding='utf-8').read()
    m = re.search(r'kind 2 .*?\n(g_all[^\n]*)\n(g_90[^\n]*)', t, re.S)
    if m: k2 = ' Uniform-A_-1 control (kind 2, same seed): ' + m.group(1)[:200] + ' | ' + m.group(2)[:200] + '; KS on g_all vs real first blocks D=0.00245 p=0.41, vs extra-block CVs p=0.97.'
except Exception as e:
    pass
TOOL = ("Tool " + W + "blk38.c (own; common.h = own SHA-256 trace + chi38 parser from U01, chi38.txt copy). Validated on known answers first: 64-step chain of a 128-byte message "
  "with the FIPS padding block equals Python hashlib sha256 (d2742f1f...8cf6); the 38-step 3-block digest of the same message equals the organizer verifier hash_functions.digest(m,'sha256',38) (ff4945c1...9590); "
  "the 38-step block-2 digests of the published pair equal the printed digest 5d9ca5f4...90645c4d and the equal padding block gives equal block-3 digests (1df71bae...cc3c); "
  "own exhaustive G enumeration over W8x in 2^32 gives 67,108,864 variants / 102,696 c7 classes, largest class 3,840, all 90 filed classes found; "
  "closed-form W7 = c7(a0) - A_-1 equals a full recompute (ref_words) on 2,000,000 random (CV, a0) with 0 mismatches; the published a0 reproduces W0..W13 and lies in G and F7. "
  "Assumption: sha256-38 = 38-step compression with feed-forward, Merkle-Damgard, IV, FIPS 180-4 padding (checked against the verifier). ")
base = dict(hash="sha256-38", row_i=None, row_j=None, source="our workflow: scan-once-wave2", own_test=True,
            date="2026-10-12", lever=False, gain_bits=0.0, gain_basis="T")
recs = {}
def R(cell, **kw):
    d = dict(base); d.update(kw); d['notes'] = "universe cell " + cell + ". " + d['notes']; recs[cell] = d

R("sha256-38|CV.BLKn|CV|Q1", status="COMPUTED", labels=["N"],
  object="CV.BLKn block count and layout of the colliding messages",
  question="Q1 count/size of the layout as the attack uses it: data blocks, padding blocks, compressions, contents.",
  topic="G04-38 block layout count",
  evidence=W+"blk38.c; "+W+"out38.txt",
  number="EXACT: 128-byte messages M0||M1 and M0||M1' = 2 data blocks + 1 FIPS padding block = 3 compressions per member (block 1 shared: 5 distinct F_38 calls for a verified pair). Block 3 = W0=80000000, W1..W13=0, W14=00000000, W15=00000400 (bit length 1024), identical in both members. Block 2 uses all 16 words as data; required dW14=00000000 (y-x), dW15=fc400800 (nonzero; 38 differs from 37 where dW14 is also nonzero). Published pair under the printed CV: both block-2 digests 5d9ca5f459ace3a3...90645c4d (equal, = printed digest); after the equal padding block both are 1df71baea9f997c673aa936c26aa81ee78140597fdc08ee34175c7e9e852cc3c (equal). Cost: 1 compression per first-block trial (block 1 only); blocks 2 and 3 run only on a hit (4 compressions). Hits are about 2^-97.8 per variant (ledger q3), so the layout costs nothing measurable: 0 bit, 0 bytes of memory.",
  notes=TOOL+"Method: val mode (38 and 64 steps, padblock), published pair through the 3-block layout. Not tested: an organizer-harness run of the 3-block hash on a real collision (none exists below ~2^98 work); the 38-step-per-block reading of the hash was confirmed against hash_functions.digest on one 128-byte message only.")

R("sha256-38|CV.BLKn|CV|Q2", status="KILLED", labels=["K","Z"],
  object="CV.BLKn necessity: padding inside the colliding block; colliding block directly on the IV",
  question="Q2 necessity: replace the layout (a) padding inside the colliding block (no pad block), (b) colliding block directly on the IV (no M0), and recompute the exact event.",
  topic="G04-38 block layout necessity",
  evidence=W+"blk38.c; "+W+"out38.txt",
  number="(a) EXACT 0 of 12,544 ordered length pairs (L,L') in 0..119 bytes with the padding in the final block give dW14=00000000, dW15=fc400800 (112 equal-length pairs give dW14=dW15=0; the largest reachable |dW15| is 952 bits vs required 4,232,054,784 = 0xfc400800 mod 2^32). The required dW15 needs L'-L = 529,006,848 bytes (2^28.98) or more, and members of different length cannot share a CV before the last block without a prefix collision. So the padding block is forced. (b) Unlike sha256-37, the gate does NOT fail at the IV: A_-1 = 6a09e667 gives g_all = 4,771,488 variants in 4,376 classes (random-CV mean 4,489,216 / 6,870) and g_90 = 122,880 variants (32 of the 90 filed classes). But one CV cannot supply the search: g_90 x q3 = 2^16.9 x 2^-97.78 = about 2^-80.9 expected hits, so about 2^81 distinct first blocks are still needed. M0 is necessary as the supply of CVs, not as a gate fix.",
  notes=TOOL+"Method: lens mode (length pairs, high length word 0 for L<2^29), iv mode (gate x = c7 - A_-1 in F7 over all 102,696 classes). q3 = 2^-97.7838 is the a0lean38.py ledger default, not remeasured here. Statement covers the chi38 / G family only. A nonzero chaining-value difference (CV.diff) is not part of this unit.")

R("sha256-38|CV.BLKn|CV|Q3", status="SAMPLED", labels=["N","B"],
  object="CV.BLKn freedom left per first block",
  question="Q3 log2 freedom left: how many good (a0) variants g does one random first block give, and how is g distributed (which CV words does the gate read)?",
  topic="G04-38 g per first block",
  evidence=W+"blk38.c; "+W+"out38.txt",
  number="Family G (own exhaustive count): 2^26 = 67,108,864 variants in 102,696 c7 classes (largest 3,840); the 90 filed classes hold 345,600 of them (0.51%). Gate: W7x = c7(a0) - A_-1 in F7 (|F7| = 287,309,824 = 2^28.10, p = 0.066895), reads ONLY A_-1 (32 bits): redrawing words 2..7 or A_-2 changes W7 in 0 of 200,000. (E16x, the row-16 filter downstream, reads the whole CV: it changed in 200,000 of 200,000 redraws.) Over 2^18 real first blocks F_38(IV,M0) (seed 101): mean g_all = 4,489,468 +- 459 (1 se) vs exact 4,489,216 (log2 22.10), cv 0.052, min 4,034,560, max 5,160,688, P(g_all=0) = 0; classes passing F7 mean 6,870.2 vs exact 6,869.8. For the 90 filed classes: mean g_90 = 23,188.9 +- 79.5 vs 23,119 expected (log2 14.50), sd 40,712, cv 1.756, P(g_90=0) = 0.6964 (only 30.4% of first blocks carry any filed-class variant), q95 122,880, max 149,760. So per CV there are 2^22.1 gate-passing variants in G but the filed program can use 2^14.5 on average, concentrated in 30% of the blocks.",
  notes=TOOL+"Method: gdist mode, 2 threads, 903 s (machine loaded). SAMPLED: intervals are 1 se of the mean; 2^18 blocks, one seed. Difference to sha256-37: there the gate read A_-1 and A_-2 and was dispersed (cv 3.09); here it reads A_-1 alone and g_all is nearly constant, the dispersion is only in the 90-class subset.")

R("sha256-38|CV.BLKn|CV|Q4", status="SAMPLED", labels=["Z"],
  object="CV.BLKn alternatives: layouts compared",
  question="Q4 alternatives: difference block as block 3 of a longer message, free extra block between, CV=IV, padding in block 2.",
  topic="G04-38 block layout alternatives",
  evidence=W+"blk38.c; "+W+"out38.txt; "+W+"ks.out",
  number="Cost per CV trial in F_38 compressions: L2 current M0||M1||pad = 1 per trial, 3 per member at the end. L3 M0*||X||M1||pad (M0* fixed, X free) = 1 per trial (X compressed from the cached CV of M0*), 4 per member at the end; g_all distribution equal to L2 (2^18 each: mean 4,489,226 vs 4,489,468; g_90 mean 23,107.3 vs 23,188.9, P(g_90=0) 0.6969 vs 0.6964; two-sample KS on g_all D=0.00209, p=0.61). L1 colliding block on the IV (2 compressions): gate passes (g(IV)=4,771,488) but supplies about 2^-80.9 hits per CV, infeasible. L0 padding inside the colliding block: 0 of 12,544 length pairs. A difference block as block 3 of a longer message is L3 with the free block before it: same trial cost 1. Net: no layout lowers the per-trial cost below 1 compression; gain 0 bit."+k2,
  notes=TOOL+"Method: gdist kinds 0 (real F38(IV,M0)) and 1 (F38(F38(IV,M0*),X)), scipy ks_2samp on per-CV g_all. Prefix reuse between sibling X blocks is a separate lever already in LEVERS.md (w7_fb_prefix); not rerun. Nonzero-dCV layouts are the CV.diff cell, outside this unit.")

R("sha256-38|CV.BLK3|CV|Q1", status="COMPUTED", labels=["N"],
  object="CV.BLK3 third block (the FIPS padding block) as the attack uses it",
  question="Q1 count/size of the third block: contents, number of compressions, when computed.",
  topic="G04-38 third block count",
  evidence=W+"blk38.c; "+W+"out38.txt",
  number="EXACT: 1 block of 64 bytes, constant: W0=80000000, W1..W13=0, W14=00000000, W15=00000400, no free bit. Computed twice (once per member), only on a hit; its input CV2 is equal in both members iff the 8 digest words of block 2 are equal, and then its output is equal: published pair block-2 digest 5d9ca5f4...90645c4d (equal), block-3 digest 1df71baea9f997c673aa936c26aa81ee78140597fdc08ee34175c7e9e852cc3c (equal). Cost 2 compressions per hit, hits ~2^-97.8 per variant: negligible (< 1e-28 bit).",
  notes=TOOL+"Method: val mode.")

R("sha256-38|CV.BLK3|CV|Q2", status="LOCAL_ONLY", labels=["K","Z"],
  object="CV.BLK3 necessity of the third block; can it act as a correction block",
  question="Q2 necessity: drop the third block, or can the equal padding block absorb a small chaining-value difference left by block 2?",
  topic="G04-38 third block necessity",
  evidence=W+"blk38.c; "+W+"out38.txt",
  number="Drop: EXACT impossible for a 128-byte message (0 of 12,544 length pairs fit the padding into the colliding block with the required dW15 = fc400800; see BLKn Q2). Correction block: 3,291,200 tests (100 random CV2; per CV2 all 32,896 XOR differences of weight 1-2 plus the 16 +-1 per-word differences) through F_38 with the fixed padding block: 0 equal outputs, minimum output XOR weight 87 of 256, mean 128.00. So block 3 only carries an existing collision forward (dCV2 must be 0); it cannot reduce a near-collision. 0 bit.",
  notes=TOOL+"Method: padcorr mode (100 CV2 samples). LOCAL_ONLY: low-weight differences on random CV2 only; large structured dCV2 and chosen CV2 not tested (that is CV.diff, outside this unit).")

R("sha256-38|CV.BLK3|CV|Q3", status="SAMPLED", labels=["N"],
  object="CV.BLK3 freedom of an extra free block",
  question="Q3 log2 freedom left if a free extra block X is inserted: bits added and whether its CV is as good as a first block's.",
  topic="G04-38 third block freedom",
  evidence=W+"blk38.c; "+W+"out38.txt; "+W+"ks.out",
  number="Padding block: 0 free bits (constant). Extra free block X after a fixed M0*: 512 free bits, but only 32 bits (A_-1) are read by the F7 gate; hits need about 2^81 first blocks (g_90 x q3 = 2^-80.9 per live CV) of 2^512 X values and 2^32 gate states of A_-1. Quality: 2^18 CVs F_38(F_38(IV,M0*),X): g_all mean 4,489,226 +- 459 (real first block 4,489,468 +- 459), g_90 mean 23,107.3 +- 79.4 (23,188.9 +- 79.5), P(g_90>0) = 0.3031 (0.3036), KS on g_all D=0.00209 p=0.61. No freedom is lost or gained by the extra block.",
  notes=TOOL+"SAMPLED, 2^18 per kind, one fixed M0* (seed 101); a second M0* not tried. The 2^32-state vs 2^81-blocks comparison is plain arithmetic from the ledger q3.")

R("sha256-38|CV.BLK3|CV|Q4", status="SAMPLED", labels=["Z"],
  object="CV.BLK3 alternatives for the third block",
  question="Q4 alternatives: another third-block content or place (extra free block between, difference block as block 3, longer message) and their cost.",
  topic="G04-38 third block alternatives",
  evidence=W+"blk38.c; "+W+"out38.txt; "+W+"ks.out",
  number="(i) Free extra block between M0* and M1: trial cost 1 compression (cached prefix), g distribution identical (KS p=0.61), end state 4 compressions per member: 0 bit. (ii) Difference block as block 3 of a longer message: identical to (i): 0 bit. (iii) Padding content cannot be changed (FIPS length 1024 bits fixed by the 128-byte message; a longer message only changes W14/W15 of the padding block, equal in both members): 0 bit. (iv) Padding block as correction block: 0 of 3,291,200 low-weight tests. No alternative lowers T or memory.",
  notes=TOOL+"Same limits as the Q2/Q3 cells; prefix-sharing of sibling X blocks is in LEVERS.md (w7_fb_prefix); not rerun.")

os.makedirs(out, exist_ok=True)
st = add_cell.load()
for cell, d in recs.items():
    fn = os.path.join(out, cell.replace('|', '_') + '.json')
    json.dump(d, open(fn, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    r = add_cell.validate(json.load(open(fn, encoding='utf-8')), st)
    print(cell, r)
