import math
from fractions import Fraction as F
exec(open('h1p.py').read().split("# R4")[0].split("f=F(5,7)")[0])
f=F(5,7)*138646913024
for p in [0.39,0.40]:
    for kind,dil in [("-ln(1-p)",-math.log(1-p))]:
        m=F(dil)*3072
        print(p,"T(rho=3071)=%.5f"%T(f,m,2**64)[0])
# also the 0.39 with 1/3072 cap variant frames using eps: required 0.39
# R3: LP control of Lemma S8: min Pr(N>0)/mu given mu, rho, support 0..Kmax
import numpy as np
from scipy.optimize import linprog
def lp(rho,Kmax,mu=1.0):
    ks=np.arange(1,Kmax+1)
    # variables p_k >=0 ; scaled so mu=1 (sum k p_k=1): minimise sum p_k
    A=np.vstack([ks,ks*(ks-1)]); bb=[1.0,rho]
    r=linprog(np.ones(Kmax),A_eq=A,b_eq=bb,bounds=(0,None),method='highs')
    return r.fun if r.status==0 else None
def b(r):
    ro=math.floor(r)+1; return (2*ro-r)/(ro*(ro+1))
mx=0
for rho in [0,0.0065,0.5,1,1.5,2,7.3,100,3070.5,3071]:
    v=lp(rho,3072); print("rho",rho,"LP min Pr/mu=%.10g"%v,"b=%.10g"%b(rho),"diff=%.2e"%(v-b(rho))); mx=max(mx,abs(v-b(rho)))
print("max |LP-b|",mx)
# negative control: linear formula 1-rho/2 at rho=3071 is wrong (negative) ; LP says 1/3072
print("neg control 1-rho/2 at 3071 =",1-3071/2,"LP:",lp(3071,3072))
# cap control: with cap Kmax=3072 and rho=3071 the extremal law is point mass at 3072 (+0): infeasible for rho>3071
print("rho=3071.5 feasible with Kmax 3072?",lp(3071.5,3072))
