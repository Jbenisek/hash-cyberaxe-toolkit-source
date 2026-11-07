# existence of two-equal-output local pins in ONE first-word-difference G call with identical inputs
# case AC: outputs a,c equal (b,d differ); case BD (control, as in Fact P for C3): outputs b,d equal.
import numpy as np, random, sys, time
M=0xffffffff
def ror(x,n): return ((x>>n)|(x<<(32-n)))&M
def rol(x,n): return ror(x,32-n)
def G(a,b,c,d,x,y):
    a=(a+b+x)&M; d=ror(d^a,16); c=(c+d)&M; b=ror(b^c,12)
    a=(a+b+y)&M; d=ror(d^a,8); c=(c+d)&M; b=ror(b^c,7); return a,b,c,d
U=np.uint32
def vror(x,n): return (x>>U(n))|(x<<U(32-n))
def vrol(x,n): return vror(x,32-n)
CH=1<<24
def solve(fn,total=1<<32):
    sols=[]
    for s in range(0,total,CH):
        u=np.arange(s,s+CH,dtype=np.uint32)
        z=fn(u)
        idx=np.nonzero(z)[0]
        for i in idx: sols.append(int(u[i]))
    return sols
def case(kind,seed):
    R=random.Random(seed); t0=time.time()
    while True:
        a,b,c,d,x,y=[R.getrandbits(32) for _ in range(6)]
        a1=(a+b+x)&M; d1=ror(d^a1,16); c1=(c+d1)&M; b1=ror(b^c1,12)
        if kind=='AC':
            # eq1 over x' : a1'+b1' == a1+b1
            def f1(u):
                a1p=(U(a)+U(b)+u); d1p=vror(U(d)^a1p,16); c1p=U(c)+d1p; b1p=vror(U(b)^c1p,12)
                return (a1p+b1p)==U((a1+b1)&M)
            s1=[v for v in solve(f1) if v!=x]
            print(kind,"eq1 solutions for x':",len(s1),"t=%.0fs"%(time.time()-t0),flush=True)
            if not s1: continue
            xp=s1[0]; a1p=(a+b+xp)&M; d1p=ror(d^a1p,16); c1p=(c+d1p)&M; b1p=ror(b^c1p,12)
            def f2(u):
                a2=U(a1+b1)&U(M); a2=(U((a1+b1)&M)+u); d2=vror(U(d1)^a2,8); d2p=vror(U(d1p)^a2,8)
                return (U(c1)+d2)==(U(c1p)+d2p)
            s2=solve(f2)
            print(kind,"eq2 solutions for y:",len(s2),"t=%.0fs"%(time.time()-t0),flush=True)
            if not s2: continue
            yy=s2[0]
        # verify
        A=G(a,b,c,d,x,yy); B=G(a,b,c,d,xp,yy)
        print('A out',[hex(v) for v in A]); print('B out',[hex(v) for v in B]); print('equal outputs a,b,c,d:',[A[i]==B[i] for i in range(4)])
        print(kind,"inputs",[hex(v) for v in (a,b,c,d)],"x,x'",hex(x),hex(xp),"y,y'",hex(y),hex(yy))
        # A uses y; B uses y' = yy-offset : a2 free = a1+b1+y_A ; our u was a2 for B? see check
        return A,B
if __name__=="__main__":
    print(case('AC',int(sys.argv[1])))
