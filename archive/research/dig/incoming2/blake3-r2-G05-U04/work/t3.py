import numpy as np, json, collections, time
t=time.time(); out={}
for delta in (8,7,15):
    cnt=collections.Counter()
    for c in range(64):
        a=(np.arange(c<<26,(c+1)<<26,dtype=np.uint64)).astype(np.uint32)
        D=((a^np.uint32(delta)).astype(np.int64)-a.astype(np.int64))
        u,n=np.unique(D,return_counts=True)
        for k,v in zip(u.tolist(),n.tolist()): cnt[k]+=v
    out[str(delta)]={str(k):v for k,v in sorted(cnt.items())}
    print(delta,'distinct D:',len(cnt),'(2^popcount =',2**bin(delta).count('1'),') each count',set(cnt.values()),time.time()-t)
json.dump(out,open('t3_out.json','w'),indent=1)
