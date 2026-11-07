import sys,json; sys.path.insert(0,'.')
import b3core as B
from collections import Counter,defaultdict
prog,out=B.build(3)
by=defaultdict(Counter); masks=defaultdict(list)
for i,o in enumerate(prog):
    by[o['tag']][o['kind']]+=1
res={}
for t,c in sorted(by.items(),key=str):
    res[str(t)]=dict(c); 
# round-2 table with internal mask indices
for i,o in enumerate(prog):
    if o['tag'] and o['tag'][0]==2 and o['kind']=='and' and o['imm']==B.REP*B.M32: masks[o['tag']].append(i)
tab={}
for j in range(8):
    for q in range(1,5):
        c=by[(2,j,q)]; tab['R2%s%d.q%d'%('C' if j<4 else 'D',j%4,q)]=dict(total=sum(c.values()),kinds=dict(c),internal_masks=masks.get((2,j,q),[]))
print(json.dumps(tab,indent=0)[:3000]); print('final',dict(by[('final',)]),'masks',[i for i,o in enumerate(prog) if o['tag']==('final',) and o['kind']=='and'])
print('round totals',[sum(sum(by[(r,j,q)].values()) for j in range(8) for q in range(1,5)) for r in range(3)])
json.dump(dict(table=tab,final=dict(by[('final',)])),open('q1_counts.json','w'))
