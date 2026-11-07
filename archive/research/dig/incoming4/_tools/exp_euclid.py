import random, json, time
from eng import *
random.seed(8)
n=1500
a=PC([random.randrange(P) for _ in range(n+1)]); b=PC([random.randrange(P) for _ in range(n)])
steps=0; qd=[]; mults=0
t=time.time()
while not b.is_zero():
    q,r=divmod(a,b)
    qd.append(q.degree()); steps+=1
    # classical division cost for quotient degree dq on dividend degree da: (dq+1)*(deg b +1) mults + inverse per step
    mults+=(q.degree()+1)*(b.degree()+1)
    a,b=b,r
res=dict(n=n,steps=steps,quotient_deg_counts={str(k):qd.count(k) for k in set(qd)},mults_classical=mults,mults_over_n2=round(mults/n**2,3),sec=round(time.time()-t,1))
N=39062
res['predicted_mults_at_39062']=int(res['mults_over_n2']*N*N)
print(res); json.dump(res,open('euclid.json','w'))
