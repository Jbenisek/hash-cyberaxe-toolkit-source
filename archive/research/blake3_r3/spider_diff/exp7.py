from exp6 import *
import math
# find low-HW pre-round-3 diffs from backward (x,x); then measure forward probability of reaching digest-collision from that diff
N=1<<17
mm=[rng.integers(0,2**32,N,dtype=np.uint64).astype(M) for _ in range(16)]
best=[]
for i in (0,1,2,3):
    A=[rng.integers(0,2**32,N,dtype=np.uint64).astype(M) for _ in range(16)]
    B=[x.copy() for x in A]; B[i]^=M(1<<31);B[i+8]^=M(1<<31)
    rinv(A,mm);rinv(B,mm)
    D=np.stack([A[j]^B[j] for j in range(16)]);h=pop(D).sum(0)
    k=h.argmin();best.append((h[k],D[:,k].copy(),i))
    # most common diff
    key=np.ascontiguousarray(D.T);vv=key.view(np.dtype((np.void,64))).ravel()
    u,idx,cnt=np.unique(vv,return_index=True,return_counts=True)
    print("i",i,"minHW",h[k],"mode count",cnt.max(),"of",N,"mode HW",pop(D[:,idx[cnt.argmax()]]).sum(),flush=True)
    best.append((int(pop(D[:,idx[cnt.argmax()]]).sum()),D[:,idx[cnt.argmax()]].copy(),i))
# forward test: apply mode diff Δ3 to random states, round 3 with message mm, check digest diff zero
for hw,D,i in best[1::2]:
    tot=0;hit=0;eqs=np.zeros(9,dtype=np.int64)
    for _ in range(8):
        A=[rng.integers(0,2**32,N,dtype=np.uint64).astype(M) for _ in range(16)]
        B=[A[j]^D[j] for j in range(16)]
        rnd(A,mm);rnd(B,mm)
        eq=sum(((A[j]^A[j+8])==(B[j]^B[j+8])).astype(np.int64) for j in range(8))
        eqs+=np.bincount(eq,minlength=9);tot+=N
    print("i",i,"HW",hw,"digest-eq-words histogram (0..8) over",tot,eqs.tolist())
