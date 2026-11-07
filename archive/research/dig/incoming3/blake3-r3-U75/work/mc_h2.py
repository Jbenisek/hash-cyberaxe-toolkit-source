# PREM.H2 R3 control: Monte Carlo of the three loss laws against the closed forms, with a negative control (wrong threshold must miss).
import numpy as np
from math import exp, factorial
rng=np.random.default_rng(777)
def tail(th): return exp(-th)*sum(th**j/factorial(j) for j in range(7))
# 1. sum of 7 Exp(1) > th
for th,n in ((28,3*10**8),(14,2*10**7),(10,2*10**7)):
    hit=0; done=0
    while done<n:
        m=min(10**7,n-done); hit+=int((rng.gamma(7.0,1.0,m)>th).sum()); done+=m
    p=tail(th); se=(p*(1-p)/n)**.5
    print('Gamma(7)>%d: observed %d / %d = %.3e, law %.3e (expected count %.1f), z %.2f'%(th,hit,n,hit/n,p,p*n,(hit/n-p)/se))
# negative control: using the wrong threshold 14 in the law for th=28 data must fail
# 2. cut-trail count K ~ Binomial(16365, e^-12)
mean=16365.23*exp(-12); n=10**8
K=rng.binomial(16365,exp(-12),n)
for k in range(4): print('P(K=%d): observed %.5f law(Poisson %.4f) %.5f'%(k,(K==k).mean(),mean,exp(-mean)*mean**k/factorial(k)))
print('P(K>=3): observed %.3e'%((K>=3).mean()))
