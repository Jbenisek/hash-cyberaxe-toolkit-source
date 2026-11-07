from explore import *
from functools import reduce
import pathlib
base=pathlib.Path(__file__).parent
allout=[]
for N in (37,38,39,40):
 surv=sweep(N)
 for T,d,es in surv:
  W,n=symbolic(T,N);B=basis([r for t in range(32,N) if t not in T for r in W[t]],n)
  cols=[sum(apply(w,x)<<(32*t) for t,w in enumerate(W)) for x in B]
  best=(10000,0)
  for l in range(1,5):
   for inds in itertools.combinations(range(d),l):
    v=reduce(int.__xor__,(cols[i] for i in inds))
    if any(not ((v>>(32*t))&MASK) for t in T):continue
    hw=v.bit_count()
    if hw<best[0]:best=hw,v
  print('CAND',N,T,d,best[0],flush=True)
  record={'N':N,'T':T,'dimension':d,'upper_weight':best[0],'words':[f'{(best[1]>>(32*t))&MASK:08x}' for t in range(N)],'columns_hex':[hex(c) for c in cols]}
  allout.append(record)
(base/'linear_candidates.json').write_text(json.dumps(allout,indent=2))
