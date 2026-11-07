import random
from ref import *
random.seed(5)
Y7=0x76f7aefd;Y15=0xbbfbdffe
X3,X7,X11,X15=0x29d4fa98,0xbee3af28,0x44036000,0x40c58500
W4,W13=0x97475638,0x0007c006
N=100000
def inst(w13=W13,x7=X7,x15=X15):
    # X: post round0 state, free except pins; mp round-1 order via w
    X=[random.getrandbits(32) for _ in range(16)]
    X[3],X[7],X[11],X[15]=X3,x7,X11,x15
    w=[random.getrandbits(32) for _ in range(16)]; w[15]=0
    w[4]=W4; w[13]=w13
    wb=list(w); wb[4]=(W4+8)&M; wb[5]=(w[5]-8)&M
    ZA=round1(X,mp_from_w(w))[1]; ZB=round1(X,mp_from_w(wb))[1]
    return fold(ZA),fold(ZB)
def run(label,**kw):
    eq=[0]*8; allpinned=0; tot=[0]*8
    for _ in range(N):
        a,b=inst(**kw)
        e=[a[i]==b[i] for i in range(8)]
        for i in range(8): eq[i]+=e[i]
    print(label,"digest word equal counts of",N,":",eq)
run("pins")
run("w13 relaxed (random)",w13=random.getrandbits(32)) if False else None
# relaxation: break pins on X7 / X15 one at a time by re-randomising, per-sample
def run2(label,relax):
    eq=[0]*8
    for _ in range(N):
        kw={}
        if relax=="X7": kw['x7']=random.getrandbits(32)
        if relax=="X15": kw['x15']=random.getrandbits(32)
        if relax=="w13": kw['w13']=random.getrandbits(32)
        a,b=inst(**kw)
        for i in range(8): eq[i]+=(a[i]==b[i])
    print(label,eq)
for r in ("X7","X15","w13"): run2("relax "+r,r)
