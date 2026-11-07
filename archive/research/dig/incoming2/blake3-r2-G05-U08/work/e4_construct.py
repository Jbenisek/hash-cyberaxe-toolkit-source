# Generalized pin constructor (own transcription of the filed pkgB3V Steps O,M,Y,T with IV[0..7]/flags/t/b replaced by host constants h,t,b,f).
# Checks, at random hosts (h,t,f): (1) forward round 0 reaches the pins X3,X7,X11,X15 with w4=W4,w13=W13,w14=w15=0;
# (2) the pair differing in the host constant that K2 can cancel gives equal digest words 0,2,5,7 (Lemma H) and different 1,3,4,6.
import random, sys
from b3m import *
random.seed(2026)
X3,X7,X11,X15=0x29d4fa98,0xbee3af28,0x44036000,0x40c58500; W4=0x97475638; W13=0x0007c006
def A(*a): return sum(a)&M
def construct(h,t,b,f):
    r=lambda: random.getrandbits(32)
    C0c1,C0d1,D3d1,S15,S9,w5,X2,y=[r() for _ in range(8)]
    tlo,thi=t&M,(t>>32)&M
    # K2 forward
    K2a1=A(h[2],h[6],W4); K2d1=ror(b^K2a1,16); K2c1=A(IV[2],K2d1); K2b1=ror(h[6]^K2c1,12)
    S2=A(K2a1,K2b1,w5); S14=ror(K2d1^S2,8); S10=A(K2c1,S14); S6=ror(K2b1^S10,7)
    # D3 (w14=w15=0)
    D3a1=rol(D3d1,16)^S14; D3c1=A(S9,D3d1); D3b1=(X3-D3a1)&M; S4=rol(D3b1,12)^D3c1
    S3=(D3a1-S4)&M; X14=ror(D3d1^X3,8); X9=A(D3c1,X14); X4=ror(D3b1^X9,7)
    # K3 backwards
    K3d1=rol(S15,8)^S3; K3c1=A(IV[3],K3d1); K3b1=ror(h[7]^K3c1,12); S11=A(K3c1,S15); S7=ror(K3b1^S11,7)
    K3a1=rol(K3d1,16)^f; w6=(K3a1-h[3]-h[7])&M; w7=(S3-K3a1-K3b1)&M
    # C0 third/fourth, D2 backwards
    X8=(C0c1-C0d1)&M; C0b1=ror(X4^C0c1,12); D2b1=rol(X7,7)^X8; D2c1=rol(D2b1,12)^S7; X13=(X8-D2c1)&M
    # step M
    D2a1=(X2-D2b1-W13)&M; D2d1=rol(X13,8)^X2; S13=rol(D2d1,16)^D2a1; S8=(D2c1-D2d1)&M; w12=(D2a1-S2-S7)&M
    K1c1=(S9-S13)&M; K1d1=(K1c1-IV[1])&M; K1a1=rol(K1d1,16)^thi; K1b1=ror(h[5]^K1c1,12)
    S1=rol(S13,8)^K1d1; S5=ror(K1b1^S9,7); w2=(K1a1-h[1]-h[5])&M; w3=(S1-K1a1-K1b1)&M
    K0b1=rol(S4,7)^S8; K0c1=rol(K0b1,12)^h[4]; K0d1=(K0c1-IV[0])&M; K0a1=rol(K0d1,16)^tlo
    S12=(S8-K0c1)&M; S0=rol(S12,8)^K0d1; w0=(K0a1-h[0]-h[4])&M; w1=(S0-K0a1-K0b1)&M
    # step Y
    Y8=rol(y,7)^C0b1; Y12=(Y8-C0c1)&M; Y0=rol(Y12,8)^C0d1; C0a1=(Y0-C0b1-w6)&M; X12=rol(C0d1,16)^C0a1
    D1c1=(X11-X12)&M; D1b1=ror(S6^D1c1,12); X6=ror(D1b1^X11,7); D1d1=(D1c1-S11)&M; X1=rol(X12,8)^D1d1
    # step T
    X0=(C0a1-X4-w2)&M
    D0d1=rol(X15,8)^X0; D0c1=A(S10,D0d1); X10=A(D0c1,X15); D0b1=ror(S5^D0c1,12); X5=ror(D0b1^X10,7)
    D0a1=rol(D0d1,16)^S15; w8=(D0a1-S0-S5)&M; w9=(X0-D0a1-D0b1)&M
    D1a1=rol(D1d1,16)^S12; w10=(D1a1-S1-S6)&M; w11=(X1-D1a1-D1b1)&M
    return [w0,w1,w2,w3,W4,w5,w6,w7,w8,w9,w10,w11,w12,W13,0,0]
def fwd_ok(h,t,b,f,w):
    X=rounds_states(h,w,t,b,f,1)[0]
    return (X[3],X[7],X[11],X[15])==(X3,X7,X11,X15)
def dig(h,w,t,b,f): return comp(h,w,t,b,f,2)[0]
N=3000
pin_ok=0; pairA=[0]*8; pairA_k0=[0]*8; nk0=0; nk1=0; pairB=[0]*8; sameX=0; pin_bad_by_k=[0,0]
for i in range(N):
    h=[random.getrandbits(32) for _ in range(8)]; t=random.getrandbits(40); f=random.choice([0,2,10,3])
    # last-block host, length pair 55/63
    w=construct(h,t,55,f)
    if not fwd_ok(h,t,55,f,w): continue
    pin_ok+=1
    K=(h[2]+h[6])&M; w4p=(((K+W4)&M)^8)-K&M; w5p=(w[5]+W4-w4p)&M
    w2=list(w); w2[4]=w4p; w2[5]=w5p
    d1=dig(h,w,t,55,f); d2=dig(h,w2,t,63,f)
    eq=[d1[j]==d2[j] for j in range(8)]
    kb=0 if w4p==(W4+8)&M else 1
    if kb==0:
        nk0+=1
        for j in range(8): pairA_k0[j]+=eq[j]
    else:
        nk1+=1
        for j in range(8): pairA[j]+=eq[j]
    # mid-block host: b=64 both; pair differs in h2 only: h2' = h2-8, w4' = W4+8, w5 same
    wm=construct(h,t,64,f)
    assert fwd_ok(h,t,64,f,wm)
    hb=list(h); hb[2]=(h[2]-8)&M; wb=list(wm); wb[4]=(W4+8)&M
    Xa=rounds_states(h,wm,t,64,f,1)[0]; Xb=rounds_states(hb,wb,t,64,f,1)[0]
    sameX+= Xa==Xb
    da=dig(h,wm,t,64,f); db=dig(hb,wb,t,64,f)
    for j in range(8): pairB[j]+= da[j]==db[j]
print('hosts built %d/%d (forward pins X3,X7,X11,X15 hit exactly, w4=W4,w13=W13,w14=w15=0), h,t,f random, f in {0,2,10,3}'%(pin_ok,N))
print('LAST-block pair 55 vs 63, K+W4 bit3=0 (%d hosts): digest words equal per index'%nk0, pairA_k0)
print('LAST-block pair 55 vs 63, K+W4 bit3=1 (%d hosts, W4\'=W4-8): digest words equal per index'%nk1, pairA)
print('MID-block pair (b=64 both; h2 differs by -8, w4 by +8): same X after round 0 in %d/%d; digest words equal per index'%(sameX,pin_ok), pairB)
