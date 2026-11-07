import sys,time,struct,random,math,json
import numpy as np
import a0lean38 as L
M=L.M
sets={}
orig=list(L.VARIANTS)
print('VARIANTS len',len(orig), 'all in G', all(L.in_G(a) for a in orig))
wd=np.fromfile('gprime_minus_G.bin',dtype=np.uint32)
rnd=random.Random(7)
def a_of(w): return (L.W8C-int(w)-L.C4)&M
sets['G_orig']=orig
sets['Gp_minus_G']=[a_of(w) for w in rnd.sample(list(wd),512)]
# non-G' control: random w8 with s0 diff wrong
non=[]
while len(non)<512:
    w=rnd.getrandbits(32)
    if ((L.s0((w+L.D8)&M)-L.s0(w))&M)!=0xfe7f8000: non.append(a_of(w))
sets['nonGp']=non
nrep=int(sys.argv[1]); 
res={}
for name,vs in [(n,sets[n]) for n in sys.argv[2].split(",")]:
    L.VARIANTS=vs
    lgs=[];succs=[];bad=0;t=time.time();vals=[]
    for r in range(nrep):
        rng=L.Shake('g04u04|%s|%d'%(name,r))
        z,pairs,b,succ,lg,alt=L.smc_replicate(rng)
        bad+=b; succs.append(succ); 
        vals.append(0.0 if z is None else 2.0**z)
        lgs.append(None if z is None else z)
    mean=sum(vals)/len(vals)
    res[name]=dict(nrep=nrep,succ=succs,bad=bad,log2_mean=(math.log2(mean) if mean>0 else None),log2_each=lgs,sec=time.time()-t)
    print(name,res[name],flush=True)
json.dump(res,open('scan2_'+sys.argv[2]+'.json','w'),indent=1)
