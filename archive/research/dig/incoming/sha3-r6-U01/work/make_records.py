
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

import json, os
D = _hca_public_path_text('__HCA_WORKSPACE__/research/dig/incoming/sha3-r6-U01')
W = 'research/dig/incoming/sha3-r6-U01/work/'
def ev(*f): return '; '.join(W + x for x in f)
common = dict(hash='sha3-r6', row_i=None, row_j=None, source='our workflow: scan-once', own_test=True, date='2026-10-12', lever=False, gain_bits=None)
recs = {}
recs['sha3-r6_round0.chi_chi_Q1'] = dict(common, object='round-1 chi on the leader route (4867f093 prefix conditions, 32 z-directions)',
 question='Q1 count the prefix conditions that keep chi1 linear/sparse (each z-flip moves exactly 2 round-1 bits, 22-word footprint).',
 labels=['N'], status='COMPUTED',
 number="128 affine conditions, rank 128, on the message: 4 per z-bit (for each of the 2 chi1-input bits a z-flip moves, its row neighbour x+1 must be 0 and x-1 must be 1). Same 128 in the 64-byte (512 free bits) and 135-byte (1080 free bits) formats; none depends on z (0 of 128x32 form/direction pairs). The leader's own 256-equation prefix (L3=0x06^M64^rotl(L0^L5,1), L4=0, L6=0, L7=L2^rotr(L0^L5,1)) satisfies all 128 (100%, plain lanes), so it over-conditions by 128 on unused planes. Validation (known answer reproduced): on 300 satisfying prefixes x 32 directions every chi1 output difference has weight 2 and equals the input difference (9,600/9,600), theta2 footprint 22 words, 21 chi2 rows, 1 two-input row; unconstrained prefixes: identity in only 5.7% of cases, mean weight 3.99.",
 evidence=ev('sha3lab.py','val_keccak.py','q12.py','q12_out.json','leader_check.py'),
 notes="Universe cell sha3-r6|round0.chi|chi|Q1. Own Keccak (matches hashlib sha3_256 at 24 rounds on 6 lengths). Counted in the plain (uncomplemented) lane convention; the note's M64 is the lane-complement convention and the plain-domain match needs it on L3. The theta3 footprint of the chi2 difference averaged 347 bits (min 265, max 426) per direction, which does NOT reproduce the note's 554 patched O2P words: that is an implementation word count (positions the compiled patch touches), not the value-dependent bit footprint; not chased. Exact for round 1 only (prefix of the path).",
 topic='sha3-r6 leader route chi1 conditions')
recs['sha3-r6_round0.chi_chi_Q2'] = dict(common, object='round-1 chi on the leader route: necessity of each of the 128 conditions',
 question='Q2 drop each prefix condition: does affinity/rank fail?',
 labels=['N'], status='SAMPLED',
 number="Affinity and rank never fail: dropping any single one of the 128 conditions (all independent, none redundant), dropping a whole family of 32, or dropping all 128 gives 0 second-difference failures (76,800 checks per format for single drops, 600 per family, 1,000 with none) and the 32 z-images keep rank 32. Reason (structural): each chi1 row holds at most one z-varying bit, so chi1 is affine in z with no condition at all. What each condition buys is constancy/sparsity: dropping one makes that direction's chi1 difference prefix-dependent (2 distinct differences, weight 3 in 32-68% of 60 samples, mean 0.49 F64 / 0.50 F135) and raises the theta2 footprint from 22 to 31 or 33 words and chi2 rows from 21 to 30-32 in the violated cases. Dropping a family of 32: mean weight 2.49; none: 3.99.",
 evidence=ev('q12.py','q12_out.json'),
 notes="Universe cell sha3-r6|round0.chi|chi|Q2. Sampled (60 prefixes per dropped condition, base prefix uniform over the other 127 equations), no interval given for the weight-3 fraction; the affinity result is exact by structure. Consequence: the conditions are a cost-shape device (AND-free constant-W patch), not a correctness requirement; the leader spends 256 equations of 512 prefix bits on them, free at 2^224 groups against 2^96 needed. Group freedom is not the limit.",
 topic='sha3-r6 leader route chi1 conditions')
