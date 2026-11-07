"""Exact minimum distance via disjoint information sets; Python standard library."""
import itertools,json,time,pathlib
from functools import reduce
from explore import *
p=pathlib.Path(__file__).parent

def invmat(rows,d):
 rr=list(rows);ii=[1<<j for j in range(d)]
 for j in range(d):
  k=next(k for k in range(j,d)if(rr[k]>>j)&1)
  rr[j],rr[k]=rr[k],rr[j];ii[j],ii[k]=ii[k],ii[j]
  for k in range(d):
   if k!=j and ((rr[k]>>j)&1):rr[k]^=rr[j];ii[k]^=ii[j]
 assert rr==[1<<j for j in range(d)]
 return [sum(((ii[k]>>j)&1)<<k for k in range(d))for j in range(d)]

def choose_sets(rows,d):
 rem=list(enumerate(rows));out=[]
 while rem:
  piv={};new=[];s=[]
  for i,r in rem:
   v=r
   while v:
    j=v.bit_length()-1
    if j in piv:v^=piv[j]
    else:piv[j]=v;s.append(i);break
   if not v:new.append((i,r))
  if len(piv)<d:break
  out.append(s);rem=new
 return out

answers=[]
for N,T,L in [(37,(22,23),4),(37,(22,24),3),(38,(23,24),4)]:
 cpu=time.process_time();wall=time.perf_counter()
 W,d=symbolic(T,N);cols=[sum(apply(w,1<<j)<<(32*t)for t,w in enumerate(W))for j in range(d)]
 rows=[x for w in W for x in w];sets=choose_sets(rows,d)
 best=100000;arg=0;seen=0;goodsets=[]
 for si,inds in enumerate(sets):
  inverses=invmat([rows[i]for i in inds],d)
  c=[]
  for j,x in enumerate(inverses):
   v=reduce(int.__xor__,(cols[i]for i in range(d)if(x>>i)&1),0)
   assert sum(((v>>t)&1)<<k for k,t in enumerate(inds))==1<<j
   c.append(v)
  for l in range(1,L+1):
   for comb in itertools.combinations(range(d),l):
    v=0
    for j in comb:v^=c[j]
    seen+=1
    weight=v.bit_count()
    if weight<best:best=weight;arg=v
  goodsets.append(inds)
  print(N,T,'set',si+1,'best',best,flush=True)
 assert best<=len(sets)*(L+1)
 out={'N':N,'T':T,'dimension':d,'disjoint_information_sets':goodsets,'sets_count':len(sets),'enumerated_max_information_weight':L,'enumerated_candidates_including_repeats':seen,'completeness_threshold':len(sets)*(L+1),'minimum':best,'words':[f'{(arg>>(32*t))&MASK:08x}'for t in range(N)],'cpu_seconds':time.process_time()-cpu,'wall_seconds':time.perf_counter()-wall}
 answers.append(out)
 (p/'linear_min_infosets.json').write_text(json.dumps(answers,indent=2))
 print('DONE',N,T,best,out['cpu_seconds'],flush=True)
