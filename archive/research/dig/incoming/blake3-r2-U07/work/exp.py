from b3ctr import *
import json, collections
R=random.Random(20261012)
res={}
# static readers of m2,m3
sched=list(range(16)); rd={2:[],3:[]}
names=['K0','K1','K2','K3','D0','D1','D2','D3']
rnames=['C0','C1','C2','C3','E0','E1','E2','E3']
s=list(range(16))
for r in range(2):
    for i in range(8):
        for k in (s[2*i],s[2*i+1]):
            if k in rd: rd[k].append((names if r==0 else rnames)[i]+"/%s"%("first" if k==s[2*i] else "second"))
    s=[s[p] for p in P]
res['readers']=rd
N=3000
dep=collections.defaultdict(lambda:[0,0]) # free word -> [w2 changed, w3 changed] over bit flips
diffA=0; firstdiff=collections.Counter(); xdiffwords=0
samples=[]
for _ in range(N):
    f=rnd_free(R); w,t,_=build(f); wa,wb=messages(w,t)
    samples.append((f,w,t))
    # word diff
    dw=[i for i in range(16) if wa[i]!=wb[i]]
    assert dw==[4,5],dw
    _,Xa,Va=comp(wa,t,55,trace=True)
    oa,Xa,_t=comp(wa,t,55,trace=True),None,None
res['msg_diff_words_A_vs_B']=[4,5]
# per-call first differing call in trace
def traces(w,t,n): 
    v=IV[:8]+IV[:4]+[t&M,t>>32,n,3]; s=list(w); out=[]
    for r in range(2):
        for i,(a,b,c,d) in enumerate(CALLS):
            G(v,a,b,c,d,s[2*i],s[2*i+1]); out.append(list(v))
        s=[s[p] for p in P]
    return out
cnt=collections.Counter(); nd=collections.defaultdict(int)
for f,w,t in samples[:500]:
    wa,wb=messages(w,t)
    ta=traces(wa,t,55); tb=traces(wb,t,63)
    for k in range(16):
        if ta[k]!=tb[k]: cnt[k]+=1
nm=['K0','K1','K2','K3','D0','D1','D2','D3','C0','C1','C2','C3','E0','E1','E2','E3']
res['calls_where_full_state_differs_A_vs_B_of_500']={nm[k]:cnt[k] for k in range(16)}
# dependence of w2,w3 on each free word (flip each bit, same other)
dep={}
for key in FREE:
    nb=32 if key not in('t_hi',) else 16
    c2=c3=tot=0
    for _ in range(40):
        f=rnd_free(R); w,t,_=build(f)
        for b in range(nb):
            g=dict(f); g[key]^=1<<b; w2_,t2,_=build(g)
            tot+=1; c2+= (w2_[2]!=w[2]); c3+=(w2_[3]!=w[3])
    dep[key]=(c2/tot,c3/tot)
res['dependence_fraction_of_single_bit_flips_changing_w2_w3']=dep
# Q2: perturb w2/w3 bit in both messages
q2={}
for idx in (2,3):
    pinkeep=halfcol=0;tot=0
    for f,w,t in samples[:300]:
        for b in range(32):
            wa,wb=messages(w,t)
            wa=list(wa);wb=list(wb); wa[idx]^=1<<b; wb[idx]^=1<<b
            oa,Xa,_=comp(wa,t,55,trace=True); ob,Xb,_=comp(wb,t,63,trace=True)
            tot+=1
            pinkeep+=(Xa[3],Xa[7],Xa[11],Xa[15])==(X3,X7,X11,X15)
            halfcol+=all(oa[i]==ob[i] for i in (0,2,5,7))
    q2['w%d'%idx]=dict(total=tot,pins_kept=pinkeep,half_collision_kept=halfcol)
res['relax_flip_one_bit_both_msgs']=q2
# Q4: difference on w2/w3 in A only (alternative difference) -> state diff words after round0
q4={}
for idx in (2,3):
    best=99;zero=0;rows=[]
    for b in range(32):
        for kind in ('xor','add','sub'):
            tots=[];
            for f,w,t in samples[:60]:
                wa,_=messages(w,t); wa2=list(wa)
                if kind=='xor': wa2[idx]^=1<<b
                elif kind=='add': wa2[idx]=(wa2[idx]+(1<<b))&M
                else: wa2[idx]=(wa2[idx]-(1<<b))&M
                _,X1,_=comp(wa,t,55,trace=True); _,X2,_=comp(wa2,t,55,trace=True)
                tots.append(sum(1 for i in range(16) if X1[i]!=X2[i]))
            mn=min(tots);best=min(best,mn);zero+=(mn==0)
            rows.append((b,kind,min(tots),sum(tots)/len(tots)))
    q4['w%d'%idx]=dict(min_X_words_differing_over_all=best,deltas_with_zero_X_diff=zero,n_deltas=96,
        mean_over_all=sum(r[3] for r in rows)/len(rows))
# reference: the w4/w5 K2 cancel gives 0
res['alt_difference_on_word_only_in_A']=q4
# xor diff 2^k -> additive deltas realizable (carry patterns): count of distinct (x^d)-x over all x for d single bit -> 2 ; for multi-bit d small bits exhaustive
def addpat(d,bits=16):
    return len({(((x^d)-x)&((1<<bits)-1)) for x in range(1<<bits)})
res['carry_patterns_per_xor_diff']={'d=1<<5':addpat(1<<5),'d=0x3':addpat(3),'d=0x15':addpat(0x15),'d=0':addpat(0)}
json.dump(res,open('exp_out.json','w'),indent=1,default=str)
print(json.dumps(res,indent=1,default=str))
