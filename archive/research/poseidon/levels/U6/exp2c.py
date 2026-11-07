from common import *
import itertools
allc=[RC[r][l] for r in range(64) for l in range(3)]
blocks=[allc[12*b:12*b+12] for b in range(16)]
for g,name in ((3,'3 blocks (k=37 with 1)'),(4,'4 blocks (k=49 with 1)')):
    t=time.time();best=None;n=0;hits=[]
    for combo in itertools.combinations(range(16),g):
        vals=[v for b in combo for v in blocks[b]]+[1]
        rel=lll_relations(vals); n+=1
        nm=norm(rel[0])
        if best is None or nm<best[0]: best=(nm,combo)
        if nm<30: hits.append((combo,nm))
    k=12*g+1
    print(f'{name}: {n} LLL runs, shortest relation seen 2^{l2(best[0]):.2f} (generic floor 2^{l2(gh(k)):.2f}), hits with norm<30: {hits}, {time.time()-t:.0f}s')
