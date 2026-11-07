import json, time
from b3h import *
rng=np.random.default_rng(99)
t=time.time(); out={}
N=1<<11
m=rand_words(rng,N,range(8,16))
s0=init(IV,0,64,11,N)
base=run_rounds(s0,m,3)
# per (message word, state word) dependency after round r: flip every bit of word w (32 flips), fraction of samples where state word changes
dep={r:np.zeros((8,16)) for r in range(3)}
for wi,w in enumerate(range(8,16)):
    for bit in range(32):
        m2=m.copy(); m2[w]^=U(1<<bit)
        fl=run_rounds(s0,m2,3)
        for r in range(3):
            dep[r][wi]+= (fl[r]!=base[r]).mean(axis=1)/32
for r in range(3):
    ch=dep[r]
    print("after round",r+1,"(msg word x state word) pairs with mean change prob 0:",int((ch==0).sum()),"of",ch.size,"; <0.5:",int((ch<0.5).sum()),"; state words reached by m8:",int((ch[0]>0).sum()))
    out[f"dep_r{r+1}"]=dict(zero_pairs=int((ch==0).sum()),lt_half=int((ch<0.5).sum()))
# digest level
dg=compress(m,rounds=3); mn=1.0
for w in range(8,16):
    for bit in range(32):
        m2=m.copy(); m2[w]^=U(1<<bit); mn=min(mn,float((compress(m2,rounds=3)!=dg).mean()))
print("digest level: smallest P(any digest word changes per word) over all 256 bits:",round(mn,4)); out["digest_min_word_change"]=mn
# Q3: conditional neutral bits: condition = top 8 bits of state word w after round 1 equal 0 (p=2^-8)
M=1<<20
mm=rand_words(rng,M,range(8,16)); ss=init(IV,0,64,11,M)
r1=run_rounds(ss,mm,1)[0]
res={}
for w in (0,5,10,15,1,4):
    ok=np.where((r1[w]>>U(24))==0)[0]
    sel=mm[:,ok]; n=sel.shape[1]; ss2=init(IV,0,64,11,n)
    cnt=0; prob=[]
    for ww in range(8,16):
        for bit in range(32):
            m2=sel.copy(); m2[ww]^=U(1<<bit)
            r=run_rounds(ss2,m2,1)[0]
            p=float(((r[w]>>U(24))==0).mean()); prob.append(p)
    prob=np.array(prob); res[w]=dict(n=int(n),neutral_ge_0p9=int((prob>=0.9).sum()),ge_0p5=int((prob>=0.5).sum()),exact_1=int((prob==1).sum()))
    print("Q3 cond top8(state[%d] after round1)=0, n=%d"%(w,n),res[w])
out["Q3"]=res
# Q4: first-use round of each message word (exact table)
PERMm=PERM; order=list(range(16)); first={}
cur=list(range(16))
for r in range(3):
    for pos,wd in enumerate(cur):
        first.setdefault(wd,[]).append((r,pos//2,"col" if pos<8 else "diag"))
    cur=[cur[i] for i in PERMm]
out["Q4_uses"]={str(k):v for k,v in first.items()}
print("Q4 uses of m8..m15 (round, Gindex, half):",{k:first[k] for k in range(8,16)})
json.dump(out,open("exp_neutral.json","w"),default=str)
print(round(time.time()-t))
