import json, itertools, random
from eng import *
from polylib import *
random.seed(2026)
res={}
# plane in S-box-input coordinates of R1: x = A (U,V) + base ; normal n = col0 x col1
A=[[MDS[i][0],MDS[i][1]] for i in range(3)]
Kp=pow((CAPACITY+RC[0][2])%P,5,P)
base=[(MDS[i][2]*Kp+RC[1][i])%P for i in range(3)]
n=[(MDS[1][0]*MDS[2][1]-MDS[2][0]*MDS[1][1])%P,(MDS[2][0]*MDS[0][1]-MDS[0][0]*MDS[2][1])%P,(MDS[0][0]*MDS[1][1]-MDS[1][0]*MDS[0][1])%P]
delta=sum(n[i]*base[i] for i in range(3))%P
assert all(sum(n[i]*A[i][k] for i in range(3))%P==0 for k in range(2))
minors=[(MDS[i][k]*MDS[l][m]-MDS[i][m]*MDS[l][k])%P for i in range(3) for l in range(i+1,3) for k in range(3) for m in range(k+1,3)]
res['plane']=dict(normal_nonzero=[x!=0 for x in n], delta=hex(delta), delta_nonzero=delta!=0, all_nine_2x2_minors_nonzero=all(m!=0 for m in minors), n_minors=len(minors))
# enumeration: each lane i satisfies alpha_i*beta_i=0 where x_i = alpha_i + beta_i*tau ; assignments s_i in {a (alpha=0), b (beta=0), ab}
def rank2(rows):
    rows=[r[:] for r in rows if any(x%P for x in r)]
    if not rows: return 0
    if len(rows)==1: return 1
    for i in range(len(rows)):
        for k in range(i+1,len(rows)):
            if (rows[i][0]*rows[k][1]-rows[i][1]*rows[k][0])%P: return 2
    return 1
sols=[]
for s in itertools.product(['a','b','ab'],repeat=3):
    Zb=[i for i in range(3) if 'b' in s[i]]; Za=[i for i in range(3) if 'a' in s[i]]
    if rank2([A[i] for i in Zb])==2: continue           # beta=0 forced -> no line
    if len(Za)==3: continue                              # n.Q=delta !=0 but n.0... alpha=0 for all lanes: Q=(0,0,0): n.x=delta impossible
    # alpha conditions on (U0,V0): need consistency (at most 2 independent equations; with 2 lanes always solvable since minor nonzero)
    sols.append(''.join(s))
res['assignments_with_line']=sols
# keep only minimal (the three canonical): each has exactly one lane in Zb and the other two in Za only
canon=[s for s in sols if sum('b' in x for x in s)==1 and sum(x=='a' for x in s)==2]
res['canonical_assignments']=canon
res['extra_assignments_beyond_canonical']=[s for s in sols if s not in canon]
# scale invariance + base translation
j=0
a,b,U0,V0,dd,base_=setup(MDS,round_opts(0,{}),j)
INV5=pow(5,-1,P-1)
F=get_F(j)
lam=random.randrange(2,P)
ok=0
for tau in (7,99991,1234567891):
    nk=(pow((U0+a*lam*tau)%P,INV5,P)-RC[0][0])%P; rho=(pow((V0+b*lam*tau)%P,INV5,P)-RC[0][1])%P
    ok+= hash_reduced(nk,rho,1)==int(F(pow(lam*tau,5,P)))
res['scale_lambda_gives_same_family']=(ok,3)
t0=random.randrange(1,P)
# translated base point: x_i = d_i (tau+t0) for i != j -> S(x)= d_i^5 (tau+t0)^5 : coefficients of tau^1..tau^4 nonzero
from math import comb
res['translated_base_tau_coeffs_nonzero']=[(comb(5,k)*pow(t0,5-k,P))%P!=0 for k in range(1,5)]
# generic dimension: number of free parameters of the 1-parameter family: lines in plane = 2 (point) + 1 (direction) ; affine-in-W lines: 3 discrete (j)
# delta-check also on j in a few different variants? done above.
json.dump(res,open('line.json','w'),indent=1,default=str)
print(json.dumps(res,indent=1))
