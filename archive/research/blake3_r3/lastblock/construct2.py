import numpy as np, json
exec(open("construct.py").read().split("def solve")[0])
rng=np.random.default_rng(2026)
n=1<<25
def sample(j):
    a=rng.integers(0,1<<32,n,dtype=np.uint64).astype(np.uint32)
    b=rng.integers(0,1<<32,n,dtype=np.uint64).astype(np.uint32)
    A,B=col(j,a,b); return a,b,A,B
c0=sample(0);c1=sample(1);c2=sample(2);c3=sample(3)
def join(keys_left, keys_right):
    """pairs (i,k) with keys_left[i]==keys_right[k]"""
    o=np.argsort(keys_right,kind="stable"); sr=keys_right[o]
    lo=np.searchsorted(sr,keys_left,'left'); hi=np.searchsorted(sr,keys_left,'right')
    idx=np.nonzero(hi>lo)[0]
    L=[];R=[]
    for i in idx:
        for t in range(lo[i],hi[i]): L.append(i);R.append(o[t])
    return np.array(L,dtype=np.int64),np.array(R,dtype=np.int64)
neg=lambda x:(np.uint32(0)-x).astype(np.uint32)
# G5: A1+B2=0 ; G6: A2+B3=0 ; G7: A3+B0=0
i1,i2=join(c1[2],neg(c2[3]))
print("col1-col2 pairs",len(i1))
A2=c2[2][i2]
j,i3=join(A2,neg(c3[3]))
print("triples",len(j))
i1,i2=i1[j],i2[j]
A3=c3[2][i3]
j,i0=join(A3,neg(c0[3]))
print("chains",len(j))
for t in range(min(3,len(j))):
    k1,k2,k3,k0=i1[j[t]],i2[j[t]],i3[j[t]],i0[t]
    h=[0]*8
    h[0],h[4]=int(c0[0][k0]),int(c0[1][k0]);h[1],h[5]=int(c1[0][k1]),int(c1[1][k1])
    h[2],h[6]=int(c2[0][k2]),int(c2[1][k2]);h[3],h[7]=int(c3[0][k3]),int(c3[1][k3])
    print(json.dumps(h))
    json.dump(h,open("h_tuned.json","w"))
