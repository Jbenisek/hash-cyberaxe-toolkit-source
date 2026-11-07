import random
M=0xffffffff
IV=[0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19]
P=[2,6,3,10,7,0,4,13,1,11,12,5,9,14,15,8]
def ror(x,n): return ((x>>n)|(x<<(32-n)))&M
def rol(x,n): return ror(x,32-n)
def G(v,a,b,c,d,x,y):
    v[a]=(v[a]+v[b]+x)&M; v[d]=ror(v[d]^v[a],16)
    v[c]=(v[c]+v[d])&M; v[b]=ror(v[b]^v[c],12)
    v[a]=(v[a]+v[b]+y)&M; v[d]=ror(v[d]^v[a],8)
    v[c]=(v[c]+v[d])&M; v[b]=ror(v[b]^v[c],7)
CALLS=[(0,4,8,12),(1,5,9,13),(2,6,10,14),(3,7,11,15),(0,5,10,15),(1,6,11,12),(2,7,8,13),(3,4,9,14)]
def comp(w,t,n,flags=3,rounds=2,trace=False):
    v=IV[:8]+IV[:4]+[t&M,t>>32,n,flags]
    s=list(w); tr=[]
    for r in range(rounds):
        for i,(a,b,c,d) in enumerate(CALLS):
            G(v,a,b,c,d,s[2*i],s[2*i+1])
            if trace: tr.append(list(v))
        s=[s[p] for p in P]
        if trace and r==0: X=list(v)
    o=[v[i]^v[i+8] for i in range(8)]
    return (o,X,v) if trace else o
X3,X7,X11,X15=0x29d4fa98,0xbee3af28,0x44036000,0x40c58500
W4,W13=0x97475638,0x0007c006
Y3,Y11=0x8127c181,0x7af77f38
K2a1=(IV[2]+IV[6]+W4)&M; K2d1=ror(55^K2a1,16); K2c1=(IV[2]+K2d1)&M; K2b1=ror(IV[6]^K2c1,12)
W4p=((((IV[2]+IV[6]+W4)&M)^8)-(IV[2]+IV[6]))&M
FREE=['C0d1','D2a1','D2b1','S11','S4','X9','w6','Y4','t_hi','c1']
def build(f):
    g=dict(f); m=lambda x:x&M
    L={}
    def S(**k): L.update(k)
    C0d1,D2a1,D2b1,S11,S4,X9,w6,Y4,t_hi,c1=[f[k] for k in FREE]
    X2=m(D2a1+D2b1+W13); X8=rol(X7,7)^D2b1
    C0c1=m(X8+C0d1); K3a1=m(IV[3]+IV[7]+w6)
    K3d1=ror(K3a1^3,16); K3c1=m(IV[3]+K3d1)
    S15=m(S11-K3c1); S3=rol(S15,8)^K3d1
    K3b1=ror(IV[7]^K3c1,12); D3a1=m(S3+S4)
    S7=ror(K3b1^S11,7); D3b1=m(X3-D3a1)
    D2c1=rol(D2b1,12)^S7; D3c1=rol(D3b1,12)^S4
    X4=ror(D3b1^X9,7); X13=m(X8-D2c1)
    X14=m(X9-D3c1); C0b1=ror(X4^C0c1,12)
    D2d1=rol(X13,8)^X2; D3d1=rol(X14,8)^X3
    Y8=rol(Y4,7)^C0b1; S13=rol(D2d1,16)^D2a1
    S9=m(D3c1-D3d1); Y12=m(Y8-C0c1)
    K1c1=m(S9-S13); Y0=rol(Y12,8)^C0d1
    K1d1=m(K1c1-IV[1]); C0a1=m(Y0-C0b1-w6)
    K1a1=rol(K1d1,16)^t_hi; w2=m(K1a1-IV[1]-IV[5])
    X0=m(C0a1-X4-w2); S14=rol(D3d1,16)^D3a1
    K1b1=ror(IV[5]^K1c1,12); S10=m(K2c1+S14)
    D0d1=rol(X15,8)^X0; S5=ror(K1b1^S9,7)
    D0c1=m(S10+D0d1); D0b1=ror(S5^D0c1,12)
    X10=m(D0c1+X15); X5=ror(D0b1^X10,7)
    S1=rol(S13,8)^K1d1; w3=m(S1-K1a1-K1b1)
    X12=rol(C0d1,16)^C0a1; D1c1=m(X11-X12)
    D1d1=m(D1c1-S11); S8=m(D2c1-D2d1)
    K0b1=rol(S4,7)^S8; S2=rol(S14,8)^K2d1
    S6=ror(K2b1^S10,7); X1=rol(X12,8)^D1d1
    K0c1=rol(K0b1,12)^IV[4]; D1b1=ror(S6^D1c1,12)
    C1a1=m(X1+X5+w3); S12=m(S8-K0c1)
    w7=m(S3-K3a1-K3b1); X6=ror(D1b1^X11,7)
    C1d1=ror(X13^C1a1,16); D1a1=rol(D1d1,16)^S12
    C1c1=m(X9+C1d1); C2a1=m(X2+X6+w7)
    w10=m(D1a1-S1-S6); C1b1=ror(X5^C1c1,12)
    C2d1=ror(X14^C2a1,16); w12=m(D2a1-S2-S7)
    Y1=m(C1a1+C1b1+w10); C2c1=m(X10+C2d1)
    Y13=ror(C1d1^Y1,8); C2b1=ror(X6^C2c1,12)
    K0d1=m(K0c1-IV[0]); Y9=m(C1c1+Y13)
    S0=rol(S12,8)^K0d1; D0a1=rol(D0d1,16)^S15
    w8=m(D0a1-S0-S5); w5=m(S2-K2a1-K2b1)
    w9=m(X0-D0a1-D0b1); w11=m(X1-D1a1-D1b1)
    E1d1=m(c1-Y11); E1a1=rol(E1d1,16)^Y12
    Y6=m(E1a1-Y1-w12); Y10=rol(Y6,7)^C2b1
    Y14=m(Y10-C2c1)
    Y2=rol(Y14,8)^C2d1
    w0=m(Y2-C2a1-C2b1)
    K0a1=m(IV[0]+IV[4]+w0)
    tlo=rol(K0d1,16)^K0a1
    t=(t_hi<<32)|tlo
    w1=m(S0-K0a1-K0b1)
    w=[w0,w1,w2,w3,W4,w5,w6,w7,w8,w9,w10,w11,w12,W13,0,0]
    return w,t,dict(S9=S9,S13=S13,K1c1=K1c1)
def messages(w,t):
    wb=list(w); wb[4]=W4p; wb[5]=m_=(w[5]+W4-W4p)&M
    return w,wb
def rnd_free(R,tmax=1<<16):
    return dict(C0d1=R.getrandbits(32),D2a1=R.getrandbits(32),D2b1=R.getrandbits(32),S11=R.getrandbits(32),S4=R.getrandbits(32),X9=R.getrandbits(32),w6=R.getrandbits(32),Y4=R.getrandbits(32),t_hi=R.randrange(tmax),c1=R.getrandbits(32))
