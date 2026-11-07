# PREM.H1 R4 (score sensitivity to the random-mapping rate) and PREM.H2 R2 (own recount of loss terms) / R4 (score sensitivity)
from fractions import Fraction
from math import log2, exp, factorial, log, sqrt
import numpy as np
from common import rho as R
p=R.plan(256); L=p['L']; N=p['N']; Q=p['Q']
lg=R.ledger(256); T0=log2(lg['total']/638)
print('base time_log2 = %.5f ; Q/2^128 = %.6f ; Q/L = %.2f ; B = %d'%(T0,Q/2**128,Q/L,p['B']))
# ---- H1 R4
lam0=R.LAMBDA
def T_for(lam,inflight=R.INFLIGHT,cutloss=R.CUTLOSS,kappa=R.KAPPA):
    R.LAMBDA=lam; R.INFLIGHT=inflight; R.CUTLOSS=cutloss; R.KAPPA=kappa
    try: return log2(R.ledger(256)['total']/638)
    finally: R.LAMBDA=lam0; R.INFLIGHT=28; R.CUTLOSS=Fraction(15,100000); R.KAPPA=12
print('H1 R4: rate deficit eps (collision rate (1-eps) of random-mapping rate), success-0.39 restored by Q ~ 1/sqrt(1-eps):')
for eps in (0.001,0.0046,0.01,0.05,0.10,0.25,0.5):
    lam=lam0/Fraction(1-eps).limit_denominator(10**9)
    d=T_for(lam)-T0
    print('  eps=%.4f: ledger time +%.4f bit (closed form 0.5*log2(1/(1-eps)) = %.4f); new T = %.4f'%(eps,d,0.5*log2(1/(1-eps)),T0+d))
print('  slope: dT/d(eps) at 0 = %.4f bit per unit eps (= 0.5/ln2)'%(0.5/log(2)))
# eps at which the claimed success 0.39 is just lost (no time repair), with total loss 1.6e-4 (proof) and 1.2e-4 (claim.json text)
for loss in (1.6e-4,1.2e-4):
    lam_need=-log(1-(0.39+loss)); eps=1-lam_need/float(lam0)
    print('  eps_max for success>=0.39 with losses %.1e: %.5f (1-exp(-0.497(1-eps))-loss=0.39)'%(loss,eps))
# raising collision rate: gain
for up in (0.01,0.05,0.10,0.25,1.0):
    print('  if rate were (1+%.2f) of model: ledger could shrink by %.4f bit (not claimed)'%(up,0.5*log2(1+up)))
# success target: time vs required p
for pp in (0.30,0.39,0.5,0.63,0.9):
    lam=Fraction(-log(1-pp)).limit_denominator(10**6)+Fraction(0)
    print('  required success p=%.2f: lambda=%.4f -> time %.4f bit (delta %+.4f)'%(pp,float(lam),T_for(lam),T_for(lam)-T0))
# ---- H2 R2 own recount
print('H2 R2 own recount:')
tail=sum(Fraction(28)**j/factorial(j) for j in range(7))*Fraction(exp(-28)).limit_denominator(10**60)
tail=float(sum(28**j/factorial(j) for j in range(7))*exp(-28))
print('  P(sum of 7 Exp(L) ages > 28 L) = e^-28 sum_{j<7} 28^j/j! = %.4e (proof 5.8e-7)'%tail)
mean_cut=(Q/L)*exp(-12)
from math import exp as ex
pk=[ex(-mean_cut)*mean_cut**k/factorial(k) for k in range(3)]
print('  trails Q/L = %.1f ; cut-trail mean = %.4f (proof 16,365*e^-12=0.1006) ; P(K=0,1,2)=%.4f %.4f %.4f ; P(K>=3)=%.2e'%(Q/L,mean_cut,*pk,1-sum(pk)))
cutc=float(R.CUTLOSS)*1.0
# loss lowering of success for K=1,2: (K*c/Q - allowance) -> lowers lambda by U*dU/N ; reproduce 3.5e-4 and 8.0e-4
c_over_Q=12*L/Q
def dsucc(K):
    extra=max(0.0,K*c_over_Q-float(R.CUTLOSS))
    lam=0.497*(1-2*extra)  # U ~ ureq*(1-extra) -> lambda ~ lam*(1-2 extra)
    return exp(-lam)-exp(-0.497) if False else (exp(-0.497)*(1-exp(0.497-lam)))*-1 if False else (exp(-lam)-exp(-0.497))
