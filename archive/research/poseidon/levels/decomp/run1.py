from decomp import *
import time
random.seed(7)
# controls
L=Line(0)
t=time.time()
for dd in (5,25):
    Bc=R([0]+[random.randrange(p) for _ in range(dd-1)]+[1])
    s0=s0_line(L,Bc)   # state affine in Z=Bc(W)
    r=0; n=dd*5**6
    B,rem=screen(s0,r,dd,n)
    print('control d=%d: B recovered ==Bc(+const0)? %s ; remainder degree %d (constant => <=0)'%(dd,B==Bc,rem.degree()),flush=True)
    for d2 in (5,25):
        if d2==dd: continue
        n2=n
        if n2%d2: continue
        B2,rem2=screen(s0,r,d2,n2)
        print('  same F, wrong d=%d: remainder deg %d'%(d2,rem2.degree()),flush=True)
print(time.time()-t)
