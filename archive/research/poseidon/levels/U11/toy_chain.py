"""U11: chains of lane-0 agreement R3.M & R4.M & R5.M (and R6.M for r=3) + free boundary counts, exhaustive toy."""
import sys, numpy as np
from toy_u11 import make_toy, run, pairs_equal
for q, seed in [(257,1),(257,2),(257,3),(769,1),(1009,1)]:
    M, RC = make_toy(q, seed); cap=(1<<65)%q
    nk, rho = np.meshgrid(np.arange(q,dtype=np.int64),np.arange(q,dtype=np.int64),indexing='ij'); nk=nk.ravel(); rho=rho.ravel()
    for r in (1,2,3):
        lv = run(q,M,RC,r,nk,rho,cap)
        names=[f"R{i}" for i,_ in lv]
        s3 = lv[3][1][0]
        keys = [s3]
        row=[]
        for j in range(4,4+r):
            keys.append(lv[j][1][0])
        # cumulative keys
        cum = np.zeros_like(s3)
        out=[]
        for kk,lane in enumerate(keys):
            cum = cum*q+lane
            out.append(pairs_equal(cum))
        # then final (R63) added
        cum2 = cum*q + lv[-1][1][0]
        out.append(pairs_equal(cum2))
        N=q*q; P=N*(N-1)//2
        print(f"q={q} seed={seed} r={r}: pairs equal at R3 | +R4 | ...| +R63 =", out, " expected(indep)=", [round(P/q**(i+1)) for i in range(len(out))])
