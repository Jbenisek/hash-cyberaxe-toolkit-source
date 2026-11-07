# Exact: for the filed pin X3,X7,X11,X15,W13, over ALL 2^32 values of w4: for which w4 do the C3 b,d outputs agree between x=w4 and x=w4+s ?
import numpy as np, time
M=np.uint32(0xFFFFFFFF)
X3,X7,X11,X15=0x29d4fa98,0xbee3af28,0x44036000,0x40c58500; W13=0x0007c006
def ror(x,n): return (x>>np.uint32(n))|(x<<np.uint32(32-n))
def c3(x):
    a=np.uint32(X3); b=np.uint32(X7); c=np.uint32(X11); d=np.uint32(X15)
    a1=a+b+x; d1=ror(d^a1,16); c1=c+d1; b1=ror(b^c1,12)
    a2=a1+b1+np.uint32(W13); d2=ror(d1^a2,8); c2=c1+d2; b2=ror(b1^c2,7)
    return b2,d2
t0=time.time(); res={}
for s in (8,-8):
    cnt=0; sols=[]
    for hi in range(256):
        w=(np.arange(1<<24,dtype=np.uint64)+(np.uint64(hi)<<np.uint64(24))).astype(np.uint32)
        b1,d1=c3(w); b2,d2=c3(w+np.uint32(s&0xFFFFFFFF))
        ok=(b1==b2)&(d1==d2); k=int(ok.sum()); cnt+=k
        if k and len(sols)<6: sols+= [hex(int(v)) for v in w[ok][:6-len(sols)]]
    res[s]=(cnt,sols); print('shift %+d: w4 with equal (b,d) outputs, of 2^32: %d  first: %s  (%.0fs)'%(s,cnt,sols,time.time()-t0),flush=True)
