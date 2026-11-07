import sys; sys.argv=['x']
from u3_toy import mk_toy
import numpy as np
for q,sd in ((23,1),(23,2),(17,1),(17,2),(37,1),(37,2)):
    M,_=mk_toy(q,sd); M=M.astype(object)
    e0=np.array([1,0,0],dtype=object); r1=e0.dot(M)%q; r2=r1.dot(M)%q
    A=[list(e0),list(r1),list(r2)]
    det=(A[0][0]*(A[1][1]*A[2][2]-A[1][2]*A[2][1])-A[0][1]*(A[1][0]*A[2][2]-A[1][2]*A[2][0])+A[0][2]*(A[1][0]*A[2][1]-A[1][1]*A[2][0]))%q
    print(q,sd,"det[e0;e0M;e0M^2] mod q =",det)
