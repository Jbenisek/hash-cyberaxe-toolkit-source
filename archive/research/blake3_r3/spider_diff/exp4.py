from exp1 import *
def hwstats(diffs,S,mode='xor'):
    D=len(diffs);N=D*S
    base=[rng.integers(0,2**32,N,dtype=np.uint64).astype(M) for _ in range(16)]
    alt=[b.copy() for b in base]
    for k,d in enumerate(diffs):
        sl=slice(k*S,(k+1)*S)
        for w,dl in d.items(): alt[w][sl]=base[w][sl]^M(dl) if mode=='xor' else base[w][sl]+M(dl)
    s1=[];s2=[];compress(base,3,64,11,N,s1);compress(alt,3,64,11,N,s2)
    out=[]
    for r in range(3):
        h=sum(pop(s1[r][i]^s2[r][i]) for i in range(16)).reshape(D,S)
        out.append((h.mean(1),h.min(1)))
    return out
diffs=[{w:1<<b} for w in range(16) for b in (0,7,15,31)]
o=hwstats(diffs,2048)
print("single bit: mean HW of 512-bit state diff after r0,r1,r2 (random=256); min over samples")
for r in range(3):
    k=o[r][0].argmin(); print(" round",r,"lowest-mean cfg",diffs[k],o[r][0][k],"min sample HW overall",o[r][1].min())
