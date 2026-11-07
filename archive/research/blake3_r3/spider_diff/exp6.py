from exp1 import *
def rotl(x,n): return (x<<M(n))|(x>>M(32-n))
def Ginv(v,a,b,c,d,mx,my):
    v[b]=rotl(v[b],7)^v[c]; v[c]=v[c]-v[d]; v[d]=rotl(v[d],8)^v[a]; v[a]=v[a]-v[b]-my
    v[b]=rotl(v[b],12)^v[c]; v[c]=v[c]-v[d]; v[d]=rotl(v[d],16)^v[a]; v[a]=v[a]-v[b]-mx
def rinv(v,m):
    Ginv(v,0,5,10,15,m[8],m[9]);Ginv(v,1,6,11,12,m[10],m[11]);Ginv(v,2,7,8,13,m[12],m[13]);Ginv(v,3,4,9,14,m[14],m[15])
    Ginv(v,0,4,8,12,m[0],m[1]);Ginv(v,1,5,9,13,m[2],m[3]);Ginv(v,2,6,10,14,m[4],m[5]);Ginv(v,3,7,11,15,m[6],m[7])
# sanity: invert round
N=1000
m=[rng.integers(0,2**32,N,dtype=np.uint64).astype(M) for _ in range(16)]
v=init(m,64,11,N);v0=[x.copy() for x in v];rnd(v,m);rinv(v,m);assert all((a==b).all() for a,b in zip(v,v0))
# last round (round index 2) message
mm=m
for _ in range(2): mm=perm(mm)
# pre-round-3 diff HW when post-round-3 diff is (x,x) low weight
N=1<<14
mm=[rng.integers(0,2**32,N,dtype=np.uint64).astype(M) for _ in range(16)]
res={}
for i in range(8):
  for b in (0,31):
    A=[rng.integers(0,2**32,N,dtype=np.uint64).astype(M) for _ in range(16)]
    B=[x.copy() for x in A]
    B[i]^=M(1<<b);B[i+8]^=M(1<<b)
    rinv(A,mm);rinv(B,mm)
    h=sum(pop(A[j]^B[j]) for j in range(16))
    act=sum((A[j]!=B[j]).astype(int) for j in range(16))
    res[(i,b)]=(h.mean(),h.min(),act.mean(),act.min())
print("backward through last round from digest-collision shaped diff (x,x) (x single bit): meanHW minHW meanActive minActive")
for k,v_ in sorted(res.items(),key=lambda t:t[1][0])[:5]: print(k,v_)
