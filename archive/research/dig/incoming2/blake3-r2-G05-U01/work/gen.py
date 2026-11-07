import json,re,os
base=os.path.dirname(os.path.abspath(__file__)); out=os.path.dirname(base)
scan=json.load(open(os.path.join(base,'scan_init.out.json')))
S={r['label']:r for r in scan}
w4=open(os.path.join(base,'w4scan.out.txt')).read()
n_p8=int(re.search(r'^8 (\d+)',w4,re.M).group(1)); n_m8=int(re.search(r'^-8 (\d+)',w4,re.M).group(1))
ctl=S['control h=IV']
D="research/dig/incoming2/blake3-r2-G05-U01/work/"
EV="; ".join(D+f for f in ("initlib.py","val.py","scan_init.py","scan_init.out.json","w4scan.c","w4scan.out.txt"))
def ag(r): return "low-6-bit agreement of digest-word XOR difference for words 1,3,4,6 = %d/%d/%d/%d of %d (control h=IV: %d/%d/%d/%d)"%(r['agree']['1'],r['agree']['3'],r['agree']['4'],r['agree']['6'],r['n'],ctl['agree']['1'],ctl['agree']['3'],ctl['agree']['4'],ctl['agree']['6'])
VAL=("Validated first: own compress == organizer verifier/blake3.py on 1000 single-block messages at 2 and 7 rounds, empty-message 7-round vector af1349b9... reproduced, and the h=IV builder reproduces pins X3/X7/X11/X15, Y4=y, X equal and digest words 0,2,5,7 equal on 3000/3000 (also through verifier.blake3 on the 55/63-byte strings). ")
LAB={0:('w0','K0','w0 = K0a1 - h0 - h4'),1:('w2','K1','w2 = K1a1 - h1 - h5'),3:('w6','K3','w6 = K3a1 - h3 - h7')}
recs=[]
def rec(cell,obj,q,labels,status,number,notes,topic):
    recs.append(dict(hash='blake3-r2',row_i=None,row_j=None,object=obj,question=q+" [universe cell %s]"%cell,labels=labels,status=status,number=number,source="our workflow: scan-once-wave2",own_test=True,evidence=EV,date="2026-10-12",lever=False,gain_bits=None,notes="Scan of universe cell %s . "%cell+notes,topic=topic))
al=S['h[0..3] all random (h2 with bit3 ok), h4..7=IV']
c1=S['multi-block chunk: h = arbitrary 8-word CV, flags 10 (CHUNK_END|ROOT), h2+h6 ok']
cv=S['multi-block chunk: h arbitrary 8-word CV, flags 10, no filter']
for k in (0,1,3):
    v,call,form=LAB[k]; r=S['h[%d] random uniform, others IV'%k]
    rec("blake3-r2|INIT.v%d|INIT|Q2"%k,"state word v%d = h[%d] (IV[%d] at the first block of a chunk)"%(k,k,k),"Necessity of h[%d]=IV[%d]: relax or replace it and recount the outcome mass"%(k,k),["K","N"],"LOCAL_ONLY",
      "NOT necessary: replacing h[%d] by a uniform random 32-bit word (others IV), %d trials with random free parameters: pins X3/X7/X11/X15 and round-0 state X equal A vs B kept %d/%d, half-collision (digest words 0,2,5,7 equal, lengths 55 vs 63) %d/%d (control h=IV %d/%d). Proxy for the residual mass: %s. All of h[0..3] random together (h2 with bit 3 condition): half-collision %d/%d"%(k,r['n'],r['pins'],r['n'],r['half'],r['n'],ctl['half'],ctl['n'],ag(r),al['half'],al['n']),
      VAL+"Why: h[%d] enters round 0 only as the a-input of %s (v%d), whose call is solved backwards, so it only shifts the derived message word (%s); the round-0 target state X, the pins and C3 (Fact P) do not see it, and the digest never XORs h (256-bit output is Z[i]^Z[i+8]). Free-parameter count unchanged (same 8 parameters, same bijection). The residual R=0 mass itself (2^-128 scale) cannot be sampled; the measured proxy matches the h=IV control within sampling noise, so the exact outcome mass is LOCAL_ONLY. Round 1 reads that message word again, so the block moves but the pair structure is unchanged. Own code only, pkgB3U root construction at 2 rounds."%(k,call,k,form),
      "b3 INIT.v%d Q2"%k)
    rec("blake3-r2|INIT.v%d|INIT|Q4"%k,"state word v%d = h[%d], alternatives to IV[%d]"%(k,k,k),"Alternatives to IV[%d] as h[%d] (multi-block chunk: h = earlier output) that still reach the digest event"%(k,k),["K","Z"],"LOCAL_ONLY",
      "Every value works: %d/%d uniform random values of h[%d] give a valid pair (builder is a bijection per value, so count 2^32 by construction, sampled only); multi-block alternative (whole h an arbitrary 8-word CV, last block flags 10 = CHUNK_END|ROOT, h2+h6 condition met): half-collision %d/%d; %s"%(r['half'],r['n'],k,c1['half'],c1['n'],ag(c1)),
      VAL+"Alternatives tested in the same builder: h[%d] uniform; whole h arbitrary with flags 10 instead of 11 (only changes the constant xored in K3a1). Not tested: the cost of producing a chosen CV from earlier blocks (door 37 prices it 0.007-0.1 bit, not re-measured here), chunk counter t != 0 for a later chunk (Lemma TR counter construction is separate), and the bit-3 condition on h2+h6 (see the INIT.v2 cell) which this word does not touch. No gain found: the freedom is real but the cost of a pair is unchanged."%k,
      "b3 INIT.v%d Q4"%k)
