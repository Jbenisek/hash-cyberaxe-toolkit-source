import numpy as np, time
from b3h import IV, U, ror
from opcount import trace
M=0xFFFFFFFF
def rol(x,n): return ((x<<n)|(x>>(32-n)))&M
t0=time.time(); out={}
for col in (0,1):
    a=int(IV[col]); b=int(IV[col+4]); c=int(IV[col]); a1=(a+b)&M
    sols=[]
    for hi in range(64):
        d1=(np.arange(1<<26,dtype=np.uint64)+np.uint64(hi<<26)).astype(np.uint32)
        c1=d1+U(c); b1=ror(U(b)^c1,12); a2=U(a1)+b1
        ok=np.nonzero(d1==a2)[0]
        for i in ok: sols.append(int(d1[i]))
    res=[]
    for d1 in sols:
        d=rol(d1,16)^a1       # counter word making D'=0 (x=y=0): d1=ror16(d^a1)
        res.append(d)
    print("column",col,"counter word values with post-column d2=0:",[hex(r) for r in res],"time",round(time.time()-t0))
    out[col]=res
    for d in res:
        ctr = d if col==0 else d<<32
        print("  ops with counter",hex(ctr),":",trace(ctr=ctr)[0])
