# exact carry-class counts for a K-call cancellation by XOR difference delta on u=K+w (K=h_a+h_b): Delta=(u^delta)-u = sum_{i in delta} (1-2u_i)2^i
import json,itertools
res={}
def classes(delta):
    bits=[i for i in range(32) if delta>>i&1]
    c={}
    for pat in itertools.product((0,1),repeat=len(bits)):
        D=sum((1-2*p)<<i for p,i in zip(pat,bits))&0xffffffff
        c[D]=c.get(D,0)+1   # each pattern = 2^(32-len(bits)) values of u
    return bits,c
# validate formula on random u
import random
rng=random.Random(8)
for _ in range(100000):
    d=rng.getrandbits(32); u=rng.getrandbits(32)
    bits,c=classes(d&0x7f) if False else (None,None)
    D=((u^d)-u)&0xffffffff; calc=sum((1-2*(u>>i&1))<<i for i in range(32) if d>>i&1)&0xffffffff
    assert D==calc
print('Delta formula exact on 100000 random (u,delta)')
for name,delta in [('length 55^63 = 8',8),('flags 11^12 = 7',7),('flags 11^10 = 1',1),('length 40^64=104',104),('length 55^64 = 119',119)]:
    bits,c=classes(delta); res[name]=dict(delta=delta,popcount=len(bits),distinct_Delta=len(c),u_per_class='2^%d'%(32-len(bits)),Delta_plus8_classes=c.get(8,0),Delta_list=sorted(((k if k<2**31 else k-2**32) for k in c)))
    print(name,res[name])
# AC pair: both K2 (delta_b) and K3 (delta_f) cancelled independently: total classes = product
json.dump(res,open('carries.out.json','w'),indent=1)
