import json,os
base=dict(hash="sha256-37",row_i=None,row_j=None,source="our workflow: scan-once-wave2",own_test=True,date="2026-10-12",lever=False,gain_bits=0.0)
ev="research/dig/incoming2/sha256-37-G04-U01/work/ (nec.c nec.out, alt.c alt.out, val.c val.out)"
recs={
"sha256-37_CV.A-1_CV_Q2":dict(row_i=-1,row_j=7,object="CV word A_-1 = x (class gate): x in F7 (W7x = c7(a0) - x)",
 question="Q2 necessity: is the gate x in F7 needed; what exact event does dropping or weakening it give?",
 labels=["E","0"],status="COMPUTED",
 number="NECESSARY AND SUFFICIENT for the W22 cell's modular difference: #{W7x: W22y-W22x = 017f8000} = 68,157,440 = |F7| exactly (all 2^32 W7x, 0 mismatches vs the definition s0(w+fbc00800)-s0(w)=017f8000); sampled 2e7 uniform W0..W7 with published W8..W15: x not in F7 -> W22 cell holds 0 of 19,682,809, W22 cell holding while dW22 != 017f8000: 0; in F7 -> dW22 ok 317,191 of 317,191. Dropping the gate = event probability 0 (not a cost saving)",
 notes="universe cell sha256-37|CV.A-1|CV|Q2. Mechanism: W16..W21 and W23 cells are all '=' so those words are equal in both members; W22 = s1(W20)+W15+s0(W7)+W6 with W20 equal gives dW22 = dW15 + d6 + [s0(W7+d7)-s0(W7)], so the W22 cell (u/n bits fix the modular difference) forces s0 diff of W7 = t7 = 017f8000 exactly. t7 is the same for all 32 l (dW15 = -2^29 forced by the W15 cell). Scope: published S and l (schedule words W8..W15 of the pair); own SHA-256 trace and schedule from W0..W15 recomputed, no held-fixed expanded word. Gate x = A_-1 is W7x = c7(a0) - A_-1, a bijection per a0."),
"sha256-37_CV.A-1_CV_Q4":dict(row_i=-1,row_j=7,object="CV word A_-1 = x: alternative gates (E4[31:29]=v other than 000 changes d7; larger a0 family)",
 question="Q4 alternatives: is there another gate set for x (other d7), or a larger a0 family sharing the gate?",
 labels=["Z","K"],status="COMPUTED",
 number="Exhaustive over all 2^32 E4 (a0 = E4 - 000b362e): d7_v = fbc00800 - v*2^29 (v = E4[31:29]); the W23 condition ds0(W8y)-ds0(W8x) = -d7_v holds for 18,978,816 E4, ALL with v = 0 (v=1..7: 0). So no alternative F7_v gate exists; of the 18,978,816, 12,103,680 have W8x[29]=1 (= |G|) and 6,875,136 are borrow variants (W8x[29]=0); gate F7 unchanged (68,157,440) for all. 3000/3000 pairs built from random CV words (Lemma 4.1, gate hits found by search) for a0 in the borrow set: A/E cells rows 0..15 hold, W16..W23 diffs as the pair (W22=017f8000, others 0)",
 notes="universe cell sha256-37|CV.A-1|CV|Q4. The 18,978,816 is the already-known G' (dense_boring finding 3), reproduced here as exactly the whole 2^32 E4 space; the new part is that E4[31:29] != 000 is closed for any W8 (|ds0 diff| < 2^27 cannot equal d7_v, whose magnitude is >= 2^29 - 2^27). Borrow variants: W8 XOR cell fails by design, dW24 = 2^29 hit 3/3000 vs 5/3000 for the published a0 (same order; W24 tail not measured further). Not tested: row 16..36 survival of borrow variants (Lemma 7.1 says rows 16..22 do not depend on W8), no table rebuilt; this is the same small lever as G' (0.02-0.03 bit), not new."),
"sha256-37_CV.A-2_CV_Q2":dict(row_i=-2,row_j=6,object="CV word A_-2 (second gate cb = C6 - A_-2): cb in F6 (W6x = cb + f(x))",
 question="Q2 necessity: is the gate cb in F6 needed; what exact event does dropping or weakening it give?",
 labels=["E","0"],status="COMPUTED",
 number="NECESSARY AND SUFFICIENT for W21x = W21y: #{W6x: W21 equal} = 287,309,824 = |F6| exactly (all 2^32 W6x, 0 mismatches vs s0(w+20000000)-s0(w)=03c00800); sampled 2e7: W6x not in F6 -> W21 equal 0 of 18,663,979; W23 equal count = W21 equal count = F6 count 1,336,021 (W23 needs ds1(W21)=0, so one gate serves both). Dropping the gate = probability 0 for the W21 and W23 cells",
 notes="universe cell sha256-37|CV.A-2|CV|Q2. Mechanism: W21 cell all '=' so dW21 = ds1(W19)(=0) + dW14 + ds0(W6+d6)-ds0(W6) + dW5(=0) = 0, i.e. s0 diff of W6 = -dW14 = 03c00800 = t6 with dW14 = fc3ff800 fixed by the W14 cell. W23 = s1(W21)+W16+s0(W8)+W7 then also needs W21x = W21y. Scope: published S and l; schedule recomputed from W0..W15 for both members."),
"sha256-37_CV.A-2_CV_Q4":dict(row_i=-2,row_j=6,object="CV word A_-2: alternative carriers of the second gate",
 question="Q4 alternatives: can another CV word or another shifted set carry the W6 gate?",
 labels=["Z","I"],status="LOCAL_ONLY",
 number="Perturbation test (8 CV words, 50 random CVs each, words rebuilt by Lemma 4.1 with a0 published): W6x moves only with A_-1 and A_-2; W7x only with A_-1; A_-3, A_-4, E_-1..E_-4 move only W0..W5. So (A_-1, A_-2) <-> (W7x, W6x) is a bijection per a0 and the only carriers of the gates; for each x the accepted A_-2 set is a translate (-1 sign) of F6, size 287,309,824. d6 = 20000000 and t6 = 03c00800 are forced by dE6 and dW14 (cells), so F6 cannot be altered inside this dense part",
 notes="universe cell sha256-37|CV.A-2|CV|Q4. LOCAL_ONLY: the dependence check is sampled (400 CVs, a0 published) on top of the Lemma 4.1 algebra, and alternatives with another d6/t6 need another S (dense part), which zoneD_family covered as 'F6/F7 unchanged' and which this scan did not redo. 3000/3000 constructed pairs with both gates hit hold A/E cells rows 0..15 and the W16..W23 schedule differences."),
}
for k,v in recs.items():
    r=dict(base); r.update(v)
    json.dump(r,open(k+".json","w",encoding="utf-8"),indent=1)
    r["evidence"]=ev
    json.dump(r,open(k+".json","w",encoding="utf-8"),indent=1)
