import numpy as np, sys, json
sys.path.insert(0,'.')
from kk6 import *
ONES=np.uint64(2**64-1)
def A2of(L): return theta(rnd(L,0))
def O2Pof(A2): 
    B=chi(rhopi(A2)); B[0]^=M64(RC[1]); return theta(B)
def run(drop=None,N=1024,seed=7,verbose=True):
    rng=np.random.default_rng(seed)
    L0=leader_state(rng,N,drop=drop)
    res={}
    A20=A2of(L0); O0=O2Pof(A20)
    # affinity in z: second difference for random z pairs
    bad=0;tot=0
    for t in range(20):
        za=int(rng.integers(0,2**32)); zb=int(rng.integers(0,2**32))
        def f(z):
            L=L0.copy(); L[4]^=np.uint64(z); L[14]^=np.uint64(z); return A2of(L)
        d=f(za^zb)^f(za)^f(zb)^f(0)
        bad+= int(d.any()); tot+=1
    res['affine_fail_pairs']=f"{bad}/{tot}"
    sup_sizes=[];uniform=[];rows_touched=[];two_in_row=[];o2p_union=[];o2p_mean=[];dout_union=[]
    for j in range(32):
        L=L0.copy(); L[4]^=np.uint64(1<<j); L[14]^=np.uint64(1<<j)
        A2=A2of(L); dA=A2^A20
        nz=dA.any(axis=1)  # lane x plane? need per word: word=(lane,plane)
        # words: (lane, bit) positions where any slice differs
        words=[(l,b) for l in range(25) for b in range(64) if ((dA[l]>>np.uint64(b))&np.uint64(1)).any()]
        # slice-uniform: for a bit position, all slices differ (all ones) or none
        uni=all(((dA[l]>>np.uint64(b))&np.uint64(1)).all() for (l,b) in words)
        sup_sizes.append(len(words)); uniform.append(uni)
        # chi2 input diff rows
        din=rhopi(dA)
        rows={}
        for Y in range(5):
            for p in range(64):
                mask=0
                for X in range(5):
                    if ((din[X+5*Y]>>np.uint64(p))&np.uint64(1)).any(): mask|=1<<X
                if mask: rows[(Y,p)]=mask
        rows_touched.append(len(rows)); two_in_row.append(sum(1 for m in rows.values() if bin(m).count('1')>1))
        O=O2Pof(A2); dO=O^O0
        wu=sum(int(((dO[l]>>np.uint64(b))&np.uint64(1)).any()) for l in range(25) for b in range(64))
        wm=np.mean([sum(bin(int(dO[l][s])).count('1') for l in range(25)) for s in range(0,N,16)])
        o2p_union.append(wu); o2p_mean.append(float(wm))
        # dout before theta3: chi2 output diff words
        B1=chi(rhopi(A2)); B0=chi(rhopi(A20)); dd=B1^B0
        dout_union.append(sum(int(((dd[l]>>np.uint64(b))&np.uint64(1)).any()) for l in range(25) for b in range(64)))
        if j==0 and verbose: print(" j=0 A2 diff words:",sorted(words))
    res.update(support_words=sorted(set(sup_sizes)),uniform_allones_all_j=all(uniform),rows_touched=sorted(set(rows_touched)),
        rows_with_2plus_inputs=sorted(set(two_in_row)),o2p_changed_words_union_over_slices=dict(min=min(o2p_union),mean=float(np.mean(o2p_union)),max=max(o2p_union)),
        o2p_changed_words_mean_per_slice=dict(min=min(o2p_mean),mean=float(np.mean(o2p_mean)),max=max(o2p_mean)),
        chi2_out_changed_words_union=dict(min=min(dout_union),mean=float(np.mean(dout_union)),max=max(dout_union)))
    return res
if __name__=="__main__":
    r=run(None,N=1024)
    print(json.dumps(r,indent=1))
    json.dump(r,open('t1_q1_chi2_out.json','w'),indent=1)
