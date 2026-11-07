import random,json
from tree_pairs import *
rng=random.Random(77)
cases=[(55,11,63,11),(55,11,64,12),(64,11,64,12),(55,11,63,10),(55,11,55,10),(40,11,64,12)]
out={}
for bA,fA,bB,fB in cases:
    ok=0
    for _ in range(5000):
        w,w2,c=pair(IV,IV,bA,fA,bB,fB,rng)
        vA=list(IV)+IV[:4]+[0,0,bA,fA]; vB=list(IV)+IV[:4]+[0,0,bB,fB]
        sA=run(IV,w,0,bA,fA,1)[0]; sB=run(IV,w2,0,bB,fB,1)[0]
        ok+= sA==sB
    out['%d/%d vs %d/%d'%(bA,fA,bB,fB)]=ok; print(bA,fA,bB,fB,ok,'/5000')
json.dump(out,open('xcheck.out.json','w'))
