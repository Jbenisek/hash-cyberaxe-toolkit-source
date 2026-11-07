# ledger arithmetic for class-table alternatives. Inputs are the shipped ledger/memory numbers of a0lean38 (ledger.out of our G02 scan): per-first-block terms.
import math, json
import a0lean38 as L
C=2728; F=35
w7=1497.66; hit=12.041; scal=278.94; cls=128796.72; lanes=1714.3396; r16=0.48729
K0=90
fixed=C+F+scal            # not proportional to K
perK=(w7+hit+cls+lanes+r16)/K0
tot0=fixed+perK*K0
print('per-FB total',tot0, 'per-class',perK)
T0=87.90374
def dT(K,fixed_=fixed,perK_=perK):   # T ~ log2(perFB / K)
    return math.log2((fixed_+perK_*K)/K)-math.log2(tot0/K0)
out={}
# memory per class
planes=sum(15*bin(c[2]).count('1')*32 for c in L.CLASSES)
table=K0*3*32
out['planes_bytes_90']=planes; out['bytes_per_class_planes_avg']=planes/K0
B0=1045792
res=[]
for K in (45,60,80,89,90,91,100,120,150,180,1000,10**9):
    d=dT(K); B=B0+(K-K0)*(planes/K0+96)
    pen=max(0,math.log2(B)-20)
    res.append((K,round(d,5),int(B),round(pen,4),round(d+pen,4)))
out['K_sweep(K,dT,B,penalty,dS)']=res
out['ceiling_K_inf_dT']=dT(10**12)
# no grouping: every one of the 345600 variants tests its own W7 (16.64 ops each, 1497.66/90 per class test), good variants then need >=0 further ops
perw7=w7/K0
V=K0*3840
ng=fixed+V*perw7   # lower bound: ignores all per-variant work after the gate
out['nogroup_perFB_lower']=ng; out['nogroup_dT_lower']=math.log2(ng/tot0)
# gate by classes but bit-slice: each class tested once = shipped
# cost split
out['share_w7_percent']=100*w7/tot0; out['share_classes_percent']=100*cls/tot0
out['cost_per_good_variant_ops']=tot0/(K0*3840*287309824/2**32)
print(json.dumps(out,indent=1))
json.dump(out,open('scan4.json','w'),indent=1)
