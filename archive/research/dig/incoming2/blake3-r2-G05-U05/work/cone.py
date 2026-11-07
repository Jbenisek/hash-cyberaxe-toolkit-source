from model import *
import json
X3,X7,X11,X15,W4,W13=0x29d4fa98,0xbee3af28,0x44036000,0x40c58500,0x97475638,0x0007c006
def pair(X,m):
    m2=list(m); m2[4]=w4p(m[4]); m2[5]=(m[5]+m[4]-m2[4])&M
    r=[]
    for mm in (m,m2):
        v=list(X); round_(v,[mm[i] for i in PERM]); r.append(digest(v))
    return [r[0][k]^r[1][k] for k in range(8)]
random.seed(7)
def base():
    X=[random.getrandbits(32) for _ in range(16)]; X[3],X[7],X[11],X[15]=X3,X7,X11,X15
    m=[random.getrandbits(32) for _ in range(16)]; m[4]=W4; m[13]=W13; m[14]=m[15]=0
    return X,m
T=400; out={}
for kind,name,idx in [('X','X%d'%i,i) for i in range(16)]+[('m','w%d'%i,i) for i in range(16)]:
    stay=[0]*8
    for _ in range(T):
        X,m=base()
        if kind=='X': X[idx]=random.getrandbits(32)
        else: m[idx]=random.getrandbits(32)
        D=pair(X,m)
        for k in range(8): stay[k]+= (D[k]==0)
    out[name]=stay
# sanity: pinned base all zero for 0,2,5,7
print(json.dumps(out))
# which vars break each digest word (stay < T)
for k in range(8):
    print('D%d zero-set broken by:'%k,[n for n,s in out.items() if s[k]<T])
