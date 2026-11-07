from exp1 import *
import math,time
def big(diff,total,chunk=1<<19):
    mins=[999,999,999];dmin=999;eqmax=0;eqcount=np.zeros(9,dtype=np.int64);t=0
    while t<total:
        N=chunk
        base=[rng.integers(0,2**32,N,dtype=np.uint64).astype(M) for _ in range(16)]
        alt=[b.copy() for b in base]
        for w,dl in diff.items(): alt[w]=base[w]^M(dl)
        s1=[];s2=[];compress(base,3,64,11,N,s1);compress(alt,3,64,11,N,s2)
        for r in range(3):
            h=sum(pop(s1[r][i]^s2[r][i]) for i in range(16)); mins[r]=min(mins[r],int(h.min()))
        dg=[(s1[2][i]^s1[2][i+8])^(s2[2][i]^s2[2][i+8]) for i in range(8)]
        dh=sum(pop(x) for x in dg); dmin=min(dmin,int(dh.min()))
        eq=sum((x==0).astype(np.int64) for x in dg); eqcount+=np.bincount(eq,minlength=9)
        t+=N
    return mins,dmin,eqcount
for diff in ({13:1<<31},{15:1<<31},{9:1<<31},{13:1<<31,9:1<<31}):
    t0=time.time();print(diff,big(diff,1<<22),"%.0fs"%(time.time()-t0),flush=True)
