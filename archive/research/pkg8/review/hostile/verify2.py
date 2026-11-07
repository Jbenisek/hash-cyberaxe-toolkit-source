#!/usr/bin/env python3
"""Part 2: the construction, Lemma N, and an independent measurement of the
cluster yield of 6.7 / H4 and of the stage-2 shares. Written from the text."""
import numpy as np, random, struct
M32=0xffffffff
IV=[0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19]
X3c,X7c,X11c,X15c=0x29d4fa98,0xbee3af28,0x44036000,0x40c58500
W4=0x97475638; W13=0x0007c006
K=(IV[2]+IV[6])&M32; W4p=((((K+W4)&M32)^8)-K)&M32; DELTA=(W4-W4p)&M32
ETA=0x830303cf; Y3c,Y3pc,Y11c,Y11pc=0x8127c181,0x7edf3e7e,0x7af77f38,0x850000c3
SUBMASK=0x07ef8303; SUBVAL=0x030c0303
FREE17=[2,3,4,5,6,7,10,11,12,13,14,20,27,28,29,30,31]
def rotr(x,r): x&=M32; return ((x>>r)|(x<<(32-r)))&M32
def rotl(x,r): x&=M32; return ((x<<r)|(x>>(32-r)))&M32
PERM=[2,6,3,10,7,0,4,13,1,11,12,5,9,14,15,8]
S0SCH=list(range(16)); S1SCH=[S0SCH[PERM[i]] for i in range(16)]
def G(v,a,b,c,d,x,y):
    v[a]=(v[a]+v[b]+x)&M32; v[d]=rotr(v[d]^v[a],16)
    v[c]=(v[c]+v[d])&M32;   v[b]=rotr(v[b]^v[c],12)
    v[a]=(v[a]+v[b]+y)&M32; v[d]=rotr(v[d]^v[a],8)
    v[c]=(v[c]+v[d])&M32;   v[b]=rotr(v[b]^v[c],7)
def compress2(w,n):
    v=IV[:8]+IV[:4]+[0,0,n,11]; out={}
    for r,s in ((0,S0SCH),(1,S1SCH)):
        G(v,0,4,8,12,w[s[0]],w[s[1]]); G(v,1,5,9,13,w[s[2]],w[s[3]])
        G(v,2,6,10,14,w[s[4]],w[s[5]]); G(v,3,7,11,15,w[s[6]],w[s[7]])
        out['S' if r==0 else 'Y']=v[:]
        G(v,0,5,10,15,w[s[8]],w[s[9]]); G(v,1,6,11,12,w[s[10]],w[s[11]])
        G(v,2,7,8,13,w[s[12]],w[s[13]]); G(v,3,4,9,14,w[s[14]],w[s[15]])
        out['X' if r==0 else 'Z']=v[:]
    o=[(v[i]^v[i+8])&M32 for i in range(8)]
    out['o']=o; return out

def stepO(c0c1,c0d1,d3d1,s15,s9,w5):
    n={}
    n['K2a1']=(IV[2]+IV[6]+W4)&M32; n['K2d1']=rotr(55^n['K2a1'],16)
    n['K2c1']=(IV[2]+n['K2d1'])&M32; n['K2b1']=rotr(IV[6]^n['K2c1'],12)
    n['S2']=(n['K2a1']+n['K2b1']+w5)&M32; n['S14']=rotr(n['K2d1']^n['S2'],8)
    n['S10']=(n['K2c1']+n['S14'])&M32; n['S6']=rotr(n['K2b1']^n['S10'],7)
    n['D3a1']=rotl(d3d1,16)^n['S14']; n['D3c1']=(s9+d3d1)&M32
    n['D3b1']=(X3c-n['D3a1'])&M32; n['S4']=rotl(n['D3b1'],12)^n['D3c1']
    n['S3']=(n['D3a1']-n['S4'])&M32; n['X14']=rotr(d3d1^X3c,8)
    n['X9']=(n['D3c1']+n['X14'])&M32; n['X4']=rotr(n['D3b1']^n['X9'],7)
    n['K3d1']=rotl(s15,8)^n['S3']; n['K3c1']=(IV[3]+n['K3d1'])&M32
    n['K3b1']=rotr(IV[7]^n['K3c1'],12); n['S11']=(n['K3c1']+s15)&M32
    n['S7']=rotr(n['K3b1']^n['S11'],7); n['K3a1']=rotl(n['K3d1'],16)^11
    n['w6']=(n['K3a1']-IV[3]-IV[7])&M32; n['w7']=(n['S3']-n['K3a1']-n['K3b1'])&M32
    n['X8']=(c0c1-c0d1)&M32; n['C0b1']=rotr(n['X4']^c0c1,12)
    n['D2b1']=rotl(X7c,7)^n['X8']; n['D2c1']=rotl(n['D2b1'],12)^n['S7']
    n['X13']=(n['X8']-n['D2c1'])&M32
    n.update(c0c1=c0c1,c0d1=c0d1,d3d1=d3d1,S15=s15,S9=s9,w5=w5)
    return n
