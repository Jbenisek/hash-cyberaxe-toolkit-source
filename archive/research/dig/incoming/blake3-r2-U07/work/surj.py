from b3ctr import *
R=random.Random(99); bad=0; N=20000
for _ in range(N):
    w2t,w3t=R.getrandbits(32),R.getrandbits(32); t_hi=R.randrange(1<<16)
    K1a1=(w2t+IV[1]+IV[5])&M; K1d1=ror(K1a1^t_hi,16); K1c1=(K1d1+IV[1])&M
    K1b1=ror(IV[5]^K1c1,12); S1=(w3t+K1a1+K1b1)&M; S13=ror(S1^K1d1,8); S9=(K1c1+S13)&M
    a,b,w6,S4=[R.getrandbits(32) for _ in range(4)]
    X2=(a+b+W13)&M; X13=ror(rol(S13^a,16)^X2,8); X8=rol(X7,7)^b
    D2c1=(X8-X13)&M; S7=D2c1^rol(b,12)
    K3a1=(IV[3]+IV[7]+w6)&M; K3d1=ror(K3a1^3,16); K3c1=(IV[3]+K3d1)&M; K3b1=ror(IV[7]^K3c1,12)
    S11=rol(S7,7)^K3b1
    S15=(S11-K3c1)&M; S3=rol(S15,8)^K3d1; D3a1=(S3+S4)&M; D3b1=(X3-D3a1)&M; D3c1=rol(D3b1,12)^S4
    D3d1=(D3c1-S9)&M; X14=ror(D3d1^X3,8); X9=(X14+D3c1)&M
    f=dict(C0d1=R.getrandbits(32),D2a1=a,D2b1=b,S11=S11,S4=S4,X9=X9,w6=w6,Y4=R.getrandbits(32),t_hi=t_hi,c1=R.getrandbits(32))
    w,t,_=build(f)
    if (w[2],w[3])!=(w2t,w3t): bad+=1
print("targets",N,"mismatch",bad)
