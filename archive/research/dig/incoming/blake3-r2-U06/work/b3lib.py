# own code: BLAKE3 2-round compression + pkgB3U Section 4 root construction (written from proof.md Sections 1-4)
M=0xffffffff
IV=[0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19]
P=(2,6,3,10,7,0,4,13,1,11,12,5,9,14,15,8)
def ror(x,r): return ((x>>r)|(x<<(32-r)))&M
def rol(x,r): return ((x<<r)|(x>>(32-r)))&M
def G(v,a,b,c,d,x,y):
    v[a]=(v[a]+v[b]+x)&M; v[d]=ror(v[d]^v[a],16)
    v[c]=(v[c]+v[d])&M; v[b]=ror(v[b]^v[c],12)
    v[a]=(v[a]+v[b]+y)&M; v[d]=ror(v[d]^v[a],8)
    v[c]=(v[c]+v[d])&M; v[b]=ror(v[b]^v[c],7)
def compress(w,n,tlo=0,thi=0,flags=11):
    """returns dict S,X,Y,Z (state lists) and cv (o[0..7]) for 2 rounds"""
    v=IV[:8]+IV[:4]+[tlo,thi,n,flags]
    st={}
    s=list(w)
    for r in range(2):
        G(v,0,4,8,12,s[0],s[1]); G(v,1,5,9,13,s[2],s[3]); G(v,2,6,10,14,s[4],s[5]); G(v,3,7,11,15,s[6],s[7])
        if r==0: st['S']=v[:]
        G(v,0,5,10,15,s[8],s[9]); G(v,1,6,11,12,s[10],s[11]); G(v,2,7,8,13,s[12],s[13]); G(v,3,4,9,14,s[14],s[15])
        if r==0: st['X']=v[:]; 
        if r==0: s=[s[P[i]] for i in range(16)]
        if r==0: pass
    # Y = state after C0..C3 of round1: recompute separately
    return st,v
def compress_full(w,n,tlo=0,thi=0,flags=11):
    v=IV[:8]+IV[:4]+[tlo,thi,n,flags]
    st={}
    s=list(w)
    for r in range(2):
        G(v,0,4,8,12,s[0],s[1]); G(v,1,5,9,13,s[2],s[3]); G(v,2,6,10,14,s[4],s[5]); G(v,3,7,11,15,s[6],s[7])
        if r==0: st['S']=v[:]
        elif r==1: st['Y']=v[:]
        G(v,0,5,10,15,s[8],s[9]); G(v,1,6,11,12,s[10],s[11]); G(v,2,7,8,13,s[12],s[13]); G(v,3,4,9,14,s[14],s[15])
        if r==0:
            st['X']=v[:]; s=[s[P[i]] for i in range(16)]
    st['Z']=v[:]
    o=[v[i]^v[i+8] for i in range(8)]
    return st,o
X3,X7,X11,X15=0x29d4fa98,0xbee3af28,0x44036000,0x40c58500
W4,W13=0x97475638,0x0007c006
K=(IV[2]+IV[6])&M
W4p=(((K+W4)&M)^8)-K&M
def build(C0c1,C0d1,D3d1,S15,S9,w5,X2,y,full=False):
    """Steps O,M,Y,T,S2. returns dict with names, block A, block B"""
    n={}
    sub=lambda *a:(a[0]-sum(a[1:]))&M
    add=lambda *a:sum(a)&M
    K2a1=add(IV[2],IV[6],W4); K2d1=ror(55^K2a1,16); K2c1=add(IV[2],K2d1); K2b1=ror(IV[6]^K2c1,12)
    S2=add(K2a1,K2b1,w5); S14=ror(K2d1^S2,8); S10=add(K2c1,S14); S6=ror(K2b1^S10,7)
    D3a1=rol(D3d1,16)^S14; D3c1=add(S9,D3d1); D3b1=sub(X3,D3a1); S4=rol(D3b1,12)^D3c1
    S3=sub(D3a1,S4); X14=ror(D3d1^X3,8); X9=add(D3c1,X14); X4=ror(D3b1^X9,7)
    K3d1=rol(S15,8)^S3; K3c1=add(IV[3],K3d1); K3b1=ror(IV[7]^K3c1,12); S11=add(K3c1,S15)
    S7=ror(K3b1^S11,7); K3a1=rol(K3d1,16)^11; w6=sub(K3a1,IV[3],IV[7]); w7=sub(S3,K3a1,K3b1)
    X8=sub(C0c1,C0d1); C0b1=ror(X4^C0c1,12); D2b1=rol(X7,7)^X8; D2c1=rol(D2b1,12)^S7; X13=sub(X8,D2c1)
    D2a1=sub(X2,D2b1,W13); D2d1=rol(X13,8)^X2; S13=rol(D2d1,16)^D2a1; S8=sub(D2c1,D2d1); w12=sub(D2a1,S2,S7)
    K1c1=sub(S9,S13); K1d1=sub(K1c1,IV[1]); K1a1=rol(K1d1,16); K1b1=ror(IV[5]^K1c1,12)
    S1=rol(S13,8)^K1d1; S5=ror(K1b1^S9,7); w2=sub(K1a1,IV[1],IV[5]); w3=sub(S1,K1a1,K1b1)
    K0b1=rol(S4,7)^S8; K0c1=rol(K0b1,12)^IV[4]; K0d1=sub(K0c1,IV[0]); K0a1=rol(K0d1,16)
    S12=sub(S8,K0c1); S0=rol(S12,8)^K0d1; w0=sub(K0a1,IV[0],IV[4]); w1=sub(S0,K0a1,K0b1)
    Y8=rol(y,7)^C0b1; Y12=sub(Y8,C0c1); Y0=rol(Y12,8)^C0d1; C0a1=sub(Y0,C0b1,w6); X12=rol(C0d1,16)^C0a1
    D1c1=sub(X11,X12); D1b1=ror(S6^D1c1,12); X6=ror(D1b1^X11,7); D1d1=sub(D1c1,S11); X1=rol(X12,8)^D1d1
    X0=sub(C0a1,X4,w2); D0d1=rol(X15,8)^X0; D0c1=add(S10,D0d1); X10=add(D0c1,X15)
    D0b1=ror(S5^D0c1,12); X5=ror(D0b1^X10,7); D0a1=rol(D0d1,16)^S15
    w8=sub(D0a1,S0,S5); w9=sub(X0,D0a1,D0b1)
    D1a1=rol(D1d1,16)^S12; w10=sub(D1a1,S1,S6); w11=sub(X1,D1a1,D1b1)
    A=[w0,w1,w2,w3,W4,w5,w6,w7,w8,w9,w10,w11,w12,W13,0,0]
    w5p=(w5+W4-W4p)&M
    B=A[:]; B[4]=W4p; B[5]=w5p
    return dict(A=A,B=B,S4=S4,S8=S8,S12=S12,S0=S0,K0d1=K0d1,K0b1=K0b1,K0c1=K0c1,S3=S3,S9=S9,X2=X2)
def rnd(rng): return rng.getrandbits(32)
