import json
EV="research/dig/incoming/blake3-r2-U09/work/scan_m67.py; research/dig/incoming/blake3-r2-U09/work/scan_m67.out.json; research/dig/incoming/blake3-r2-U09/work/validate_b3.py"
VAL="Construction validated first: 3000/3000 random 8-word inputs reproduce X3/X7/X11/X15, Y4=y, S and X equal A vs B, digest words 0,2,5,7 equal (work/validate_b3.py, reused from U06 on our b3lib.py written from pkgB3U proof). "
rec={}
for w,rd,use in ((6,"round 0 K3 (second operand of the first message add of G3,7,11,15 is w6, w7 the second add); w6 reappears in round 1 C0 (permuted slot s1), w7 in round 1 C2 (slot s4)",None),(7,"",None)):
    pass
use={6:"w6 is the first message word of K3 (round 0) and the second of C0 (round 1, permuted slot 1)",7:"w7 is the second message word of K3 (round 0) and the first of C2 (round 1, permuted slot 4)"}
d={}
d[1]=("difference/condition count as used on m{w}",
 "COMPUTED","w6 and w7: A-vs-B difference 0 in 20000/20000 builds (B copies A except w4,w5 by construction); 0 conditions placed on the value of either word (both are outputs of the K3 inversion: w6=K3a1-IV3-IV7, w7=S3-K3a1-K3b1); no fixed bits (max bit bias 0.0083 / 0.0089 over 20000, all 32 bits free in both)",
 "Reads the pair block layout: m6,m7 are equal in A and B and carry no printed condition of their own; their values are derived from K3 pins (X3 etc.). Bias figures are sampled on 20000; zero-difference is structural.")
d[2]=("necessity of the conditions tying m{w} to its derived value",
 "SAMPLED","Changing w6 (or w7) in A and B alike (3000 trials each, random xor): X3/X7/X11/X15 kept 0/3000, digest words 0,2,5,7 equal 0/3000 (control without change 3000/3000); changing it in B only: Lemma H kept 0/3000, S equal 0/3000, mean 8.0/8 digest words differ. Both words are necessary: the derived value is the only one that works",
 "Drop-singly test: the condition 'm{w} = derived value' cannot be dropped. Sampling interval: 0/3000 gives rate < 0.1% (95%). Note S-equal stays 3000/3000 under same change in A and B because the pair differs only in w4,w5; it is the pinned X constants and Lemma H that break.")
d[3]=("local freedom of m{w} given earlier rows (log2 values consistent)",
 "COMPUTED","(w6,w7) jointly free: 64 bits. K3 inverse (S3,S15)<->(w6,w7) round-trips 200000/200000 both ways; solving S15 and S9 for 20000 random targets (w6t,w7t) gives A[6]=w6t, A[7]=w7t with X constants and Lemma H kept 20000/20000; w6 and w7 each take 65536 distinct values over 65536 random S15 draws; dependence on the 8 free params: D3d1, S15, S9, w5 change both words in 2000/2000, C0c1, C0d1, X2, y change neither (0/2000)",
 "So m{w} costs nothing (bijective in S15, jointly with the other word via S9); the pair is a reparametrisation of (S3,S15). Constructive solution exists for every target pair.")
d[4]=("alternative signings of m{w} difference (same modular difference)",
 "SAMPLED","No alternative: the A-B difference on w6,w7 is 0; putting a modular difference dl on w6, on w7, a sum-preserving (+dl,-dl) pair or independent pair in B: K3 state equal 0/3000, S equal 0/3000, Lemma H 0/3000. K3 state is injective in (w6,w7): 0 collisions in 300000 samples (each a-step is a bijection in its message word, so equal outputs force equal words)",
 "Counter/flag absorption (as in K0 where t enters d) is not available here: K3 d-init is the fixed flags word 11, so no compensating field exists for w6/w7. Flags were not varied (fixed by the root call).")
for q in (1,2,3,4):
    for w in (6,7):
        qq,st,num,note=d[q]
        r=dict(hash="blake3-r2",row_i=None,row_j=None,object=f"m{w} message word",question=qq.format(w=w),
          labels=["I"] if q!=4 else ["Z"],status=st,number=num.replace("(w6,w7)",f"(w6,w7)") ,source="our workflow: scan-once",own_test=True,
          evidence=EV,date="2026-10-12",lever=False,gain_bits=None,
          notes=f"Universe cell blake3-r2|m{w}|msgword|Q{q}. {use[w]}. {VAL}{note.format(w=w)} Method same as blake3-r2-U06 (scan_m01.py) applied to words 6,7. Tested the pkgB3U root construction only, 2-round, A (len 55) vs B (len 63).",
          topic=f"b3 msgword m{w} Q{q}")
        json.dump(r,open(f"blake3-r2|m{w}|msgword|Q{q}.json".replace("|","_"),"w"),indent=1)
