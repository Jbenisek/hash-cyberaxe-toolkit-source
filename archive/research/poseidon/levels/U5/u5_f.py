from u5_lib import *
T,S,D = charpoly(MDS); K=F3(T,S,D); al=(0,1,0); p=P; n=p**3-1
Mi=matinv(MDS)
cj=json.load(open("cauchy.json")); xs=[int(x,16) for x in cj["xs"]]; ys=[int(y,16) for y in cj["ys"]]
Xd=[[xs[i] if i==j else 0 for j in range(3)] for i in range(3)]; Yd=[[ys[i] if i==j else 0 for j in range(3)] for i in range(3)]
A=matmul(Yd,Mi); B=matmul(Mi,Xd); one=[1,1,1]
u=matvec(Mi,one); w=[sum(Mi[i][j] for i in range(3))%p for j in range(3)]
print("Y M^-1 + M^-1 X == +(M^-1 1)(1^T M^-1) (displacement rank 1 inherited by the inverse):",all((A[i][j]+B[i][j]-u[i]*w[j])%p==0 for i in range(3) for j in range(3)))
from u5_lib import det3
print("cross(row0,row2) constant = -detM ?:", 0x368d6421ff2e1f27f56143c10a3fac07bbf74d81048352202a3dffe2da985272==(-det3(MDS))%p)
print("--- special powers of M (generator => every power M^k is a_0+a_1 M+a_2 M^2) ---")
I3=[[1,0,0],[0,1,0],[0,0,1]]
def mpow(k):
    a=K.pw(al,k); M2=matmul(MDS,MDS)
    return [[(a[0]*I3[i][j]+a[1]*MDS[i][j]+a[2]*M2[i][j])%p for j in range(3)] for i in range(3)]
for q in [2,3,463,73,5839,12221196943,5187662682403,539204044132271846773,487887715480415483992657]:
    R=mpow(n//q)
    scalar = R[0][1]==0 and R[0][2]==0 and R[1][0]==0 and R[1][2]==0 and R[2][0]==0 and R[2][1]==0 and R[0][0]==R[1][1]==R[2][2]
    print(f"  M^(n/{q}): scalar={scalar}; "+(f"scalar value = {hex(R[0][0])} ({'-1' if R[0][0]==p-1 else 'other'})" if scalar else f"non-scalar, MDS={is_mds(R)}, then M^(n/q)^q == I: {matmul(R,I3)==R}"))
R=mpow((n//2)); print("M^((p^3-1)/2) == -I:", R==[[p-1,0,0],[0,p-1,0],[0,0,p-1]])
R=mpow(p*p+p+1); print("M^(p^2+p+1) == detM * I:", R==[[D if i==j else 0 for j in range(3)] for i in range(3)])
R=mpow(p-1); print("M^(p-1) is MDS:",is_mds(R)," ; M^(p+1) MDS:",is_mds(mpow(p+1))," ; M^p (Frobenius-twist matrix, similar to M) MDS:",is_mds(mpow(p)))
# Singer: orbit size of e0 under M is p^3-1 since alpha primitive -> verify by M^((p^3-1)/q) e0 != e0 for primes q (equivalent)