d1,d2=dsucc(1)*-1,dsucc(2)*-1
print('  cut c/Q = %.3e ; allowance %.1e ; success loss given K=1: %.2e , K=2: %.2e (proof 3.5e-4, 8.0e-4 : sign: lowers P by these)'%(c_over_Q,float(R.CUTLOSS),abs(d1),abs(d2)))
cutdef=pk[1]*3.5e-4+pk[2]*8.0e-4+(1-sum(pk))*0.3916
print('  cut-trail deficit (proof numbers 3.5e-4,8.0e-4) = %.2e (proof 9.7e-5) ; with my K=1,2 losses = %.2e'%(cutdef,pk[1]*abs(d1)+pk[2]*abs(d2)+(1-sum(pk))*0.3916))
inside=Q*L/N
print('  expected colliding pairs inside one trail <= Q L/N = 2^%.2f'%log2(inside))
keyfalse=(p['tmax']**2/2)/2.0**64
print('  64-bit key false matches among %d entries: %.2e = 2^%.1f (proof < 2^-36)'%(p['tmax'],keyfalse,log2(keyfalse)))
# table-overflow Chernoff: Poisson mean m=Q/L, need >= tmax+1
m=Q/L; k=p['tmax']+1
chern=-(m-k+k*log(k/m))   # ln of Chernoff bound exp(-m)(e m/k)^k
print('  table overflow: Poisson mean %.0f need >= %d: Chernoff ln P = %.1f (e^-125.5 = 10^-54.5 claimed)'%(m,k,chern))
mu2=7*p['B']/2**32
print('  stage-2: mu2 = %.3e ; abort needs 2 mu2+65 ; Chernoff exponent mu2(2 ln2 - 1) = %.3e'%(mu2,mu2*(2*log(2)-1)))
U=0.99985*Q-28*L-1
print('  U/2^128 = %.6f ; ureq/2^128 = %.6f ; lambda_eff = U(U-1)/2N = %.5f ; 1-exp(-lam)=%.5f'%(U/2**128,(R.isqrt(2*N*497//1000)+2)/2**128,U*(U-1)/(2*N),1-exp(-U*(U-1)/(2*N))))
tot=tail+0+pk[0]*0+ (6.1e-5)+cutdef+2**-36
print('  loss sum (5.8e-7 + 6.1e-5 [as written] + %.1e + 2^-36) = %.2e'%(cutdef,tot))
# the 6.1e-5 term: what is it? 1.5e-4 allowance covers 0.20 of a cut trail; P(K>=1)*...? recompute: probability that the in-flight sum exceeds, plus P(K=1)*... print candidates
print('  P(K>=1)*(allowance fraction)= %.2e'%((1-pk[0])*0.2))
# ---- H2 R4 sensitivity: ledger time vs loss parameters
print('H2 R4: ledger sensitivity')
for nm,kw in (('INFLIGHT 28 -> 56',dict(inflight=56)),('INFLIGHT 28 -> 14',dict(inflight=14)),('CUTLOSS x10',dict(cutloss=Fraction(15,10000))),('CUTLOSS x0',dict(cutloss=Fraction(0))),('KAPPA 12 -> 24 (cap doubles)',dict(kappa=24)),('KAPPA 12 -> 8',dict(kappa=8))):
    print('  %-30s time %+.5f bit'%(nm,T_for(lam0,**kw)-T0))
