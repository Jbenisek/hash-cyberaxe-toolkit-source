# LEDGER.EVALS R2/R3: recount Q from the plan and a Monte Carlo control of the birthday law that sets it:
# P(no collision among U distinct uniform draws from N) ~ exp(-U(U-1)/2N); U = sqrt(2 lambda N) gives 1-exp(-lambda).
import numpy as np
from math import sqrt, exp, log2
from common import rho as R
p=R.plan(256); N=p['N']
ureq=R.isqrt(2*N*R.LAMBDA.numerator//R.LAMBDA.denominator)+2
print('recount: ureq = sqrt(2 N lambda) = %.9f * 2^128 (lambda 0.497) ; + 28 L = %.6f ; Q = 7B = %.9f * 2^128 ; B=%d'%(ureq/2**128,28*p['L']/2**128,p['Q']/2**128,p['B']))
print('  Q check: (ureq + 28L + 1)/(1-1.5e-4) = %.9f ; ledger Q = %.9f ; 7B >= that: %s'%(((ureq+28*p['L']+1)/(1-0.00015))/2**128,p['Q']/2**128,p['Q']>=(ureq+28*p['L']+1)/(1-0.00015)))
print('  plain-birthday value in proposed cell B3R3-G1: 0.9943 = sqrt(2*ln(1/0.61)) = %.4f (success 0.39 exactly); filed 0.99700 uses lambda 0.497 (success 0.39165)'%sqrt(2*0.4943))
rng=np.random.default_rng(1012)
lgN=32; Nn=1<<lgN
for scale in (0.9,1.0,1.1):
    lam=0.497*scale*scale
    U=int(round(sqrt(2*lam*Nn))); T=3000; hit=0
    for _ in range(T):
        a=rng.integers(0,Nn,U,dtype=np.uint64)
        if len(np.unique(a))<U: hit+=1
    pr=1-exp(-U*(U-1)/(2*Nn)); se=sqrt(pr*(1-pr)/T)
    print('MC control N=2^32, U=%d (U/sqrtN=%.4f, scale %.1f): observed %.4f (se %.4f), law 1-exp(-U(U-1)/2N) = %.4f, z=%.2f'%(U,U/sqrt(Nn),scale,hit/T,se,pr,(hit/T-pr)/se))
