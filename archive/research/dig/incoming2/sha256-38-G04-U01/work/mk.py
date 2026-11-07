
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

import json,os,sys
sys.path.insert(0,_hca_public_path_text('__HCA_WORKSPACE__/research/dig'))
import add_cell
out=_hca_public_path_text('__HCA_WORKSPACE__/research/dig/incoming2/sha256-38-G04-U01')
base=dict(hash="sha256-38",source="our workflow: scan-once-wave2",own_test=True,date="2026-10-12",lever=False,gain_bits=0.0,
 evidence="research/dig/incoming2/sha256-38-G04-U01/work/ (nec38.c nec38.out, alt38.c alt38.out, a2.c a2.out, common.h)")
val=" Validated first on the published pair: digest of both members = printed, 0 cell failures over A,E rows -4..37 and W rows 0..37, W7x in F7, Lemma 4.1 reproduces W0..W7 of both members, fam38 reproductions |G|=2^26, 102,696 c7 values, 180 classes of 3840."
recs={
"sha256-38|CV.A-1|CV|Q2":dict(row_i=-1,row_j=7,object="CV word A_-1 = x (class gate): x in F7 (W7x = c7(a0) - A_-1)",
 question="Q2 necessity: is the gate x in F7 needed; what exact event does dropping or weakening it give?",
 labels=["E","0"],status="COMPUTED",
 number="NECESSARY AND SUFFICIENT for the W22 cell: #{W7x : W22x = W22y} = 287,309,824 = |F7| exactly (all 2^32 W7x with the published W20, W15, W6; 0 mismatches against the definition s0(w+20000000)-s0(w)=03bff800). Sampled 2e7 (W6, W7 uniform, W16..W21 forced to the pair's values through W0..W5, W8..W15 the pair, W16..W37 recomputed from W0..W15 for both members): x not in F7 -> W22 cell holds 0 of 18,663,707 (cells W16..W22 all: 0); x in F7 -> W22 cell and cells W16..W22 hold 1,336,293 of 1,336,293. Dropping the gate = event probability 0, not a cost saving. The cell-literal gate (W7 XOR cell n at bit 29, i.e. w29=0) is only 268,435,456 = 2^28 of the 287,309,824; the modular F7 is already the weaker gate used (1,248,318 of 1,336,293 sampled F7 words also meet the W7 XOR cell)",
 notes="universe cell sha256-38|CV.A-1|CV|Q2. Mechanism: W22 = s1(W20)+W15+s0(W7)+W6; the pair has dW6 = 0, dW20 = 0, dW15 = fc400800 and the W22 cell all '=', so dW22 = 0 forces s0(W7+20000000)-s0(W7) = t7 = -dW15 = 03bff800. Gate x = A_-1 enters only through W7x = c7(a0) - A_-1 (a bijection per a0). Scope: published S and published l (W8..W15 of the pair); schedule recomputed from W0..W15, no held-fixed expanded word; the W23 cell (value dependent) is not part of the gate (holds for 20,817 of 1,336,293 F7 samples, a tail event of q3)."+val),
"sha256-38|CV.A-1|CV|Q4":dict(row_i=-1,row_j=7,object="CV word A_-1 = x: alternative gates (other d7 or t7, larger a0 family)",
 question="Q4 alternatives: is there another gate set for x (other d7/t7), or a larger a0 family sharing the gate?",
 labels=["Z","K"],status="COMPUTED",
 number="(i) d7 = W7y-W7x = 20000000 for every a0 and every A_-1 (2e6 random pairs, 0 exceptions; E4, E5, E6 are equal in both members), so no E4-dependent alternative gate as in r37; (ii) over all 2^32 values of s0(w+20000000)-s0(w) there are 512 distinct values and eight of them tie at the maximum count 287,309,824 = 2^28.098, the printed t7 = 03bff800 among them: no t with a bigger F7 for this d7; (iii) exhaustive over all 2^32 a0: |G| = 67,108,864 = 2^26 (cell + 3 two-bit conds), G' (modular s0(W8y)-s0(W8x) = fe7f8000 only) = 68,157,440 = 1.0156 x |G| (+1,048,576 = 2^20 extra a0); distinct c7: G 102,696 (180 classes of 3840, 691,200 variants), G' 103,800 (180 classes of size >= 3840, max 3880, 694,800 variants, +0.52%)",
 notes="universe cell sha256-38|CV.A-1|CV|Q4. Same small lever as r37 G' (dense_boring finding 3), now measured for r38: +1.56% a0, +0.52% variants in the top-size classes, class shapes change (max class 3880 > 3840), so a rebuilt class schedule would be needed. Not tested: the value-dependent cells of rows 23.. for the extra a0 (W23 holds bits of s0(W8x)), q3 for G', the other l of L (their t7 = -dW15 differs; the 8 l were not re-enumerated here), borrow-variant pairs end to end. Not a gain claim."+val),
"sha256-38|CV.A-2|CV|Q1":dict(row_i=-2,row_j=16,object="CV word A_-2 as the attack uses it: what, if anything, tests it (F6 analogue)",
 question="Q1 count: how many A_-2 values pass the attack's A_-2-dependent test; what is the count of the object as used?",
 labels=["D","N"],status="COMPUTED",
 number="No W6 gate in the 38-step program: dW6 = 0 and dW14 = 0, so all 2^32 of 2^32 W6 values (W6x = const - A_-2, a bijection) give W21x = W21y and W22x = W22y (exhaustive, published other words). The only test that moves with A_-2 is the row-16 filter on E16x = C16 + W0 + s0(W1): A_-2 enters W0 (through MAJ(A_-1,A_-2,A_-3) in E0) and W1 (through E0 and E1). Per context (A_-1 in F7), exhaustive over all 2^32 A_-2: stage 3a (12 bits) accepts 1,044,352 / 1,049,088 / 1,028,096 / 962,560 / 1,056,256 / 1,040,128 / 1,041,856 (7 contexts, mean 2^19.97 vs 2^20); the 32-word row-16 set accepts 128, 0, 0, 0, 0, 0, 64 (mean 27.4, expected 32 = 2^-27 x 2^32)",
 notes="universe cell sha256-38|CV.A-2|CV|Q1. F6 analogue: none (the r37 gate p6 = 2^-3.9 does not exist here). Context 0 is the published CV (A_-2 varied; 128 hits including the published A_-2). 4 hits of each nonempty context rebuilt from the lemma and traced: 0 cell failures rows -4..16. Counts per context are exact; the spread across contexts is only 7 draws."+val),
"sha256-38|CV.A-2|CV|Q2":dict(row_i=-2,row_j=6,object="CV word A_-2 (second gate cb = C6 - A_-2): the F6 analogue",
 question="Q2 necessity: is a second CV gate on A_-2 needed; what happens if it is dropped or replaced?",
 labels=["0","K"],status="COMPUTED",
 number="No second gate exists to drop: W6 is equal in both members (d6 = 0), W21 = s1(W19)+W14+s0(W6)+W5 has dW14 = 0 and W22 carries W6 equally, so W21x = W21y and W22x = W22y hold for all 2^32 W6 (exhaustive, 4,294,967,296 of 4,294,967,296 each). The r37 factor p6 = 2^-3.90 is 1 here (the r38 gate cost is only p7 = 2^-3.90197). The A_-2-dependent test that remains is stage 3a / row 16 on E16x (needed: row-16 probability 2^-27 = 32 words, counts under Q1)",
 notes="universe cell sha256-38|CV.A-2|CV|Q2. Scope: published S and l. The value of W6 still enters later schedule values, but Lemma 5.1 makes (W16..W21) iid uniform and independent of W6 through W0..W5; sampled evidence: 2e7 samples with W6 uniform (nec38.out) gave W16..W22 cells holding exactly when W7x is in F7, no dependence on W6."+val),
"sha256-38|CV.A-2|CV|Q3":dict(row_i=-2,row_j=16,object="CV word A_-2: log2 freedom left",
 question="Q3 freedom: how much of the 32 bits of A_-2 is free after the A_-2-dependent test?",
 labels=["N"],status="SAMPLED",
 number="Raw: 32 bits (no gate). Effective for E16x: A_-2 matters only at the bits of M1 | M2 with M1 = A_-1 ^ A_-3 (MAJ in E0) and M2 = A0 ^ A_-1 (MAJ in E1): popcount 25, 24, 22, 21, 23, 26, 26 in 7 contexts (mean 23.9 +- 0.7 se, expected 24); the other bits are free and multiply every count by 2^(32-popcount). After the row-16 set the accepted count per context is 128, 0, 0, 0, 0, 0, 64 (log2 7, none x5, 6); mean 27.4 +- 18.4 se against 32 expected; 2 of 7 contexts have any accepted A_-2 (counts are multiples of 2^(32-popcount))",
 notes="universe cell sha256-38|CV.A-2|CV|Q3. SAMPLED over 7 contexts (each exact over 2^32 A_-2); the interval is the standard error of 7 draws. Consequence: the row-16 test cannot be steered by A_-2 alone, but the first block is random anyway, so this is not a lever."+val),
"sha256-38|CV.A-2|CV|Q4":dict(row_i=-2,row_j=16,object="CV word A_-2: alternative carriers of the A_-2-dependent test",
 question="Q4 alternatives: which other CV words carry W0..W7 and E16x, can another word replace A_-2?",
 labels=["Z","I"],status="LOCAL_ONLY",
 number="Perturbation test (400 random CVs, one random change per CV word each, Lemma 4.1 with the published A0..A13 and a0): A_-1 moves W0..W7 and E16x; A_-2 moves W0..W6 and E16x; A_-3 W0..W5; A_-4 W1..W4; E_-1 W0..W3; E_-2 W0..W2; E_-3 W0,W1; E_-4 W0 only; all eight words move E16x. So A_-2 is the only carrier of W6 (W6 = const - A_-2) and with A_-1 the only carrier of W7; E_-4 is a clean translate carrier of E16x (W0 only). Lemma-4.1 rebuilt blocks reproduce A0..A13 and E4..E13 on 1000 random CVs (0 mismatches)",
 notes="universe cell sha256-38|CV.A-2|CV|Q4. LOCAL_ONLY: dependence is sampled for the published a0 and S. No alternative d6/t6 gate exists to carry (dW6 = 0 is fixed by the characteristic); alternatives with a W6 difference need another characteristic and were not scanned."+val),
}
for cid,v in recs.items():
    r=dict(base); r.update(v)
    fn=os.path.join(out,cid.replace("|","_")+".json")
    json.dump(r,open(fn,"w",encoding="utf-8"),indent=1)
    add_cell.validate(json.load(open(fn,encoding="utf-8")),add_cell.load())
    print("ok",fn)
