# Special frames (X13 = D1.d1 = 0): dependency, generation, rates

1. Q1 X13 (ctr_outer L750 X13=X8-D2.c1; X8 L736<-D2.b1; D2.c1 L747<-D2.b1,S7; S7 L745<-S11,K3.b1; K3 L738-743<-w6) reads exactly 3 of the 8 drawn words: D2.b1, S11, w6.
2. Q1 D1.d1 (L779 =D1.c1-S11; D1.c1 L778<-X12; X12 L777<-C0.d1,C0.a1; C0.a1 L762<-Y0,C0.b1,w6 -> Y4,X9,S4,S11) reads 7 of 8: all but D2.a1 (which feeds only X2/S13/D2.d1). Both confirmed by per-input perturbation.
3. Q2 YES, generable directly in triangular order, O(1) arithmetic, no 2^-64 rejection. Free (C0.d1,D2.a1,D2.b1,w6,S4,C0.b1); solve S11=rol(S7,7)^K3.b1 with S7=X8^rol(D2.b1,12) => X13=0; set target C0.a1=rol(C0.d1,16)^(X11-S11) => D1.d1=0; derive X9 from free C0.b1.
4. BUT forcing D1.d1=0 makes Y4 an OUTPUT (Y4=ror(Y8^C0.b1,7), the sol §8.2 chart), not a freely drawn class member, so the step survives only if that computed Y4 lands in the class. Measured class rate = 3.05e-5 ~ 2^-15.0 (= CLASS_MASK popcount 15).
5. So the ordinary marginal law is NOT preserved: Y4 and the filter inputs Y9, E=Y3+Y4+w8 carry §8.2's restricted conditional law, not the free-class law. Effective cost per generated special step ~ 2^15 lightweight tries + one ctr_outer; all 1464 verified X13=D1.d1=0, Y4 consistent.
6. Q3 real 32-bit steps (ORD N=24000 random; SPC N=1464 generated with X13=D1.d1=0) -- success-relevant partial rates match within standard error:
7. filter pass share: ORD 0.0012 (se 2e-4) vs SPC 0.0014 (se 1.0e-3); z = -0.20.
8. E3 condition (1) per listed outcome (fq automaton on Q=Y9): ORD 0.0072 (se 2e-4) vs SPC 0.0073 (se 8e-4); z = -0.18.
9. filter condition (2) per outcome (fe automaton on E): ORD 0.0227 (se 4e-4) vs SPC 0.0243 (se 1.5e-3); z = -1.02.
10. per-trial E1 gate T0!=0 (ctr_trial, 4 random cube members/step): 1.0000 in both -- saturated, uninformative here.
11. VERDICT: the special-frame restricted law does not measurably shift any success-relevant rate (all |z|<1.1); but SPC se is 3-5x larger (n=1464), so absolute shifts below ~1e-3 remain undetectable.
12. Matches §8.2 caveats: nonemptiness confirmed (1464 real frames), class mean ~2^-15 here; no claim made about productive mass or full E1/chunk-collision success.
