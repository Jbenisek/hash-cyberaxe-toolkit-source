# Fact P scan: for the pinned X3,X7,X11,X15,W13, which w4 give equal C3 b- and d-outputs for the pair (w4, w4+delta)?
import numpy as np,sys
from initlib import X3,X7,X11,X15,W13
u=np.uint32
def ror(x,r): return (x>>u(r))|(x<<u(32-r))
def c3(w4):
    a1=u(X3)+u(X7)+w4; d1=ror(u(X15)^a1,16); c1=u(X11)+d1; b1=ror(u(X7)^c1,12)
    a2=a1+b1+u(W13); d2=ror(d1^a2,8); c2=c1+d2; b2=ror(b1^c2,7)
    return b2,d2
res={}
for delta in (8,-8,16,-16,1,-1):
    cnt=0; hits=[]
    for hi in range(256):
        w4=(np.arange(1<<24,dtype=np.uint64)+(hi<<24)).astype(np.uint32)
        b,d=c3(w4); b_,d_=c3((w4+u(delta&0xffffffff)))
        m=(b==b_)&(d==d_); cnt+=int(m.sum())
        if m.any() and len(hits)<5: hits+= [int(x) for x in w4[m][:5]]
    res[delta]=(cnt,[hex(h) for h in hits[:5]]); print(delta,res[delta],flush=True)
