from decomp import *
import time
# digit test on control
random.seed(3)
L=Line(1); Bc=R([0]+[random.randrange(p) for _ in range(4)]+[1])
F=circuit(s0_line(L,Bc),0)
print('control full digits d=5 (nonconst digits, levels):',digits(F,Bc),flush=True)
for r in (0,1,2):
  for j in (0,1,2):
    L=Line(j); n=5**(6+r); s0=s0_line(L)
    res=[]
    for d in (5,25,125):
        t=time.time()
        B,rem=screen(s0,r,d,n)
        res.append((d,rem.degree(),round(time.time()-t,1)))
    print('r',r,'j',j,'screen (d, remdeg, secs):',res,flush=True)
    if r<=2:
        t=time.time(); F=circuit(s0,r); 
        assert F.degree()==n
        out=[]
        for d in (5,25,125):
            B,_=screen(s0,r,d,n)
            out.append((d,digits(F,B)[0]))
        print('   full expansion deg',F.degree(),'digit test (d, #nonconst digits):',out,round(time.time()-t,1),flush=True)
