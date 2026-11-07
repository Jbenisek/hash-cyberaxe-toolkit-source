import json, random, time
from polylib import *
random.seed(99)
res={}
j=0
a,b,U0,V0,dd,base=setup(MDS,round_opts(0,{}),j)
xj=(MDS[j][0]*U0+MDS[j][1]*V0+base[j])%P
out=[PC(pow(xj,5,P)) if i==j else PC(pow(dd[i],5,P))*Wp for i in range(3)]
st=mat_apply(MDS,out)
for idx in (2,3):
    st=[st[i]+RC[idx][i] for i in range(3)]
    st=[p5(f) for f in st]
    st=mat_apply(MDS,st)
ell=st[0]; s1=st[1]; s2=st[2]
res['lane0_deg_after_R3']=ell.degree(); res['lane1_deg']=s1.degree(); res['lane2_deg']=s2.degree()
# find W1,W2 distinct with ell(W1)=ell(W2): roots of (ell(W)-ell(W1))/(W-W1)
t=time.time(); pair=None
for _ in range(40):
    W1=random.randrange(P)
    q=(ell-int(ell(W1)))
    q,r=divmod(q,PC([-W1%P,1])); assert r.is_zero()
    res['quotient_degree']=q.degree()
    rts=[int(x) for x,m in q.roots()]
    rts=[x for x in rts if x!=W1]
    if rts: pair=(W1,rts[0]); break
res['tries_to_find_pair']=_+1
W1,W2=pair
# check: P1 S-box input lane 0 equal, and difference after P1 is M(0,d1,d2)
def state3(W):
    return [int(f(W)) for f in (ell,s1,s2)]
A1,A2=state3(W1),state3(W2)
res['lane0_equal_at_interface']=A1[0]==A2[0]
# full digest equal? (expect no)
Fj=get_F(0)
res['digest_equal_for_this_pair']=int(Fj(W1))==int(Fj(W2))
# degree in W2 of E(W2) = Phi(M(w,a2(W2),b2(W2))) with w fixed
w=pow((A1[0]+RC[4][0])%P,5,P)
L=[PC(w), s1+RC[4][1], s2+RC[4][2]]
Lm=mat_apply(MDS,L)
st=Lm
for idx in (60,61,62,63):
    st=[st[i]+RC[idx][i] for i in range(3)]
    st=[p5(f) for f in st]
    st=mat_apply(MDS,st)
res['E_deg_in_W2_for_fixed_W1']=st[0].degree()
# nominal Bezout against the quotient curve (deg 24) and E' (deg 15625-1)
res['bezout_bound']=24*(st[0].degree()-1)
res['filed_odd_part_degree']=39062
res['ratio_bezout_over_filed']=round(res['bezout_bound']/39062,2)
res['W1']=hex(W1); res['W2']=hex(W2)
print(res); json.dump(res,open('lane0.json','w'),indent=1)
# squarefree on j=1,2
sq={}
for jj in (1,2):
    F=get_F(jj); c=random.randrange(P)
    g=odd_part(taylor_shift(F,c))
    sq[jj]=dict(deg=g.degree(),nnz=nnz(g),gcd_deg=g.gcd(g.derivative()).degree())
print(sq); json.dump(sq,open('sqfree_j12.json','w'))
