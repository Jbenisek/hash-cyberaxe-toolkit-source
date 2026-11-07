"""zero-immediate constructions for the four D0 immediates (v0+v5, v15, v10, v5 after the columns). Own code, closed-form solves."""
import sys, os, json
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
import b3steps as B
from b3steps import *
R=B._ror; rol=lambda x,k:R(x,32-k)
def cols(msg):
    v=list(IV)+list(IV[:4])+[0,0,64,11]
    for j,(a,b,c,d) in enumerate(GC[:4]):
        x,y=msg[2*j],msg[2*j+1]
        v[a]=(v[a]+v[b]+x)&M32; v[d]=R(v[d]^v[a],16); v[c]=(v[c]+v[d])&M32; v[b]=R(v[b]^v[c],12)
        v[a]=(v[a]+v[b]+y)&M32; v[d]=R(v[d]^v[a],8); v[c]=(v[c]+v[d])&M32; v[b]=R(v[b]^v[c],7)
    return v
def pre(j):  # state of call j (a,b,c,d) after q1,q2 with x=0
    a,b,c,d=GC[j]; v=list(IV)+list(IV[:4])+[0,0,64,11]
    A=(v[a]+v[b])&M32; D=R(v[d]^A,16); C=(v[c]+D)&M32; Bv=R(v[b]^C,12)
    return A,Bv,C,D
msg=[0]*8; out={}
# m1 -> v0=0 : v0 = a2 = A+Bv+m1 -> m1 = -(A+Bv)
A,Bv,C,D=pre(0); msg[1]=(-(A+Bv))&M32
# m3 -> v5=0 : b2 = R7(b1 ^ c2), c2 = C + d2, d2 = R8(D ^ a2): b2=0 -> c2=b1 -> d2=b1-C -> a2 = D ^ rol8(d2)
A,Bv,C,D=pre(1); d2=(Bv-C)&M32; a2=D^rol(d2,8); msg[3]=(a2-A-Bv)&M32
# m5 -> v10=0 : c2=0
A,Bv,C,D=pre(2); d2=(-C)&M32; a2=D^rol(d2,8); msg[5]=(a2-A-Bv)&M32
# m7 -> v15=0 : d2=0 -> a2 = D
A,Bv,C,D=pre(3); a2=D; msg[7]=(a2-A-Bv)&M32
v=cols(msg)
out["words"]=["%08x"%x for x in msg]; out["v0_v5_v10_v15"]=["%08x"%v[i] for i in (0,5,10,15)]
def tot(m): return build(consts=m+[0]*8)[1]
res={"all_four_zero":tot(msg)}
for name,idx in (("v0 via m1",1),("v5 via m3",3),("v10 via m5",5),("v15 via m7",7)):
    mm=[0]*8; mm[idx]=msg[idx]; res[name]=tot(mm)
src=build(consts=msg+[0]*8)[0]
res["circuit_correct_all_four"]=B.check(src,3,36,7,range(8,16),consts=msg+[0]*8)
out["totals"]=res
json.dump(out,open(os.path.join(HERE,"scan3_out.json"),"w"),indent=1); print(json.dumps(out))
