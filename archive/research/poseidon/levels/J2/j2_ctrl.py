import sys; sys.argv=['x']
from j2_toy import *
# det=0 control: find toy matrices with det[e0;e0M;e0M^2]=0, show R3&R4&R5 pairs > 0, and compare det!=0
for q in (23,29,37):
    zs=[sd for sd in range(1,400) if Toy(q,sd).det_trail()==0][:2]
    nz=[sd for sd in range(1,6) if Toy(q,sd).det_trail()!=0][:1]
    for sd in zs+nz:
        t=Toy(q,sd); N=q*q
        NK=np.repeat(np.arange(q,dtype=np.int64),q); RHO=np.tile(np.arange(q,dtype=np.int64),q)
        s=[NK,RHO,np.full_like(NK,t.cap)]
        for i in range(4): s=t.rnd(s,i,True)
        Ls=[s[0]]
        for i in (4,5,6): s=t.rnd(s,i,False); Ls.append(s[0])
        def pr(k):
            key=np.zeros(N,dtype=np.int64)
            for L in Ls[:k]: key=key*q+L
            _,c=np.unique(key,return_counts=True); return int((c*(c-1)//2).sum())
        print('q=%d seed=%d det=%d  pairs equal R3&R4: %d  R3&R4&R5: %d  R3..R6: %d  (random %.1f / %.2f / %.3f)'%(q,sd,t.det_trail(),pr(2),pr(3),pr(4),N*N/2/q**2,N*N/2/q**3,N*N/2/q**4))