recs['sha3-r6_round0.chi_chi_Q3'] = dict(common, object='round-1 freedom on the leader route and the linstruct 24/35-dim spaces',
 question='Q3 log2 freedom (1,080 free message bits; 24/35-dim spaces of linstruct).',
 labels=['N'], status='COMPUTED',
 number="Leader route (32 z-dims, 128 conditions): 2^352 groups in the 64-byte format (512 bits), 2^920 groups in the 135-byte format (1,080 bits); 2^96 groups x 2^32 are needed for N=2^128, so headroom 256 / 824 bits. Leader's 256-equation prefix: at most 2^224 groups (2^256 prefixes less the L0/L5 z overlap), still 128 bits of headroom. linstruct re-measured with our Keccak: the listed 31-direction set has GF(2) rank 24, 82 conditions rank 82, outer freedom 1080-24-82 = 2^974, second-difference test on the real 2-round function 0/300 fails (controls: conditions ignored 200/200 fail; conditions met but 3 rounds 200/200 fail); SOLCLOUD_16 35-dim space: rank 35, 2^320 source, outer 2^285, 0/300 fails. The other listed 24-direction run has rank 19, 67 conditions, outer 2^994.",
 evidence=ev('q3.py','q3_out.json','controls.txt','q12_out.json'),
 notes="Universe cell sha3-r6|round0.chi|chi|Q3. Reproduces the known numbers (rank 24 / 82 / 974 and 35 / 285) from the stored direction and condition files; the directions themselves were not regenerated. The 35-dim check lifts the Appendix-B vectors into lanes 0-4 and 10-14; the sponge match is verify_sol16.py's, not redone. Freedom is not the constraint on this route.",
 topic='sha3-r6 leader route freedom')
recs['sha3-r6_round0.chi_chi_Q4'] = dict(common, object='round-1 chi: non-identity transitions and theta2 kernel membership, per message direction',
 question='Q4 do non-identity chi transitions give another route (theta kernel membership too)?',
 labels=['Z'], status='LOCAL_ONLY',
 number="No, at the single-direction level. All 1,320 CP-kernel pair directions of the 135-byte rate (the leader's 32 z-directions included) touch two chi1 rows; for each, all 1,024 row-value assignments are feasible (any transition type costs the same 2 conditions per varying bit) and 0 of 1,320 directions has any chi1 output difference in the theta2 kernel (identity or not). The best footprint after theta2 is 22 words (identity) for 1,264 directions and 21 words (one non-identity weight-3 transition) for 56 directions (e.g. message bits 384/1024); other non-identity transitions cost at least 31. The two varying bits sit in different z-slices, so no choice of the neighbour bits can cancel a column parity.",
 evidence=ev('q4.py','q4_out.json'),
 notes="Universe cell sha3-r6|round0.chi|chi|Q4. LOCAL_ONLY: one direction at a time, round 1 only; joint families (sums of directions sharing a row or column) and chi2/chi3 transitions are not covered (SHA3R6_MAP section 4 lead stays open at those depths). The 22 for the leader directions reproduces the known footprint. The 21-word cases are weight-3 transitions on lane6/lane16 pairs; an upper bound for their worth is one word of the 22 in the 7.30 ops/message chi2 patch block, about 0.3 op/message (about 0.004 bit), not validated against a full path.",
 topic='sha3-r6 non-identity chi transitions')
recs['sha3-r6_round0.theta_theta_Q4'] = dict(common, object='round-1 theta: column-parity kernel of the message space',
 question='Q4 column-parity kernel alternatives at the first theta (what directions leave theta as the identity).',
 labels=['N'], status='COMPUTED',
 number="Kernel of the column-parity map on the free message bits: 135-byte format 760 dims (1080 bits, column-parity rank 320, no column has a single free bit); 64-byte format 192 dims (rank 320 of 512; 128 columns have a single free bit). The kernel is exactly spanned by the within-column pairs (span dim = kernel dim); weight-2 kernel vectors: 1,320 (135-byte) and 192 (64-byte) and all are CP pairs, so the leader's 32 z-directions (L0^L5 pair at each z) are 32 of these. theta acts as the identity on 200/200 sampled pairs (192/192 in the 64-byte format).",
 evidence=ev('q4_theta.py','q4_theta_out.json'),
 notes="Universe cell sha3-r6|round0.theta|theta|Q4. Exact rank counts. Alternatives to the leader's pair class exist only inside this kernel; the chi1 side of the question is cell sha3-r6|round0.chi|chi|Q4 (no kernel output difference). theta2/theta3 kernels belong to later rounds' cells.",
 topic='sha3-r6 theta kernel')
for k, v in recs.items():
    json.dump(v, open(os.path.join(D, k + '.json'), 'w'), indent=1)
print(list(recs))
