import random, itertools, json
from b3 import *
random.seed(20261012)
R=lambda: random.getrandbits(32)
def ror_(x,n): return ror(x,n)
def pair(host, alt, m):
    """host=(h,tlo,thi,b,d) ; alt same shape. Build m' so the state after round 0 is identical.
       Requires equal b-row (h4..h7) between host and alt. Returns m' or None."""
    h,tl,th,b,d=host; h2,tl2,th2,b2,d2=alt
    v=init(h,m,tl,th,b,d); v2=init(h2,m,tl2,th2,b2,d2)
    m2=list(m)
    for j,(A,B,C,D) in enumerate(COLS):
        if v[B]!=v2[B] or v[C]!=v2[C]: return None
        a1=(v[A]+v[B]+m[2*j])&M
        a1p=a1^v[D]^v2[D]
        m2[2*j]=(a1p-v2[A]-v2[B])&M
        m2[2*j+1]=(m[2*j+1]+a1-a1p)&M
    return m2
def x0(host,m): return states(*host[:1],m,*host[1:],rounds=1)[-1]
def st(host,m,r): h,tl,th,b,d=host; return states(h,m,tl,th,b,d,r)
# T1: Lemma L over all ordered length pairs, random hosts (non-IV h, random t, random flags)
def T1(hosts_per_pair=20):
    ok=tot=0; ok_state=0
    for b in range(0,65):
        for b2 in range(0,65):
            if b==b2: continue
            for _ in range(hosts_per_pair):
                h=[R() for _ in range(8)]; tl,th=R(),R(); d=random.choice([1,2,3,8,10,11,4,12,0,5])
                m=[R() for _ in range(16)]
                m2=pair((h,tl,th,b,d),(h,tl,th,b2,d),m)
                s1=st((h,tl,th,b,d),m,1)[-1]; s2=st((h,tl,th,b2,d),m2,1)[-1]
                tot+=1; ok+= (s1==s2)
                # words changed
                assert set(i for i in range(16) if m[i]!=m2[i])<= {4,5}
    return ok,tot
# lines table
LINES={'t_lo':0,'t_hi':1,'b':2,'flags':3}  # column index; d-lines
ALINES={'h0':0,'h1':1,'h2':2,'h3':3}
def alt_host(host,lines):
    h,tl,th,b,d=host; h=list(h)
    for L in lines:
        if L=='t_lo': tl^=R()|1
        elif L=='t_hi': th^=R()|1
        elif L=='b': b=(b^R())&0xffffffff or 1
        elif L=='flags': d^=R()|1
        else: h[int(L[1])]=(h[int(L[1])]+R()+1)&M
    return (h,tl,th,b,d)
# which E calls read which words in round 1: E_j reads positions 8+2j,9+2j -> words PI
CREAD=[{PI[2*j],PI[2*j+1]} for j in range(4)]
EREAD=[{PI[8+2*j],PI[9+2*j]} for j in range(4)]
def predict(changed):
    dirtyC=[j for j in range(4) if CREAD[j]&changed]
    dirtyE_direct=[j for j in range(4) if EREAD[j]&changed]
    best=None
    for G_keep,G_name in ((( 0,2),'A'),((1,3),'B')):
        other=(1,3) if G_name=='A' else (0,2)
        if any(e in other for e in dirtyE_direct): continue
        best=(4,G_name); break
    if not dirtyC and not dirtyE_direct: return 0,'-'
    if best is None: best=(8,'AB')
    return best
if __name__=='__main__':
    ok,tot=T1(); print('T1 lemmaL all ordered pairs b!=b2 in 0..64: state-after-round0 identical',ok,'of',tot)
    base=['t_lo','t_hi','b','flags','h0','h1','h2','h3']
    rows=[]
    N=300
    for r in range(1,len(base)+1):
        for sub in itertools.combinations(base,r):
            chg=set(); ok=0
            Ysets=set()
            for _ in range(N):
                host=([R() for _ in range(8)],R(),R(),random.randrange(65),random.choice([1,3,11]))
                alt=alt_host(host,sub)
                m=[R() for _ in range(16)]
                m2=pair(host,alt,m)
                s1=st(host,m,2); s2=st(alt,m2,2)
                assert s1[1]==s2[1], sub
                chg|=set(i for i in range(16) if m[i]!=m2[i])
            k,g=predict(chg)
            rows.append((sub,sorted(chg),k,g))
    json.dump([[list(a),b,c,d] for a,b,c,d in rows],open('lines_table.json','w'))
    from collections import Counter
    print(Counter(r[2] for r in rows))
    for r in rows:
        if len(r[0])<=2 or r[2]==4: print(r)
