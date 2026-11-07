# density of pins: random (X3,X7,X11,X15,w4,w13), shift s=+8: P(C3 outputs b and d both equal); also d only / b only
import numpy as np
rng=np.random.default_rng(5)
def ror(x,n): return (x>>np.uint32(n))|(x<<np.uint32(32-n))
def c3(a,b,c,d,x,y):
    a1=a+b+x; d1=ror(d^a1,16); c1=c+d1; b1=ror(b^c1,12)
    a2=a1+b1+y; d2=ror(d1^a2,8); c2=c1+d2; b2=ror(b1^c2,7)
    return a2,b2,c2,d2
for s in (8,-8):
    tot=0; both=0; donly=0; bonly=0
    for _ in range(24):
        n=1<<24
        a,b,c,d,x,y=[rng.integers(0,1<<32,n,dtype=np.uint64).astype(np.uint32) for _ in range(6)]
        r1=c3(a,b,c,d,x,y); r2=c3(a,b,c,d,x+np.uint32(s&0xFFFFFFFF),y)
        eb=r1[1]==r2[1]; ed=r1[3]==r2[3]
        tot+=n; both+=int((eb&ed).sum()); donly+=int(ed.sum()); bonly+=int(eb.sum())
    print('shift %+d: samples %d  P(d equal)=%.3e  P(b equal)=%.3e  P(both)=%d hits => %.3e = 2^%.2f'%(s,tot,donly/tot,bonly/tot,both,both/tot,np.log2(max(both,1)/tot)))
