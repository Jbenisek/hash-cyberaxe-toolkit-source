from common import *
random.seed(6)
for k in (30,48,64,96,128,192):
    vals=[random.randrange(P) for _ in range(k)]
    idx=[1,k//3,k-2]; co=[5,-7,2]
    vals.append(sum(c*vals[i] for i,c in zip(idx,co))%P)
    t=time.time(); r=lll_relations(vals,W=1<<40)
    planted=[0]*(k+1)
    for i,c in zip(idx,co): planted[i]=c
    planted[k]=-1
    ok=any(v==planted or v==[-x for x in planted] for v in r)
    print(f'k={k+1}: planted 3-term (5,-7,2,-1) norm 2.9^: found-as-basis-vector={ok}, shortest 2^{l2(norm(r[0])):.2f}, time {time.time()-t:.1f}s')
