import numpy as np, json
from fam import *
from cone import KEEP, idx
rng=np.random.default_rng(7)
G=256
L=make_family(G,rng)
# sanity: padding byte 0x86 -> lane16 top byte 0x80 ; check family satisfies Lemma1 lanes zero/allones after theta1
d0=theta(apply_z(L,0)); assert (d0[5]==0).all() and (d0[15]==0).all()

# Lemma1: lane 8 and 23 all-ones after theta? (D3 = all ones) -> lanes 8,23 (x=3) become all-ones
print('lane8,23 allones after theta1:', (d0[8]==U(2**64-1)).all(), (d0[23]==U(2**64-1)).all())
# Lemma 2 affinity of A2 in z
def A2(z): return stages(apply_z(L,z))['A2']
ok=True
for t in range(30):
    a,b,c=[int(rng.integers(0,2**32)) for _ in range(3)]
    ok&=bool((A2(a)^A2(b)^A2(c)^A2(a^b^c)==0).all())
print('A2 affine in z (30 tests x 256 groups):',ok)
# footprint per single z-flip j: changed words (bit positions where any of 256 groups differ)
def wordmask(X,Y):  # (25,G) -> number of (lane,z) positions where any group differs
    diff=np.zeros(25,dtype=np.uint64)
    # bit-slice: position (l,b) differs in any group g: OR over g of (X^Y)[l,g]
    D=X^Y; return np.bitwise_or.reduce(D,axis=1)
def popc(a): return int(sum(bin(int(v)).count('1') for v in a))
res={k:[] for k in ['A2','T3','S3','T4','S4','T5']}
rowsT3=[];rowsS3=[]; rowsT4=[]
for trial in range(24):
    z0=int(rng.integers(0,2**32)); st0=stages(apply_z(L,z0))
    for j in range(32):
        st1=stages(apply_z(L,z0^(1<<j)))
        for k in res: res[k].append(popc(wordmask(st0[k],st1[k])))
        # chi3 rows touched: rows (y,z) of B3 = rhopi(T3)
        B0=rhopi(st0['T3']);B1=rhopi(st1['T3']); dm=wordmask(B0,B1)
        r=0
        for y in range(5):
            m=np.uint64(0)
            for x in range(5): m|=dm[x+5*y]
            r+=bin(int(m)).count('1')
        rowsT3.append(r)
        # round-4 chi rows touched
        B0=rhopi(st0['T4']);B1=rhopi(st1['T4']); dm=wordmask(B0,B1)
        r=0
        for y in range(5):
            m=np.uint64(0)
            for x in range(5): m|=dm[x+5*y]
            r+=bin(int(m)).count('1')
        rowsT4.append(r)
out={k:dict(mean=float(np.mean(v)),min=int(min(v)),max=int(max(v))) for k,v in res.items()}
out['chi3_rows_touched']=dict(mean=float(np.mean(rowsT3)),min=int(min(rowsT3)),max=int(max(rowsT3)))
out['chi4_rows_touched']=dict(mean=float(np.mean(rowsT4)),min=int(min(rowsT4)),max=int(max(rowsT4)))
print(json.dumps(out,indent=1)); json.dump(out,open('footprint.json','w'),indent=1)
