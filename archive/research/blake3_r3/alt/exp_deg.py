import json, time
from b3h import *
rng=np.random.default_rng(77)
t=time.time()
def cube_sum_zero_bits(rounds,word_bits,nbase,full=True):
    """word_bits: list of (word, bit) cube variables. returns number of the 256 digest bits whose cube sum is 0 for ALL bases"""
    d=len(word_bits); n=1<<d
    alive=np.ones(256,dtype=bool)
    idx=np.arange(n,dtype=np.uint64)
    for b in range(nbase):
        base=rand_words(rng,1,range(8,16))
        m=np.repeat(base,n,axis=1)
        for j,(w,bit) in enumerate(word_bits):
            m[w]=(m[w]&~U(1<<bit))|(((idx>>np.uint64(j))&np.uint64(1)).astype(np.uint32)<<U(bit))
        dg=compress(m,rounds=rounds)            # (8,n)
        x=np.bitwise_xor.reduce(dg,axis=1)      # (8,)
        nz=np.array([(int(x[i])>>b2)&1 for i in range(8) for b2 in range(32)],dtype=bool)
        alive&=~nz
    return int(alive.sum())
def cube(word,d,place):
    if place=="low": bits=list(range(d))
    elif place=="top": bits=list(range(32-d,32))
    else: bits=list(range(0,32,32//d))[:d]   # spread
    return [(word,b) for b in bits]
out={}
# Q1: word 8, low bits, d=1..16, rounds 1..3 (+7 control at d=8)
q1={}
for r in (1,2,3):
    q1[r]={d:cube_sum_zero_bits(r,cube(8,d,"low"),8) for d in (1,2,4,8,12,16)}
    print("Q1 rounds",r,"word8 low-bit cube: #digest bits with cube-sum 0 on all 8 bases",q1[r],round(time.time()-t))
q1["ctl7"]=cube_sum_zero_bits(7,cube(8,8,"low"),8); print("control 7 rounds d=8:",q1["ctl7"])
out["Q1"]=q1
# Q2: placement top/spread
q2={}
for place in ("top","spread"):
    q2[place]={r:{d:cube_sum_zero_bits(r,cube(8,d,place),8) for d in (4,8,12,16)} for r in (1,2,3)}
    print("Q2",place,q2[place],round(time.time()-t))
out["Q2"]=q2
# Q3: word choice at d=12, rounds 3 and 2, top vs low
q3={}
for r in (2,3):
    for place in ("low","top"):
        q3[f"r{r}_{place}"]={w:cube_sum_zero_bits(r,cube(w,12,place),4) for w in range(8,16)}
        print("Q3",r,place,q3[f"r{r}_{place}"],round(time.time()-t))
out["Q3"]=q3
# Q4: two-word cube (d/2 low bits in m8 and m9; and in m8 and m10), rounds 3
q4={}
for pair in ((8,9),(8,10),(8,12)):
    wb=[(pair[0],b) for b in range(6)]+[(pair[1],b) for b in range(6)]
    q4[str(pair)]={r:cube_sum_zero_bits(r,wb,6) for r in (1,2,3)}
    print("Q4 two-word cube 12 low bits",pair,q4[str(pair)])
out["Q4"]=q4
json.dump(out,open("exp_deg.json","w"),default=str)
print(round(time.time()-t))
