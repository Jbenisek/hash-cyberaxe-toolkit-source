#!/usr/bin/env python3
"""Hostile independent verification of pkg8 proof.md. Written from the text only."""
import numpy as np, random, struct, sys

M32 = 0xffffffff
IV = [0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19]
X3c,X7c,X11c,X15c = 0x29d4fa98,0xbee3af28,0x44036000,0x40c58500
W4 = 0x97475638
W13 = 0x0007c006
K = (IV[2]+IV[6]) & M32
W4p = (((K+W4)&M32) ^ 8) - K & M32
DELTA = (W4 - W4p) & M32
ETA = 0x830303cf
Y3c,Y3pc,Y11c,Y11pc = 0x8127c181,0x7edf3e7e,0x7af77f38,0x850000c3

def rotr(x,r): x&=M32; return ((x>>r)|(x<<(32-r)))&M32
def rotl(x,r): x&=M32; return ((x<<r)|(x>>(32-r)))&M32

# ---------- reference 2-round BLAKE3-256, written from Section 1 ----------
SIG=[[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]]
PERM=[2,6,3,10,7,0,4,13,1,11,12,5,9,14,15,8]
s1=[SIG[0][PERM[i]] for i in range(16)]
SIG.append(s1)
def G(v,a,b,c,d,x,y):
    v[a]=(v[a]+v[b]+x)&M32; v[d]=rotr(v[d]^v[a],16)
    v[c]=(v[c]+v[d])&M32;   v[b]=rotr(v[b]^v[c],12)
    v[a]=(v[a]+v[b]+y)&M32; v[d]=rotr(v[d]^v[a],8)
    v[c]=(v[c]+v[d])&M32;   v[b]=rotr(v[b]^v[c],7)
def compress2(w,n,flags=11):
    v=IV[:8]+IV[:4]+[0,0,n,flags]
    states={}
    for r in range(2):
        s=SIG[r]
        G(v,0,4,8,12,w[s[0]],w[s[1]]); G(v,1,5,9,13,w[s[2]],w[s[3]])
        G(v,2,6,10,14,w[s[4]],w[s[5]]); G(v,3,7,11,15,w[s[6]],w[s[7]])
        states['S' if r==0 else 'Y']=v[:]
        G(v,0,5,10,15,w[s[8]],w[s[9]]); G(v,1,6,11,12,w[s[10]],w[s[11]])
        G(v,2,7,8,13,w[s[12]],w[s[13]]); G(v,3,4,9,14,w[s[14]],w[s[15]])
        states['X' if r==0 else 'Z']=v[:]
    o=[(v[i]^v[i+8])&M32 for i in range(8)]+[(v[i+8]^IV[i])&M32 for i in range(8)]
    return o,states
def digest_bytes(msg):
    assert len(msg)<=64
    blk=msg+b'\0'*(64-len(msg))
    w=list(struct.unpack('<16I',blk))
    o,st=compress2(w,len(msg))
    return b''.join(struct.pack('<I',o[i]) for i in range(8)),o,st

# check schedule of Section 1 round 1 against text
assert [s1[i] for i in range(16)]==[2,6,3,10,7,0,4,13,1,11,12,5,9,14,15,8], s1
# text: C0=G(..,w2,w6) C1=(w3,w10) C2=(w7,w0) C3=(w4,w13) E0=(w1,w11) E1=(w12,w5) E2=(w9,w14) E3=(w15,w8)
assert [s1[0],s1[1],s1[2],s1[3],s1[4],s1[5],s1[6],s1[7]]==[2,6,3,10,7,0,4,13]
assert [s1[8],s1[9],s1[10],s1[11],s1[12],s1[13],s1[14],s1[15]]==[1,11,12,5,9,14,15,8]
print("OK round-1 schedule of Section 1 matches the standard permutation")

# ---------- Fact P ----------
def Gfull(A,B,C,D,x,y):
    v=[A,B,C,D]; G(v,0,1,2,3,x,y); return v
