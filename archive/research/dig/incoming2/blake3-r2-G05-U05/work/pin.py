from model import *
X3,X7,X11,X15,W4,W13=0x29d4fa98,0xbee3af28,0x44036000,0x40c58500,0x97475638,0x0007c006
def c3(w4):
    v=[0]*16; v[3],v[7],v[11],v[15]=X3,X7,X11,X15; g(v,3,7,11,15,w4,W13); return v[3],v[7],v[11],v[15]
A=c3(W4);B=c3(w4p(W4)); print([hex(x) for x in A],[hex(x) for x in B])
# round-1 model with random rest; verify digest words 0,2,5,7 equal
random.seed(1); bad=0; N=20000
for _ in range(N):
    X=[random.getrandbits(32) for _ in range(16)]; X[3],X[7],X[11],X[15]=X3,X7,X11,X15
    m=[random.getrandbits(32) for _ in range(16)]; m[4]=W4; m[13]=W13; m[14]=m[15]=0
    m2=list(m); m2[4]=w4p(W4); m2[5]=(m[5]+W4-m2[4])&M
    r=[]
    for mm in (m,m2):
        v=list(X); mp=[mm[i] for i in PERM]; round_(v,mp); r.append(digest(v))
    if any(r[0][k]!=r[1][k] for k in (0,2,5,7)): bad+=1
print('pinned digest words 0,2,5,7 mismatches',bad,'/',N)