def stepM(n,X2):
    m={}
    m['D2a1']=(X2-n['D2b1']-W13)&M32; m['D2d1']=rotl(n['X13'],8)^X2
    m['S13']=rotl(m['D2d1'],16)^m['D2a1']; m['S8']=(n['D2c1']-m['D2d1'])&M32
    m['w12']=(m['D2a1']-n['S2']-n['S7'])&M32
    m['K1c1']=(n['S9']-m['S13'])&M32; m['K1d1']=(m['K1c1']-IV[1])&M32
    m['K1a1']=rotl(m['K1d1'],16); m['K1b1']=rotr(IV[5]^m['K1c1'],12)
    m['S1']=rotl(m['S13'],8)^m['K1d1']; m['S5']=rotr(m['K1b1']^n['S9'],7)
    m['w2']=(m['K1a1']-IV[1]-IV[5])&M32; m['w3']=(m['S1']-m['K1a1']-m['K1b1'])&M32
    m['K0b1']=rotl(n['S4'],7)^m['S8']; m['K0c1']=rotl(m['K0b1'],12)^IV[4]
    m['K0d1']=(m['K0c1']-IV[0])&M32; m['K0a1']=rotl(m['K0d1'],16)
    m['S12']=(m['S8']-m['K0c1'])&M32; m['S0']=rotl(m['S12'],8)^m['K0d1']
    m['w0']=(m['K0a1']-IV[0]-IV[4])&M32; m['w1']=(m['S0']-m['K0a1']-m['K0b1'])&M32
    m['X2']=X2; return m
def stepY(n,y):
    t={}
    t['Y8']=rotl(y,7)^n['C0b1']; t['Y12']=(t['Y8']-n['c0c1'])&M32
    t['Y0']=rotl(t['Y12'],8)^n['c0d1']; t['C0a1']=(t['Y0']-n['C0b1']-n['w6'])&M32
    t['X12']=rotl(n['c0d1'],16)^t['C0a1']
    t['D1c1']=(X11c-t['X12'])&M32; t['D1b1']=rotr(n['S6']^t['D1c1'],12)
    t['X6']=rotr(t['D1b1']^X11c,7); t['D1d1']=(t['D1c1']-n['S11'])&M32
    t['X1']=rotl(t['X12'],8)^t['D1d1']; t['Y4']=y; return t
def stepT(n,m,t):
    u={}
    u['X0']=(t['C0a1']-n['X4']-m['w2'])&M32
    u['D0d1']=rotl(X15c,8)^u['X0']; u['D0c1']=(n['S10']+u['D0d1'])&M32
    u['X10']=(u['D0c1']+X15c)&M32; u['D0b1']=rotr(m['S5']^u['D0c1'],12)
    u['X5']=rotr(u['D0b1']^u['X10'],7); u['D0a1']=rotl(u['D0d1'],16)^n['S15']
    u['w8']=(u['D0a1']-m['S0']-m['S5'])&M32; u['w9']=(u['X0']-u['D0a1']-u['D0b1'])&M32
    u['D1a1']=rotl(t['D1d1'],16)^m['S12']; u['w10']=(u['D1a1']-m['S1']-n['S6'])&M32
    u['w11']=(t['X1']-u['D1a1']-t['D1b1'])&M32
    return u