r1=Gfull(X3c,X7c,X11c,X15c,W4,W13); r2=Gfull(X3c,X7c,X11c,X15c,W4p,W13)
print("Fact P: W4'=%08x delta=%08x" % (W4p,DELTA))
print("  w4=W4 : a2=%08x b2=%08x c2=%08x d2=%08x"%(r1[0],r1[1],r1[2],r1[3]))
print("  w4=W4': a2=%08x b2=%08x c2=%08x d2=%08x"%(r2[0],r2[1],r2[2],r2[3]))
assert (r1[3],r1[1])==(r2[3],r2[1]), "Fact P d/b equal FAILS"
assert r1[0]==Y3c and r2[0]==Y3pc and r1[2]==Y11c and r2[2]==Y11pc, "Fact P a/c constants mismatch"
assert r1[3]==0xbbfbdffe and r1[1]==0x76f7aefd
print("OK Fact P verified, and the displayed intermediate table:")
for w4v,exp in ((W4,(0x7ffffff8,0x7af83f3a,0xbefb9f3a,0x01200183)),(W4p,(0x80000000,0x8500c0c5,0xc90420c5,0xfed77e78))):
    a1=(X3c+X7c+w4v)&M32; d1=rotr(X15c^a1,16); c1=(X11c+d1)&M32; b1=rotr(X7c^c1,12)
    assert (a1,d1,c1,b1)==exp, (hex(a1),hex(d1),hex(c1),hex(b1))
print("   both rows of 3.2 reproduce exactly")

# ---------- Lemma Q / Q2 ----------
cls=[Y4 for Y4 in range(0)]
cnt=0; cnt2=0
e1mask=0x03cf8303; e1val=0x030c0303; sub=0x07ef8303
for e1 in range(0,1<<32,1<<0) if False else []:
    pass
# count by mask arithmetic + verify the eta condition on a sample
def eta_of(Y4):
    e1=(Y3c+Y4)&M32; return rotr(e1 ^ ((e1+ (Y3pc-Y3c))&M32),16)
nclass=1<<(32-bin(e1mask).count('1')); nsub=1<<(32-bin(sub).count('1'))
print("Lemma Q: mask %08x has %d bits -> class size %d (text 524288)"%(e1mask,bin(e1mask).count('1'),nclass))
print("Lemma Q2: mask %08x has %d bits -> sub-class size %d (text 131072)"%(sub,bin(sub).count('1'),nsub))
assert nclass==524288 and nsub==131072
rng=random.Random(7); bad=0
for _ in range(200000):
    Y4=rng.getrandbits(32); e1=(Y3c+Y4)&M32
    inclass = (e1 & e1mask)==e1val
    if (eta_of(Y4)==ETA) != inclass: bad+=1
assert bad==0, bad
# exhaustive over the 19 free bits: every class member has eta, and only them (by construction)
free=[i for i in range(32) if not (e1mask>>i)&1]
chk=0
for k in range(1<<19):
    e1=e1val
    for j,p in enumerate(free):
        if (k>>j)&1: e1|=1<<p
    Y4=(e1-Y3c)&M32
    if eta_of(Y4)!=ETA: chk+=1
assert chk==0
print("OK Lemma Q exhaustive over all 524288 class members: every one gives eta=830303cf; 200k random words agree with the mask test")
assert (sub|e1mask)==sub and (e1val & 0x04200000)==0
print("OK Lemma Q2: 07ef8303 = 03cf8303 OR 04200000 and 030c0303 has zeros at bits 21,26")
FREE17=[i for i in range(32) if not (sub>>i)&1]
print("   17 free positions:",FREE17)
assert FREE17==[2,3,4,5,6,7,10,11,12,13,14,20,27,28,29,30,31]
assert 14 in FREE17 and 30 in FREE17 and 31 in FREE17
print("OK bits 14,30,31 of e1 are free in the sub-class (Lemma C needs this)")

