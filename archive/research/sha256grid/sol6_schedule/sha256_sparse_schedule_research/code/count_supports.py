from pathlib import Path
import json,subprocess,time,collections,csv
p=Path(__file__).parent;R=json.loads((p/'linear_candidates.json').read_text());summ=[];allrows=[]
for r in R:
 d=r['dimension'];N=r['N'];T=r['T'];idx=list(range(16))+T;n=len(idx);name='N'+str(N)+'_T'+'_'.join(map(str,T));cols=list(map(lambda s:int(s,16),r['columns_hex']))
 with (p/(name+'.supportmat')).open('w') as f:
  f.write(f'{d} {n}\n')
  for t in idx:
   f.write(' '.join(f'{sum(((c>>(32*t+b))&1)<<j for j,c in enumerate(cols)):x}'for b in range(32))+'\n')
 t0=time.process_time()
 subprocess.run([str(p/'rank_supports'),str(p/(name+'.supportmat')),str(p/(name+'.ranks'))],check=True)
 ranks=(p/(name+'.ranks')).read_bytes();counts=[1<<(d-r)for r in ranks]
 for j in range(n):
  b=1<<j
  for start in range(0,len(counts),2*b):
   for m in range(start,start+b):counts[m]-=counts[m+b]
 assert all(v>=0 for v in counts)
 assert sum(counts)==1<<d
 hist=collections.Counter();c=0;minwords=999;total=0
 for mask,count in enumerate(counts):
  if not count or mask>>16:continue
  S=[t for j,t in enumerate(idx)if not (mask>>j)&1]
  if not S:continue
  total+=count;c+=1;hist[len(S)]+=count;minwords=min(minwords,len(S))
  allrows.append({'N':N,'late_support':','.join(map(str,T)),'support':','.join(map(str,S)),'support_size':len(S),'exact_count':str(count)})
 summ.append({'N':N,'T':T,'dim':d,'support_count':c,'minimum_word_weight':minwords,'nonzero_exact_tail_vectors':str(total),'word_weight_distribution':dict(hist)})
 print(name,'supports',c,'minwords',minwords,'total',total,'cpu',time.process_time()-t0,flush=True)
(p/'linear_support_summary.json').write_text(json.dumps(summ,indent=2))
with (p/'linear_full_supports.csv').open('w')as f:
 w=csv.DictWriter(f,fieldnames=list(allrows[0]));w.writeheader();w.writerows(allrows)
