from u5_lib import *
T,S,D = charpoly(MDS)
print("charpoly T,S,D hex", hex(T),hex(S),hex(D))
K = F3(T,S,D)
al = (0,1,0)
# check charpoly
assert K.pw(al,3) == tuple(((T*K.pw(al,2)[i] - S*al[i] + (D if i==0 else 0))%P) for i in range(3))
print("alpha^p == ? alpha:", K.frob(al)==al)
a1 = K.frob(al); a2 = K.frob(a1)
print("conjugate alpha^p  =", [hex(x) for x in a1]); print("conjugate alpha^p^2=", [hex(x) for x in a2])
print("trace(alpha)==T:", K.trace(al)==T, " norm(alpha)==D:", K.norm(al)==D)
print("alpha^(p^3)==alpha:", K.frob(a2)==al)
# distinct eigenvalues => diagonalisable
print("alpha, alpha^p, alpha^p^2 pairwise distinct:", len({al,a1,a2})==3)
# eigenvectors over F_{p^3}: kernel of M - lam I, via cross product of two rows
def eigvec(lam):
    R = [[ (tuple(MDS[i][j] for _ in range(1)) and (MDS[i][j],0,0)) if i!=j else K.sub((MDS[i][j],0,0), lam) for j in range(3)] for i in range(3)]
    def cross(u,v):
        c0 = K.sub(K.mul(u[1],v[2]), K.mul(u[2],v[1]))
        c1 = K.sub(K.mul(u[2],v[0]), K.mul(u[0],v[2]))
        c2 = K.sub(K.mul(u[0],v[1]), K.mul(u[1],v[0]))
        return [c0,c1,c2]
    v = cross(R[0],R[1])
    # normalise first coordinate to 1
    i0 = K.inv(v[0]); v = [K.mul(x,i0) for x in v]
    # check Mv = lam v
    for i in range(3):
        s = (0,0,0)
        for j in range(3): s = K.add(s, K.mul((MDS[i][j],0,0), v[j]))
        assert s == K.mul(lam, v[i])
    return v
v0 = eigvec(al); v1 = eigvec(a1); v2 = eigvec(a2)
print("eigenvector for alpha (normalised v_0=1): v1=",v0[1]," v2=",v0[2])
print("is eigvec(alpha^p) = frob(eigvec(alpha))?", [K.frob(x) for x in v0]==v1)
# conjugate eigenvector as polynomial in alpha: v0[1] = c0 + c1 a + c2 a^2
# Cauchy params
N = [[inv(MDS[i][j]) for j in range(3)] for i in range(3)]
xs = [0, (N[1][0]-N[0][0])%P, (N[2][0]-N[0][0])%P]
ys = [N[0][j] for j in range(3)]
assert all((xs[i]+ys[j])%P==N[i][j] for i in range(3) for j in range(3))
# displacement rank 1
Xd = [[xs[i] if i==j else 0 for j in range(3)] for i in range(3)]
Yd = [[ys[i] if i==j else 0 for j in range(3)] for i in range(3)]
A1 = matmul(Xd,MDS); A2 = matmul(MDS,Yd)
print("X M + M Y == all-ones:", all((A1[i][j]+A2[i][j])%P==1 for i in range(3) for j in range(3)))
json.dump({"xs":[hex(x) for x in xs],"ys":[hex(y) for y in ys]}, open("cauchy.json","w"))
