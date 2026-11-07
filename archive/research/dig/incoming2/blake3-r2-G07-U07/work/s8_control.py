# Lemma S8 control: Pr(N>0) >= mu*b(rho), b(rho)=(2r-rho)/(r(r+1)), r=floor(rho)+1, exact on finite laws; then a negative control.
# Plus the cost table of the dependence bound in bits and the dossier arithmetic.
import random, math
from fractions import Fraction as Fr
def b(rho):
    r=math.floor(rho)+1; return (2*r-rho)/(r*(r+1))
def stats(law):  # law: dict k->prob (Fraction)
    mu=sum(k*p for k,p in law.items()); fm=sum(k*(k-1)*p for k,p in law.items())
    pos=sum(p for k,p in law.items() if k>0); return mu,(fm/mu if mu else 0),pos
random.seed(20261012)
viol=0; tight=0; n=0; worst=1e9
for it in range(20000):
    K=random.randint(1,30); ks=sorted(random.sample(range(1,60),K))
    ws=[random.random()**random.choice([1,3,8]) for _ in ks]
    tot=sum(ws); scale=random.choice([1e-1,1e-3,1e-6])
    law={k:Fr(w/tot*scale).limit_denominator(10**12) for k,w in zip(ks,ws)}
    law[0]=1-sum(law.values())
    mu,rho,pos=stats(law); n+=1
    lhs=float(pos); rhs=float(mu)*b(float(rho))
    worst=min(worst,lhs/rhs)
    if lhs < rhs*(1-1e-12): viol+=1
print("S8 positive control: %d random laws, violations %d, min Pr(N>0)/(mu*b(rho)) = %.6f"%(n,viol,worst))
# tightness: two-point law at {0,r}: equality when rho integer-ish: N in {0,r}
r=5; p=Fr(1,1000); law={0:1-p,r:p}; mu,rho,pos=stats(law)
print("tight law {0,5}: Pr=%s mu*b=%.9e ratio %.9f"%(pos,float(mu)*b(float(rho)),float(pos)/(float(mu)*b(float(rho)))))
# negative control: use a claimed rho smaller than the truth -> bound must fail for some laws
fails=0; m=0
for it in range(5000):
    K=random.randint(2,10); ks=sorted(random.sample(range(1,40),K)); ws=[random.random() for _ in ks]
    tot=sum(ws); law={k:Fr(w/tot*1e-3).limit_denominator(10**12) for k,w in zip(ks,ws)}; law[0]=1-sum(law.values())
    mu,rho,pos=stats(law); m+=1
    if float(pos) < float(mu)*b(float(rho)/10): fails+=1   # claim rho 10x too small
print("S8 negative control (claimed rho = true/10): bound fails on %d of %d laws (must be >0)"%(fails,m))
# threshold: largest rho with exp(-lam*b(rho)) <= exp(-lam)+0.001, lam=0.49594
lam=0.49594; tgt=math.exp(-lam)+0.001
lo,hi=0.0,1.0
for _ in range(100):
    mid=(lo+hi)/2
    if math.exp(-lam*b(mid))<=tgt: lo=mid
    else: hi=mid
print("max rho_c keeping exp(-lam*b)<=exp(-lam)+0.001: %.6f (clause states 0.0065); exp(-0.4943281)=%.6f < %.6f"%(lo,math.exp(-0.4943281),tgt))
print("b(0.0065)=%.5f  exponent lam*b=%.7f"%(b(0.0065),lam*b(0.0065)))
# cost of the dependence bound in bits (run length scales as 1/b at equal success), relative to rho=0.0065 as filed
print("rho_c bound      b(rho)      extra bits vs filed 0.0065")
for rho in (0.0,0.0065,0.05,0.5,1.0,2.0,23.0,3071.0):
    print("%-14g  %.6e   %+.4f"%(rho,b(rho),math.log2(b(0.0065)/b(rho))))
print("value of the filed clause itself vs rho=0: %.5f bits; d bits / d rho at 0.0065 = %.4f per 1.0, %.6f per 0.001"%(math.log2(b(0)/b(0.0065)),1/(2*math.log(2)*(1-0.0065/2)),1/(2*math.log(2)*(1-0.0065/2))/1000))
# dossier arithmetic (fa761365 Section 13 member-loop numbers and the 2^44 statement)
print("fa761365: 597.82/519.81 = %.4f ; 0.0065 / 2^-51.474 = 2^%.3f ; B3U: 0.0065/2^-51.874 = 2^%.3f"%(597.82/519.81, math.log2(0.0065)+51.474, math.log2(0.0065)+51.874))
print("2^19*2^21*2^-91.868 = 2^%.3f"%(19+21-91.868))
print("1a92bf64 fallback: log2(3072)=%.4f ; filed 101.9196 -> 113.4454 = +%.4f"%(math.log2(3072),113.4454-101.9196))
