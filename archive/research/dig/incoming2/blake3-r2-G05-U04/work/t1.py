import random, json, collections, struct, sys
from b3 import *
import blake3 as ver
random.seed(20261012)
K2=(IV[2]+IV[6])&M; K3=(IV[3]+IV[7])&M
def cancel(words, col, dv, dv2):
    """return second word list w' so that call col of round 0 leaves identical outputs when v[d] is dv vs dv2"""
    x,y = (4,5) if col==2 else (6,7)
    K = K2 if col==2 else K3
    a1=(K+words[x])&M
    a1p=a1^dv^dv2
    w=list(words); w[x]=(a1p-K)&M; w[y]=(words[y]+words[x]-w[x])&M
    return w
def one(words, specs):
    """specs: list of (col, dv, dv2). base uses dv; primed uses dv2. returns traces and states"""
    w2=list(words)
    for col,dv,dv2 in specs: w2=cancel(w2,col,dv,dv2) if False else w2
    return None
def pair(words, blen, flags, blen2, flags2, cols):
    w1=list(words); w2=list(words)
    for col in cols:
        if col==2: w2=cancel(w2,2,blen,blen2)
        else: w2=cancel(w2,3,flags,flags2)
    t1=[];t2=[]
    v1=run(IV,w1,0,blen,flags,2,t1); v2=run(IV,w2,0,blen2,flags2,2,t2)
    return w1,w2,t1,t2,v1,v2
def stats(name, blen,flags,blen2,flags2,cols,N=3000, wordfn=None):
    act=collections.Counter(); xeq=0; ndiff=collections.Counter(); fields=collections.Counter()
    for _ in range(N):
        w=[random.getrandbits(32) for _ in range(16)]
        w1,w2,t1,t2,v1,v2=pair(w,blen,flags,blen2,flags2,cols)
        # state after round 0 = inputs of round1 call 0..3 (columns) -> compare the 16-word state via round-1 call inputs
        r1a=[t for t in t1 if t[0]==1]; r1b=[t for t in t2 if t[0]==1]
        # state X equal iff first four round1 calls (columns) have equal a,b,c,d
        # (columns 0..3 cover all 16 state words)
        if all(r1a[k][2:6]==r1b[k][2:6] for k in range(4)): xeq+=1
        a=0
        for k in range(8):
            if r1a[k]!=r1b[k]:
                act[k]+=1; a+=1
                for nm,i in zip('abcdxy',range(2,8)):
                    if r1a[k][i]!=r1b[k][i]: fields[(k,nm)]+=1
        ndiff[a]+=1
        dw=sum(1 for p,q in zip(digest(v1),digest(v2)) if p!=q); ndiff[('dig',dw)]+=1
    return dict(name=name,N=N,X_equal=xeq,active_calls_hist={str(k):v for k,v in sorted((k,v) for k,v in ndiff.items() if not isinstance(k,tuple))},
        digest_words_differ_hist={str(k[1]):v for k,v in sorted((k,v) for k,v in ndiff.items() if isinstance(k,tuple))},
        call_active={('C%d'%k if k<4 else 'E%d'%(k-4)):v for k,v in sorted(act.items())},
        fields_differing_in_round1={'%s%d.%s'%('C' if k<4 else 'E',k%4,n):v for (k,n),v in sorted(fields.items())})
out=[]
out.append(stats('len 55 vs 63 (K2 cancel, w4/w5), flags 11 both',55,11,63,11,[2]))
out.append(stats('flags 11 vs 12 (K3 cancel, w6/w7), len 64 both',64,11,64,12,[3]))
out.append(stats('both cancels: len 55/63 + flags 11/12',55,11,63,12,[2,3]))
out.append(stats('control: len 55 vs 63 NO cancel (same words)',55,11,63,11,[]))
# byte level check vs organizer verifier for length pair: messages with w14=w15=0 and w13 top byte 0
bad=0;n=0
for _ in range(300):
    w=[random.getrandbits(32) for _ in range(16)]; w[13]&=0x00FFFFFF; w[14]=0; w[15]=0
    w2=cancel(w,2,55,63)
    m1=struct.pack('<16I',*w)[:55]; m2=struct.pack('<16I',*w2)[:63]
    v1=run(IV,w,0,55,11,2); v2=run(IV,w2,0,63,11,2)
    if ver.blake3(m1,2)!=struct.pack('<8I',*digest(v1)) or ver.blake3(m2,2)!=struct.pack('<8I',*digest(v2)): bad+=1
    n+=1
out.append(dict(name='byte-level check of 55/63 pair vs organizer verifier',n=n,mismatch=bad))
# round-0 state equality for all length pairs b' in 1..64 vs 55 and all flag values f' 0..15 vs 11
eq_len={}
for b2 in range(1,65):
    ok=0
    for _ in range(100):
        w=[random.getrandbits(32) for _ in range(16)]
        w1,w2,t1,t2,v1,v2=pair(w,55,11,b2,11,[2]); r1a=[t for t in t1 if t[0]==1]; r1b=[t for t in t2 if t[0]==1]
        ok+= all(r1a[k][2:6]==r1b[k][2:6] for k in range(4))
    eq_len[b2]=ok
eq_fl={}
for f2 in range(0,16):
    ok=0
    for _ in range(100):
        w=[random.getrandbits(32) for _ in range(16)]
        w1,w2,t1,t2,v1,v2=pair(w,64,11,64,f2,[3]); r1a=[t for t in t1 if t[0]==1]; r1b=[t for t in t2 if t[0]==1]
        ok+= all(r1a[k][2:6]==r1b[k][2:6] for k in range(4))
    eq_fl[f2]=ok
out.append(dict(name='X-equal count of 100 per partner',len_partner_55_vs=eq_len,flag_partner_11_vs=eq_fl))
json.dump(out,open('t1_out.json','w'),indent=1)
print(json.dumps(out,indent=1)[:6000])