# ---------- rule A, gate, Lemma A ----------
def ruleA_h1(h1):
    h=[(h1>>i)&1 for i in range(32)]
    return (h[0]==0 and h[1]==1 and h[16]==0 and h[17]==0 and
            (h[2]^h[10])==1 and (h[3]^h[11])==1 and
            (h[3]^h[12]^h[24])==0 and (h[6]^h[13]^h[25])==0)
def gate_h1(h1):
    h=[(h1>>i)&1 for i in range(32)]
    return h[16]==0 and h[17]==0 and h[0]==0 and h[1]==1
# independence / 2^-8 claim: exhaustive over the 10 relevant bits
bits=[0,1,16,17,2,10,3,11,12,24,6,13,25]
tot=0
for v in range(1<<len(bits)):
    h1=0
    for j,b in enumerate(bits):
        if (v>>j)&1: h1|=1<<b
    if ruleA_h1(h1): tot+=1
print("rule A: %d of %d patterns of the 13 read bits pass -> share %s (text 2^-8=%s)"%(tot,1<<len(bits),tot/(1<<len(bits)),1/256))
assert tot/(1<<len(bits))==1/256
g=sum(1 for v in range(1<<len(bits)) for h1 in [sum(1<<b for j,b in enumerate(bits) if (v>>j)&1)] if gate_h1(h1))
print("gate: share %s (text 2^-4=%s)"%(g/(1<<len(bits)),1/16))
assert g/(1<<len(bits))==1/16
assert all((not ruleA_h1(h1)) or gate_h1(h1) for v in range(1<<len(bits)) for h1 in [sum(1<<b for j,b in enumerate(bits) if (v>>j)&1)])
print("OK gate is implied by rule A (6.7 claim), and is exactly 4 of the 8 conditions")

# Lemma A (c)(d) packed test, scalar single lane
def lemmaA_y(Z):
    s=(Z<<12)&0x0003c000; y=Z^s
    s=s<<12; y^=s
    s=(y<<13)&0x40010000; y^=s
    return y
ALL=0x4f010300
def vword(e1):
    e=lambda i:(e1>>i)&1
    v=0
    for pos,val in ((8,0),(9,0),(24,1),(25,0),(26,1),(27,1^e(27)),(16,1^e(27)^e(28)),(30,e(29))):
        if val: v|=1<<pos
    return v
rng=random.Random(11); bad=0; nA=0
for _ in range(400000):
    k=rng.getrandbits(17); e1=sub and e1val
    e1=e1val
    for j,p in enumerate(FREE17):
        if (k>>j)&1: e1|=1<<p
    Y4=(e1-Y3c)&M32
    z=rng.getrandbits(36)   # with guard bits set, as Lemma A (c) allows
    h1=rotr(rotr(z&M32,24)^rotr(e1,16),0)
    h1=(rotr(z&M32,24)^rotr(e1,16))&M32   # Lemma A(a): ROL(h1,24)=z^ROL(e1,8)
    # Lemma A(a) check against the real definition h1=ROR(Y14^e1,16), Y14=ROR(z,8)
    h1_real=rotr(rotr(z&M32,8)^e1,16)
    if h1!=h1_real: bad+=1
    y=lemmaA_y(z); u=(y^vword(e1))&ALL
    passd=(u==ALL)
    s=u+(2**32-ALL)
    if passd!=ruleA_h1(h1_real): bad+=1
    if ((s>>32)&1)!=(1 if passd else 0): bad+=1
    if s>2**32: bad+=1
    if passd: nA+=1
print("Lemma A: %d mismatches in 400000 random (member, 36-bit z); rule-A share %.5f (2^-8=%.5f)"%(bad,nA/400000,1/256))
assert bad==0
print("OK Lemma A (a),(b),(c),(d) verified independently incl. the guard-bit claim")
