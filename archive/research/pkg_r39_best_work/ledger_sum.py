import json,glob,math
W=[json.load(open(f))[0] for f in sorted(glob.glob("led/win_*.json"),key=lambda x:int(x.split('_')[-1][:-5]))]
n=len(W);C=sum(w['distinct_claws'] for w in W);G=sum(w['distinct_groups'] for w in W);O=sum(w['ops'] for w in W)
cat={}
for w in W:
  for k,v in w['cat'].items():cat[k]=cat.get(k,0)+v
print("windows",n,"claws",C,"groups",G,"ops",O,"ops/claw %.1f = %.4f compressions"%(O/C,O/C/2812))
for k,v in sorted(cat.items(),key=lambda x:-x[1]):print("  cat %-14s %10.1f per claw  %.2f%%"%(k,v/C,100*v/O))
for k in('hits','matches','raw','opp','same','iters','s2iters','pairs','moves','drops','f9','f8','w17','parks','cuts','s2phases'):
  print("  ev %-8s total %d per claw %.4f"%(k,sum(w.get(k,0) for w in W),sum(w.get(k,0) for w in W)/C))
print("f9/raw %.5f (65/4096=%.5f)  f8/f9 %.4f (9/128=%.4f)"%(sum(w['f9'] for w in W)/sum(w['raw'] for w in W),65/4096,sum(w['f8'] for w in W)/sum(w['f9'] for w in W),9/128))
print("kernel_len %d..%d nreg max %d qmax %d trails max %d min %d kskip %d"%(min(w['kernel_len'] for w in W),max(w['kernel_len'] for w in W),max(w['kernel_nreg'] for w in W),max(w['qmax'] for w in W),max(w['trails'] for w in W),min(w['trails'] for w in W),sum(w.get('kskip',0) for w in W)))
ops=[w['ops'] for w in W];m=sum(ops)/n;sd=math.sqrt(sum((x-m)**2 for x in ops)/(n-1));print("ops mean %.0f sd %.0f max %d min %d"%(m,sd,max(ops),min(ops)))
cl=[w['distinct_claws'] for w in W];gr=[w['distinct_groups'] for w in W]
print("claws mean %.2f range %d..%d; groups mean %.2f range %d..%d; opc range %.1f..%.1f"%(sum(cl)/n,min(cl),max(cl),sum(gr)/n,min(gr),max(gr),min(o/c for o,c in zip(ops,cl)),max(o/c for o,c in zip(ops,cl))))
mx={}
for w in W:
  for k,v in w['blk'].items():mx[k]=max(mx.get(k,0),v)
print("census",len(mx),sum(mx.values()),"per-window",min(sum(w['blk'].values()) for w in W),max(sum(w['blk'].values()) for w in W))
for w in W:print("  W seed %d claws %d groups %d ops %d opc %.1f"%(w['seed'],w['distinct_claws'],w['distinct_groups'],w['ops'],w['ops']/w['distinct_claws']))
