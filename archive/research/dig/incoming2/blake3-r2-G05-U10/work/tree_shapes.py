import json,random
from val import *
rng=random.Random(11)
rows=[]
for L in [1,55,63,64,65,127,128,1024,1025,1088,2048,2049,3072,3073,4096,4097,7168,8192,8193]:
    d=bytes(rng.randrange(256) for _ in range(L))
    dg,log=tree2(d,2)
    root=log[-1]; nonroot=len(log)-1
    cc=max(1,(L+1023)//1024)
    rows.append(dict(len=L,chunks=cc,total_compressions=len(log),nonroot=nonroot,root_flags=root[1],root_b=root[2],root_h=root[3],
        kinds={k:sum(1 for x in log if x[0]==k) for k in set(x[0] for x in log)}))
    print(rows[-1])
# classes of root compression
cls={}
for r in rows: cls.setdefault((r['root_flags'],r['root_b'] if r['root_flags']==12 else 'L',r['root_h']),[]).append(r['len'])
print(cls)
json.dump(rows,open('tree_shapes.json','w'),indent=1)
