import numpy as np, json, time
from fam import *
from cone import KEEP, idx
import cone
rng=np.random.default_rng(11)
OUT={}
c=json.load(open('cone.json'))
# ---- structural footprint (data independent): A2 support -> chi2 rows -> theta3
def bitsof(arr):  # (25,) uint64 -> set of idx
    return {64*l+b for l in range(25) for b in range(64) if (int(arr[l])>>b)&1}
G=256; L=make_family(G,rng)
a0=stages(apply_z(L,0))['A2']; a1=stages(apply_z(L,1<<5))['A2']
supp=bitsof(np.bitwise_or.reduce(a0^a1,axis=1))
Bs=set()   # chi2 input bits (after rhopi) touched
for x in range(5):
    for y in range(5):
        Bl=y+5*((2*x+3*y)%5); r=RHO[x+5*y]
        for z in range(64):
            if 64*(x+5*y)+z in supp: Bs.add(64*Bl+(z+r)%64)
rows2={(i//64//5,i%64) for i in Bs}
outs2={idx(x,y,z) for (y,z) in rows2 for x in range(5)}
th3=cone.theta_dep(set())  # placeholder
fwd=set()
for i in outs2:   # forward theta: bit (x,y,z) of S flips columns (x,z) and (x+1,z+1)
    l,z=divmod(i,64); x=l%5
    fwd.add(i)
    for y in range(5):
        fwd.add(idx((x+1)%5,y,z)); fwd.add(idx((x-1)%5,y,z+1))
rows3_struct={(i//64//5,i%64) for i in fwd}  # note: before rhopi; recompute properly below
B3s=set()
for x in range(5):
    for y in range(5):
        Bl=y+5*((2*x+3*y)%5); r=RHO[x+5*y]
        for z in range(64):
            if 64*(x+5*y)+z in fwd: B3s.add(64*Bl+(z+r)%64)
rows3_struct={(i//64//5,i%64) for i in B3s}
OUT['structural']=dict(A2_support_words=len(supp),chi2_rows_touched=len(rows2),theta3_out_words_structural=len(fwd),chi3_rows_touched_structural=len(rows3_struct))
print(OUT['structural'])
# ---- sensitivity (necessity) tests
M=64
Ls=make_family(M,rng); st=stages(apply_z(Ls,int(rng.integers(0,2**32))))
keymask=np.zeros(25,dtype=np.uint64)
for z in KEEP:
    for x in range(4): keymask[x]|=U(1<<z)
def key_of(S6): return S6[:4]&keymask[:4,None]
def run_from_S3(S3): return key_of(perm(S3,3,6))
def run_from_S4(S4): return key_of(perm(S4,4,6))
def run_from_T4(T4):  # theta3.. input to round-4 chi: rest of round 4 (rhopi,chi,iota) then rounds 5,6
    A=chi(rhopi(T4)); A[0]^=U(RC[3]); return key_of(perm(A,4,6))
def run_from_T5(T5):
    A=chi(rhopi(T5)); A[0]^=U(RC[4]); return key_of(perm(A,5,6))
def sens(base, fn):
    ref=fn(base); res=np.zeros(1600,int)
    for i in range(1600):
        l,b=divmod(i,64); X=base.copy(); X[l]^=U(1<<b)
        res[i]=int(np.any(fn(X)!=ref,axis=0).sum())
    return res
t=time.time()
tests={'S3 (chi3 outputs, round3.chi... =input of theta4)':( st['S3'],run_from_S3),
       'T4 (theta4-applied words = chi4 inputs)':( st['T4'],run_from_T4),
       'S4 (chi4 outputs)':( st['S4'],run_from_S4),
       'T5 (theta5-applied words = chi5 inputs, stored by round 4)':( st['T5'],run_from_T5)}
sensres={}
for name,(b,f) in tests.items():
    r=sens(b,f); sensres[name]=r
    OUT['sens '+name]=dict(bits_with_any_effect=int((r>0).sum()),min_hits_among_effect=int(r[r>0].min()) if (r>0).any() else 0,of=1600,samples=M)
    print(name,OUT['sens '+name],round(time.time()-t))
# compare to structural cones
T5need=set(c['5']['_Sprev'] and [])  # placeholder
Bexact=cone.rhopi_inv(cone.chi_dep_bits(set(c['5']['_S'])))   # theta5-applied words (pre-rhopi coords) needed = 1363
sT5=sensres['T5 (theta5-applied words = chi5 inputs, stored by round 4)']
pred=np.zeros(1600,bool); pred[list(Bexact)]=True
OUT['T5_sens_vs_cone']=dict(cone_size=int(pred.sum()),sens_set=int((sT5>0).sum()),agree=bool(((sT5>0)==pred).all()),sens_not_in_cone=int(((sT5>0)&~pred).sum()),cone_not_sens=int((~(sT5>0)&pred).sum()))
print(OUT['T5_sens_vs_cone'])
unneeded=[i for i in range(1600) if not pred[i]]
lanes={}
for i in unneeded: lanes[i//64]=lanes.get(i//64,0)+1
OUT['T5_unneeded_words_by_lane']=lanes; OUT['T5_unneeded_words']=len(unneeded)
# ---- freedom: distinct values of cell outputs across z within one group
N=1<<18; chunk=1<<16
g1=make_family(1,rng); 
S3s=[];K=[];W5=[]
msk5=np.zeros((25,),dtype=np.uint64)
for i in sorted(Bexact): msk5[i//64]|=U(1<<(i%64))
for s in range(0,N,chunk):
    zs=rng.integers(0,2**32,chunk,dtype=np.uint64)
    A=np.repeat(g1,chunk,axis=1); A[4]^=zs; A[14]^=zs
    d=stages(A)
    S3s.append(np.ascontiguousarray(d['S3'].T)); W5.append(np.ascontiguousarray((d['T5']&msk5[:,None]).T)); K.append(np.ascontiguousarray((d['S6'][:4]&keymask[:4,None]).T))
    zlist=zs if s==0 else np.concatenate([zlist,zs])
def ndist(L):
    a=np.concatenate(L); v=a.view(np.dtype((np.void,a.dtype.itemsize*a.shape[1])))
    return len(np.unique(v))
nz=len(np.unique(zlist))
OUT['freedom']=dict(samples=N,distinct_z=nz,distinct_S3=ndist(S3s),distinct_T5_cone1363=ndist(W5),distinct_key140=ndist(K))
print(OUT['freedom'])
json.dump(OUT,open('q_results.json','w'),indent=1,default=int)
