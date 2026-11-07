from common import *
random.seed(2)
t=time.time()
allc=[RC[r][l] for r in range(64) for l in range(3)]
mds=[M[i][j] for i in range(3) for j in range(3)]
for name,vals in (('all192',allc),('all192+MDS9+1+2^65',allc+mds+[1,1<<65])):
    rel=lll_relations(vals); n=norm(rel[0]); k=len(vals)
    print(name,'k',k,'shortest rel norm 2^%.2f GH 2^%.2f ratio %.2f time %.0fs'%(l2(n),l2(gh(k)),n/gh(k),time.time()-t))
# planted detection power at k=192 (relation with coefs up to 2^20)
v=[random.randrange(P) for _ in range(192)]
v.append(sum(random.randrange(-2**20,2**20)*v[i] for i in (3,50,100,150))%P)
r=lll_relations(v); print('planted 4-term coef<=2^20 at k=193: shortest norm 2^%.1f'%l2(norm(r[0])))
v=[random.randrange(P) for _ in range(192)]
v.append(sum(random.randrange(-2**30,2**30)*v[i] for i in (3,50,100,150))%P)
r=lll_relations(v); print('planted 4-term coef<=2^30 at k=193: shortest norm 2^%.1f (GH 2^%.1f)'%(l2(norm(r[0])),l2(gh(193))))
