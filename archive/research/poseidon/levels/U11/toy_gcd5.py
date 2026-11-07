"""U11: what X1 needs: gcd(5,q-1)=1. Toys with gcd=5 (S-box not a bijection): full-state collisions appear."""
import numpy as np
from math import gcd
from toy_u11 import make_toy, run
for q in (11, 31, 41, 61, 71, 101, 151, 251, 257, 211):
    M, RC = make_toy(q, 1)
    nk, rho = np.meshgrid(np.arange(q,dtype=np.int64),np.arange(q,dtype=np.int64),indexing='ij'); nk=nk.ravel(); rho=rho.ravel()
    for r in (1,2):
        lv = run(q,M,RC,r,nk,rho,(1<<65)%q)
        L = lv[-1][1]; key=(L[0]*q+L[1])*q+L[2]
        print(f"q={q} gcd(5,q-1)={gcd(5,q-1)} r={r}: distinct full outputs {len(np.unique(key))} of {q*q}; distinct lane0 {len(np.unique(L[0]))}")
