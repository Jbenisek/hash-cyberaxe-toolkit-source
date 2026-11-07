import random, struct, sys
import b3m, blake3 as ver
from b3m import *
random.seed(99)
def cancel_d(h,t,b,f,words,call,newd):
    a,bb,c,d=CALLS[call]; v=init(h,t,b,f); x,y=words[2*call],words[2*call+1]
    a1=(v[a]+v[bb]+x)&M; d1=ror(v[d]^a1,16); a1p=newd^rol(d1,16); xp=(a1p-v[a]-v[bb])&M; yp=(y+a1-a1p)&M
    w2=list(words); w2[2*call]=xp; w2[2*call+1]=yp; return None,w2
X3,X7,X11,X15=0x29d4fa98,0xbee3af28,0x44036000,0x40c58500; W4=0x97475638; W13=0x0007c006
# (a) Lemma H, round 1 only (independent of h,t,b,flags): same X, w4 differs W4 vs W4'=W4+8 (K+W4 bit3=0), w5 differs by anything
def round1(X,words):
    v=list(X); m=[words[i] for i in PERM]
    for k,(a,b,c,d) in enumerate(CALLS): g(v,a,b,c,d,m[2*k],m[2*k+1])
    return v
agree=[0]*8; N=100000
for _ in range(N):
    X=[random.getrandbits(32) for _ in range(16)]; X[3],X[7],X[11],X[15]=X3,X7,X11,X15
    w=[random.getrandbits(32) for _ in range(16)]; w[4]=W4; w[13]=W13
    w2=list(w); w2[4]=(W4+8)&M; w2[5]=random.getrandbits(32)
    z1=round1(X,w); z2=round1(X,w2)
    for i in range(8): agree[i]+= (z1[i]^z1[i+8])==(z2[i]^z2[i+8])
print('(a) Lemma H round-1 test, %d random X/w: digest words equal counts'%N, agree)
# (b) which K=h2+h6 allow the filed pin (W4 -> W4+8)
good=0; n=1000000
for _ in range(n):
    K=(random.getrandbits(32)+random.getrandbits(32))&M
    good+= (((K+W4)&M)^8)-K & M == (W4+8)&M
print('(b) K=h2+h6 random: W4\'=W4+8 (filed pin works) in %d/%d = %.4f'%(good,n,good/n))
# (c) end to end through organizer verifier: prefix block P then last block A(55 B)/B(63 B), one chunk (flags 10) and last chunk of 2-chunk msg (flags 2, t=1)
def pair(prefix,F=b''):
    P=bytes(random.getrandbits(8) for _ in range(len(prefix)))
    h=IV; t=len(F)//1024
    for off in range(0,len(P),64): h=comp(h,words_of(P[off:off+64]),t,64,1 if off==0 else 0,2)[0]
    K=(h[2]+h[6])&M
    w=[random.getrandbits(32) for _ in range(14)]+[0,0]; w[13]&=0x00ffffff
    # A: 55 bytes ; B: w4',w5' by cancellation of b: 55->63
    f=2 if F else 10
    _,w2=cancel_d(h,t,55,f,w,2,63)
    A=P+struct.pack('<16I',*w)[:55]; B=P+struct.pack('<16I',*w2)[:63]
    ok_honest = struct.pack('<16I',*w2)[55:]==bytes(9)  # bytes 63 and tail zero in B (B is 63 bytes: byte 63 dropped must be zero)
    ok_honestA = struct.pack('<16I',*w)[55:]==bytes(9)
    X1=rounds_states(h,w,t,55,f,1)[0]; X2=rounds_states(h,w2,t,63,f,1)[0]
    return F+A,F+B,X1==X2,(A and True),w2[14]==0 and w2[15]==0 and (w2[13]>>24)==0, ok_honestA
bad=0;tot=0;xs=0;hon=0
for _ in range(300):
    for prefix,F in ((bytes(64),b''),(bytes(192),b''),(bytes(64),bytes(1024))):
        a,b,xeq,_,honest,_=pair(prefix,F)
        tot+=1; xs+=xeq; hon+=honest
        if b3m.hash_(a,2)!=ver.blake3(a,2) or b3m.hash_(b,2)!=ver.blake3(b,2): bad+=1
print('(c) real pairs (P||A55 vs P||B63; P 1 or 3 blocks; one chunk flags 10, or last chunk of 2, t=1 flags 2): n=%d; same X after round 0 in model: %d; B honest-bytes ok (w14=w15=0, top w13 byte 0 follows when A is): %d; model hash != verifier hash: %d'%(tot,xs,hon,bad))
