# root-type pair classes: cancel every cancellable constant difference in round 0, measure round-1 activity and digest-word agreement
import random,json,sys
from b3lib import M,IV,P,ror,rol,G
CALLS=((0,4,8,12),(1,5,9,13),(2,6,10,14),(3,7,11,15),(0,5,10,15),(1,6,11,12),(2,7,8,13),(3,4,9,14))
def run(h,w,t,b,f,rounds=2):
    v=list(h)+IV[:4]+[t&M,t>>32,b,f]; s=list(w); tr=[]
    for r in range(rounds):
        for k,(a,bb,c,d) in enumerate(CALLS):
            tr.append((r,k,v[a],v[bb],v[c],v[d],s[2*k],s[2*k+1])); G(v,a,bb,c,d,s[2*k],s[2*k+1])
        s=[s[P[i]] for i in range(16)]
    return v,tr
def dig(v): return [v[i]^v[i+8] for i in range(8)]
def cancel(a,b,d,a2,d2,x,y):
    # b equal required. find x2,y2 so K-call outputs equal
    a1=(a+b+x)&M; a1p=a1^d^d2
    x2=(a1p-a2-b)&M; y2=(y+a1-a1p)&M
    return x2,y2
def pair(hA,hB,bA,fA,bB,fB,rng):
    w=[rng.getrandbits(32) for _ in range(16)]; w2=w[:]
    vA=list(hA)+IV[:4]+[0,0,bA,fA]; vB=list(hB)+IV[:4]+[0,0,bB,fB]
    cancelled=[]
    for i in range(4):
        a,b,c,d=vA[i],vA[4+i],vA[8+i],vA[12+i]; a2,b2,c2,d2=vB[i],vB[4+i],vB[8+i],vB[12+i]
        if (a,d)==(a2,d2) and b==b2: continue
        if b!=b2: continue   # b input differs: not cancellable in call
        x2,y2=cancel(a,b,d,a2,d2,w[2*i],w[2*i+1]); w2[2*i],w2[2*i+1]=x2,y2; cancelled.append(i)
    return w,w2,cancelled
def trial(hA,hB,bA,fA,bB,fB,rng):
    w,w2,canc=pair(hA,hB,bA,fA,bB,fB,rng)
    vA,trA=run(hA,w,0,bA,fA); vB,trB=run(hB,w2,0,bB,fB)
    # state after round 0 = trace entries of round 1 inputs at call 0..: use entries r=1 compare
    r0=[ (a!=b) for a,b in zip(trA,trB) if a[0]==0]
    r1=[ (a[2:]!=b[2:]) for a,b in zip(trA,trB) if a[0]==1]
    act0=[k for k,x in enumerate(r0) if x]; act1=[k for k,x in enumerate(r1) if x]
    dA,dB=dig(vA),dig(vB)
    return canc,act0,act1,[dA[i]==dB[i] for i in range(8)],sum(1 for i in range(16) if w[i]!=w2[i])
def rndh(rng): return [rng.getrandbits(32) for _ in range(8)]
def main(N=5000):
    rng=random.Random(2026101201)
    cases=[]
    cases.append(('AA control: root11 len55 vs root11 len63 (h=IV)',IV,IV,55,11,63,11))
    cases.append(('AA other length pair: len 56 vs 64',IV,IV,56,11,64,11))
    cases.append(('AC: root11 len55 (h=IV) vs parent root12 b=64 (h=IV), message words treated as free',IV,IV,55,11,64,12))
    cases.append(('AC: root11 len 40 vs parent root12 b=64',IV,IV,40,11,64,12))
    cases.append(('AA-flag only: root11 b=64 vs parent-type flags 12 b=64 (same b), message free',IV,IV,64,11,64,12))
    cases.append(('A-B*: root11 len55 vs root10 len63, h=IV for both (CV with h=IV modelled free)',IV,IV,55,11,63,10))
    cases.append(('A-B*: root11 len55 vs root10 len55, h=IV for both',IV,IV,55,11,55,10))
    out=[]
    for name,hA,hB,bA,fA,bB,fB in cases:
        agg=dict(n=0,canc={},act0={},act1={},eq=[0]*8,eqk={},msgdiff={})
        for _ in range(N):
            canc,a0,a1,eq,md=trial(hA,hB,bA,fA,bB,fB,rng)
            agg['n']+=1
            for key,val in (('canc',tuple(canc)),('act0',tuple(a0)),('act1',tuple(a1)),('msgdiff',md)): agg[key][val]=agg[key].get(val,0)+1
            for i in range(8): agg['eq'][i]+=eq[i]
            k=sum(eq); agg['eqk'][k]=agg['eqk'].get(k,0)+1
        agg['name']=name
        agg['canc']={str(k):v for k,v in agg['canc'].items()}; agg['act0']={str(k):v for k,v in agg['act0'].items()}; agg['act1']={str(k):v for k,v in agg['act1'].items()}
        agg['msgdiff']={str(k):v for k,v in agg['msgdiff'].items()}; agg['eqk']={str(k):v for k,v in agg['eqk'].items()}
        out.append(agg); print(json.dumps(agg))
    # BB / B-C with shared random CV h (multi-block chunk root vs ...), only h0..3 differing
    hs=rndh(rng); hB=hs[:]; 
    json.dump(out,open('tree_pairs.out.json','w'),indent=1)
if __name__=="__main__": main(int(sys.argv[1]) if len(sys.argv)>1 else 5000)
