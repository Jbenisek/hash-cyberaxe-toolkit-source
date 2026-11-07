import json, time, random
from eng import *
random.seed(31337)
t0=time.time()
U0,V0,a,b=[random.randrange(1,P) for _ in range(4)]
Kp=pow((CAPACITY+RC[0][2])%P,5,P)
U=PC([U0,a]); V=PC([V0,b])
st=[(MDS[i][0]*0+0) for i in range(3)]
st=[U*MDS[i][0]+V*MDS[i][1]+(MDS[i][2]*Kp%P) for i in range(3)]   # state after R0 on generic line (in tau)
for idx in [1,2,3,4,60,61,62,63]:
    o=round_opts(idx,{})
    st=[st[i]+RC[idx][i] for i in range(3)]
    st=[p5(st[i]) if o['sb'][i] else st[i] for i in range(3)]
    st=mat_apply(MDS,st)
    print(idx,[f.degree() for f in st],round(time.time()-t0,1),flush=True)
y=st[0]
co=[int(c) for c in y.coeffs()]
nz=[i for i,c in enumerate(co) if c]
res=dict(deg=y.degree(), nnz=len(nz), nonzero_exps_not_mult5=sum(1 for i in nz if i%5), sec=round(time.time()-t0,1))
# validate against reference on a point
tau=123456789
nk=(pow((U0+a*tau)%P,pow(5,-1,P-1),P)-RC[0][0])%P; rho=(pow((V0+b*tau)%P,pow(5,-1,P-1),P)-RC[0][1])%P
res['ref_match']=int(y(tau))==hash_reduced(nk,rho,1)
print(res); json.dump(res,open('generic_line.json','w'))
