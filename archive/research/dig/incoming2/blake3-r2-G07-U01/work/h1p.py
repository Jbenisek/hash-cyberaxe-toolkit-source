from fractions import Fraction as F
import math
# R2: recount of the time formula of 1a92bf64 section 10.4/11 and the rho=3071 re-price
D=2**128; K=2**21-1
def frames(f,m): return -(-int(m*10**9*D)//(K*int(f*10**9)*10**9//10**9)) if False else math.ceil(F(m)*D/(K*f))
def T(f,m,S):
    fr=frames(f,m); O=S+2**46+fr*2443836395520
    return math.log2(O/430+2**38), fr
f=F(5,7)*138646913024
m0=F(515,1000)
for S in [0,2**60,2**64,2**70]:
    print("S",S,"T(m=.515)=%.5f"%T(f,m0,S)[0])
b=lambda r: (lambda ro:(F(2*ro)-r)/(ro*(ro+1)))(math.floor(r)+1)
print("b(0.0065)=",float(b(F(65,10000))),"1-rho/2=",1-0.0065/2)
print("b(3071)=",b(3071),"1/3072")
mu_needed_orig=m0*(1-F(65,10000)/2)   # sum mu*b required
for lab,req in [("keep proof's 0.51332625",mu_needed_orig),("exact -ln(0.6)",F(-math.log(0.6))),("-ln(1-0.40) with 0.40149 bound",F(-math.log(1-0.4)))]:
    m1=req/b(3071)
    for S in [0,2**64]:
        t1,fr=T(f,m1,S); print(lab,"m_total=%.3f"%float(m1),"S=%d"%S,"T=%.5f"%t1,"delta=%.5f"%(t1-101.9196),"log2 frames=%.4f"%math.log2(fr))
# R4 sensitivity: d log2 T / d rho (frames dominated) around rho=0.0065 and a few points
for r in [0.0065,0.5,1,3071]:
    h=1e-6; 
    if r<1: d=(math.log2(1/float(b(F(r+h))))-math.log2(1/float(b(F(r)))))/h
    else: d=None
    print("rho",r,"log2(1/b)=%.4f"%math.log2(1/float(b(F(r)))),"slope bit/unit=",d)
print("bits per doubling of rho at large: log2(rho)->",math.log2(3071))
# rho that costs +1 bit over 0.0065: b=b(0.0065)/2
print("rho for +1 bit over 0.0065:",2*(1-(1-0.0065/2)/2))
print("rho for +1 bit over 3071 is below any: b=1/3072 is the lower limit (cap)")
