import sys,json,random,time; sys.path.insert(0,'.')
import b3core as B
prog,out=B.build(3)
rnd=random.Random(20261012)
# test set: random + adversarial (all-ones words, alternating, single high words)
tests=[]
for _ in range(300): tests.append([rnd.getrandbits(256) for _ in range(7)])
adv=[(1<<256)-1,0,int('FFFFFFFF'*8,16)^int('80000000'*8,16),int('AAAAAAAA'*8,16),int('55555555'*8,16),int('7FFFFFFF'*8,16),int('80000000'*8,16)]
for _ in range(50):
    tests.append([rnd.choice(adv) ^ (rnd.getrandbits(256) if rnd.random()<0.3 else 0) for _ in range(7)])
ref_ok=all(B.check(prog,out,t) for t in tests); print('unmutated passes all',len(tests),'batches:',ref_ok)
res={}
t0=time.time()
for k,o in enumerate(prog):
    passing=[]
    variants=['a0','zero']+(['a1'] if len(o['args'])>1 else [])
    for v in variants:
        ok=True
        for t in tests:
            if not B.check(prog,out,t,(k,v)): ok=False;break
        if ok: passing.append(v)
    res[k]=dict(tag=list(o['tag']),kind=o['kind'],passing=passing)
print('time',time.time()-t0)
bad={k:r for k,r in res.items() if r['passing']}
print('ops with a deletion variant that passes all tests:',len(bad)); 
for k,r in bad.items(): print(k,r)
json.dump(res,open('q2_mutate.json','w'))