r=S['h[2] random uniform, others IV']; rc=S['h[2] random with bit3(h2+h6+W4)=0']
rec("blake3-r2|INIT.v2|INIT|Q2","state word v2 = h[2] (IV[2]); K = h[2]+h[6] enters the K2 length cancellation","Necessity of h[2]=IV[2]: relax or replace it and recount the outcome mass",["K","S"],"LOCAL_ONLY",
  "Not necessary but half-restricted: uniform random h[2] (others IV), %d trials: pins and X equal %d/%d, half-collision %d/%d (%.4f; control h=IV %d/%d); the success set is exactly bit 3 of (h[2]+h[6]+W4) = 0 (filtered h[2]: %d/%d). With bit 3 = 1 the length-cancelling partner is W4-8 instead of W4+8, the C3 pin (Fact P) no longer holds and digest words 0,2,5,7 differ. Outcome mass: half of the h[2] values keep the pinned pair and the per-trial mass of h=IV (%s); the other half lose the whole event unless W4 and the pins are re-solved"%(r['n'],r['pins'],r['n'],r['half'],r['n'],r['half']/r['n'],ctl['half'],ctl['n'],rc['half'],rc['n'],ag(rc)),
  VAL+"Mechanism: K = h2+h6 (5bf2cd1d at h=IV) gives w4' = ((K+w4) xor 8) - K, which is w4+8 iff bit 3 of K+w4 is 0 (K+W4 = f33a2355, bit 3 = 0). Pins were solved for the pair (W4, W4+8), so they stay valid exactly when that bit is 0. This is a 1-bit necessity on the value of h[2]+h[6], not a cost: any h[2] with that bit 0 is free. Residual R=0 mass at 2^-128 not sampled, so LOCAL_ONLY.",
  "b3 INIT.v2 Q2")
rec("blake3-r2|INIT.v2|INIT|Q4","state word v2 = h[2], alternatives to IV[2]","Alternatives to IV[2] as h[2] that still reach the digest event",["K","Z"],"LOCAL_ONLY",
  "Admissible h[2] (others IV): exactly the half with bit 3 of (h[2]+h[6]+W4) = 0: %d/%d uniform values pass (%.4f), filtered values %d/%d. Whole h an arbitrary CV with flags 10: unfiltered %d/%d (%.4f), filtered %d/%d. Other half: the pair would be (W4, W4-8). Exhaustive scan over all 2^32 w4 with the pinned X3,X7,X11,X15,W13: pair (w4, w4+8) has equal C3 b and d outputs for %d values of w4, pair (w4, w4-8) for %d values"%(r['half'],r['n'],r['half']/r['n'],rc['half'],rc['n'],cv['half'],cv['n'],cv['half']/cv['n'],c1['half'],c1['n'],n_p8,n_m8),
  VAL+"w4scan.c (C, exhaustive over 2^32) checks Fact P only (equal b and d outputs of C3 for the two w4 values); it does not re-solve the downstream Y3/Y11 differences, so a hit at the minus-8 sign would still need the rest of the pin chain (class constants eta, beta*) recomputed: not done. The single w4 hit for +8 is W4 itself (pins unique); the single hit for -8 is W4+8 (the same unordered pair taken the other way), so the failing half of h[2] cannot be repaired by choosing another W4 at these pin constants (new X3,X7,X11,X15 would be needed; not searched). No gain: alternative values only reshuffle the free context, cost per pair unchanged.",
  "b3 INIT.v2 Q4")
for x in recs:
    cid=re.search(r'universe cell (\S+)',x['notes']).group(1)
    fn=cid.replace('|','_').replace('.','_')+'.json'
    json.dump(x,open(os.path.join(out,fn),'w',encoding='utf-8'),indent=1)
    print(fn)