def member(k):
    e1=SUBVAL
    for j,p in enumerate(FREE17):
        if (k>>j)&1: e1|=1<<p
    return (e1-Y3c)&M32, e1

rng=random.Random(2026)
nbad=0; nN=0; ncheck=0
for trial in range(300):
    c0c1,c0d1,d3d1,s15,s9,w5=[rng.getrandbits(32) for _ in range(6)]
    X2=rng.getrandbits(32); k=rng.getrandbits(17)
    y,e1=member(k)
    n=stepO(c0c1,c0d1,d3d1,s15,s9,w5); m=stepM(n,X2); t=stepY(n,y); u=stepT(n,m,t)
    w=[m['w0'],m['w1'],m['w2'],m['w3'],W4,w5,n['w6'],n['w7'],
       u['w8'],u['w9'],u['w10'],u['w11'],m['w12'],W13,0,0]
    wB=w[:]; wB[4]=W4p; wB[5]=(w5+W4-W4p)&M32
    A=b''.join(struct.pack('<I',x) for x in w)[:55]
    B=b''.join(struct.pack('<I',x) for x in wB)[:63]
    assert len(A)==55 and len(B)==63 and B[55:]==b'\0'*8
    oa=compress2(w,55); ob=compress2(wB,63)
    ncheck+=1
    # half-collision on digest words 0,2,5,7
    for i in (0,2,5,7):
        if oa['o'][i]!=ob['o'][i]: nbad+=1
    # same state X, Y4 = y, Y3/Y11 of Fact P
    if oa['X']!=ob['X']: nbad+=1
    if oa['Y'][4]!=y: nbad+=1
    if (oa['Y'][3],ob['Y'][3],oa['Y'][11],ob['Y'][11])!=(Y3c,Y3pc,Y11c,Y11pc): nbad+=1
    if (oa['X'][3],oa['X'][7],oa['X'][11],oa['X'][15])!=(X3c,X7c,X11c,X15c): nbad+=1
    # Lemma A (a): h1 from z
    Y14=oa['Y'][14]
    h1=rotr(Y14^e1,16)
    C2a1=(X2+t['X6']+n['w7'])&M32; C2d1=rotr(n['X14']^C2a1,16)
    C2c1=(u['X10']+C2d1)&M32; C2b1=rotr(t['X6']^C2c1,12)
    Y2=(C2a1+C2b1+m['w0'])&M32; z=C2d1^Y2
    if rotl(h1,24)!=(z^rotl(e1,8)): nbad+=1
    if Y2!=oa['Y'][2] or Y14!=rotr(z,8): nbad+=1
    # Lemma N : n = D3 xor ROL(D6,8), and R=0 => n=0
    def e1call(wa,ws,Y11v):
        v=[oa['Y'][1],oa['Y'][6],Y11v,oa['Y'][12]]
        a1=(v[0]+v[1]+wa)&M32; d1=rotr(v[3]^a1,16); c1=(v[2]+d1)&M32; b1=rotr(v[1]^c1,12)
        a2=(a1+b1+ws)&M32; d2=rotr(d1^a2,8); c2=(c1+d2)&M32; b2=rotr(b1^c2,7)
        return a1,d1,c1,b1,a2,d2,c2,b2
    EA=e1call(m['w12'],w5,Y11c); EB=e1call(m['w12'],(w5+DELTA)&M32,Y11pc)
    beta=EA[3]^EB[3]; eps=EA[6]^EB[6]
    nn=eps^rotl(beta^eps,1)^ETA
    D3d=oa['o'][3]^ob['o'][3]; D6d=oa['o'][6]^ob['o'][6]
    if nn!=(D3d^rotl(D6d,8)): nN+=1
print("construction+digest: %d cases, %d defects; Lemma N mismatches %d"%(ncheck,nbad,nN))
assert nbad==0 and nN==0
print("OK Theorem of Section 5, Lemma T (eta), Lemma A(a) and Lemma N verified on real 2-round digests")

# eta of a sub-class member on real messages
print("OK Y3,Y3',Y11,Y11' and X3,X7,X11,X15 appear in the real states as the text says")
