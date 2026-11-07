"""U10 Q1: toy q=1000003, sampling. X2 plane, X5 carry, X7 final form, + X1-ish injectivity sample"""
import random, math, sys
from toylib import *
q=1000003
print("q prime",is_prime(q),"gcd(5,q-1)",math.gcd(5,q-1),"q-1=",q-1,"v2=",v2(q-1),"q mod 4",q%4,"q mod 5",q%5)
rnd=random.Random(1)
for cauchy in (True,False):
  for r in (1,2):
    t=Toy(q,11,cauchy=cauchy)
    M=t.M; Mi=None
    d=det3(M,q); di=inv(d,q)
    # adjugate inverse
    def minor(i,j):
        rows=[a for a in range(3) if a!=i]; cols=[b for b in range(3) if b!=j]
        return (M[rows[0]][cols[0]]*M[rows[1]][cols[1]]-M[rows[0]][cols[1]]*M[rows[1]][cols[0]])
    Mi=[[((-1)**(i+j))*minor(j,i)*di%q for j in range(3)] for i in range(3)]
    assert all(sum(M[i][k]*Mi[k][j] for k in range(3))%q==(1 if i==j else 0) for i in range(3) for j in range(3))
    K=pow(t.cap+t.RC[0][2],5,q)
    ok2=ok5=ok7=0;N=20000
    sched=t.sched(r); lastpart=sched[3+r][0]  # last partial idx
    for _ in range(N):
        nk,rho=rnd.randrange(q),rnd.randrange(q)
        # X2: after R0, (M^-1 s)_2 == K
        s=t.perm_int([nk,rho,t.cap],r); 
        s0=t.perm([nk,rho,t.cap],r,upto=1)
        if sum(Mi[2][j]*s0[j] for j in range(3))%q==K: ok2+=1
        # (A,B) reparam: H(A,B) equals hash: start from M*(A,B,K)
        # X5: partial round normal form; state after R3 -> after R4
        s3=t.perm([nk,rho,t.cap],r,upto=4)
        w=pow((s3[0]+t.RC[4][0])%q,5,q)
        v=[w,(s3[1]+t.RC[4][1])%q,(s3[2]+t.RC[4][2])%q]
        direct=t.perm([nk,rho,t.cap],r,upto=5)
        pred=[sum(M[i][j]*v[j] for j in range(3))%q for i in range(3)]
        if pred==direct: ok5+=1
        # X7: output = row0 . T, T=(state after R(last-1)+c63)^5
        sB=t.perm([nk,rho,t.cap],r,upto=len(sched)-1)
        T=[pow((sB[i]+t.RC[63][i])%q,5,q) for i in range(3)]
        y=sum(M[0][j]*T[j] for j in range(3))%q
        if y==s[0]: ok7+=1
    print(f"cauchy={cauchy} r={r}: X2 {ok2}/{N}  X5 {ok5}/{N}  X7 {ok7}/{N}")
# 5th-root inverse check at q: d=5^-1 mod q-1
dd=pow(5,-1,q-1); x=rnd.randrange(1,q); print("5th root inverse d=",dd,"check",pow(pow(x,5,q),dd,q)==x)
# injectivity sample: 3-lane output of 2e5 random inputs distinct? plus lane0 collisions found by birthday
t=Toy(q,11); seen={}; full=set(); coll0=0; N=200000
for _ in range(N):
    nk,rho=rnd.randrange(q),rnd.randrange(q)
    s=tuple(t.perm_int([nk,rho,t.cap],1))
    full.add((nk,rho,s))
    if s[0] in seen and seen[s[0]][:2]!=(nk,rho): coll0+=1
    seen[s[0]]=(nk,rho,s)
print("N",N,"distinct full outputs among distinct inputs ok; lane0 birthday collisions seen",coll0,"expected approx",N*N/2/q)
