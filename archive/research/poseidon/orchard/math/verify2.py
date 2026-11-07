from attack import *
from math import comb
out=[]
def P(*a):
    print(*a); out.append(' '.join(str(x) for x in a))
def rank_mod(rows):
    rows=[r[:] for r in rows]; rk=0; ncol=len(rows[0])
    for c in range(ncol):
        piv=None
        for i in range(rk,len(rows)):
            if rows[i][c]%p: piv=i;break
        if piv is None: continue
        rows[rk],rows[piv]=rows[piv],rows[rk]
        inv=pow(rows[rk][c],-1,p)
        rows[rk]=[x*inv%p for x in rows[rk]]
        for i in range(len(rows)):
            if i!=rk and rows[i][c]%p:
                f=rows[i][c]; rows[i]=[(x-f*y)%p for x,y in zip(rows[i],rows[rk])]
        rk+=1
    return rk
def quint(alpha,beta):   # coefficients of (alpha+beta t)^5, t^0..t^5
    return [comb(5,i)*pow(beta,i,p)*pow(alpha,5-i,p)%p for i in range(6)]
# (a) is the origin of the round-1 S-box input space on the plane P ?
# x = M (U,V,K) + RC1 = 0  => (U,V,K)^T = -M^{-1} RC1
def inv3(M):
    a,b,c=M[0];d,e,f=M[1];g,h,i=M[2]
    det=(a*(e*i-f*h)-b*(d*i-f*g)+c*(d*h-e*g))%p
    di=pow(det,-1,p)
    adj=[[e*i-f*h,c*h-b*i,b*f-c*e],[f*g-d*i,a*i-c*g,c*d-a*f],[d*h-e*g,b*g-a*h,a*e-b*d]]
    return [[x*di%p for x in r] for r in adj]
Mi=inv3(MDS)
sol=[(-sum(Mi[k][m]*RC[1][m] for m in range(3)))%p for k in range(3)]
P('origin of round-1 S-box input space lies on plane P only if 3rd comp of -M^-1 RC1 equals K:', sol[2]==K)
P('  (3rd comp, K) =', hex(sol[2]), hex(K))
# is e_k in the direction space (cols 0,1 of M) ?  <=> 2x2 minor of rows != k, cols 0,1 is 0
for k in range(3):
    I=[m for m in range(3) if m!=k]
    P('e_%d in direction space of P?'%k, (MDS[I[0]][0]*MDS[I[1]][1]-MDS[I[0]][1]*MDS[I[1]][0])%p==0)
# dim span{1, x_k^5} along the three lines (round-1 S-box output) and along the round-2 input line
for j in range(3):
    L=Line(j)
    # round-1 input line x_k = d_k tau + xQ_k  (tau)
    rows=[[1,0,0,0,0,0]]+[quint(L.xQ[k],L.d[k]) for k in range(3)]
    P('j',j,'dim span{1,x_k(tau)^5} (round 1) =',rank_mod(rows),'(<=2 means round-1 skip works)')
    alpha=mds(L.v0); beta=mds(L.v1)
    alpha=[(alpha[k]+RC[2][k])%p for k in range(3)]
    rows=[[1,0,0,0,0,0]]+[quint(alpha[k],beta[k]) for k in range(3)]
    P('j',j,'dim span{1,l_k(W)^5} (round 2) =',rank_mod(rows),'(<=2 would allow a round-2 skip)')
open('verify2_out.txt','w').write('\n'.join(out))
