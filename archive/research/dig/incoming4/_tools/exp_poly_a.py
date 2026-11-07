import json
from polylib import *
random.seed(4242)
res={}
for j in range(3):
    t=time.time(); F=get_F(j)
    d=F.degree(); lc=int(F[d])
    # lc tracker: leading coeff of lane polys through rounds, independent of flint products
    a,b,U0,V0,dd,base=setup(MDS,round_opts(0,{}),j)
    lcs=[1 if False else 0]*3
    # after R1: state = M * (c_j^5 const, d_i^5 W ...) top coefficient (deg 1 in W)
    top=[ (0 if i==j else pow(dd[i],5,P)) for i in range(3)]
    lanes=[sum(MDS[r][k]*top[k] for k in range(3))%P for r in range(3)]
    for idx in [2,3,4,60,61,62,63]:
        o=round_opts(idx,{})
        if idx==4:
            w=pow(lanes[0],5,P); lanes=[MDS[r][0]*w%P for r in range(3)]
        else:
            lanes=[pow(x,5,P) for x in lanes]
            lanes=[sum(MDS[r][k]*lanes[k] for k in range(3))%P for r in range(3)]
    lc_pred=lanes[0]
    # note: partial round: non-sboxed lanes keep lower degree; tracker only valid on top-degree part; compare
    res[j]=dict(deg=d, lc=hex(lc), lc_tracker_matches=(lc==lc_pred), sec=round(time.time()-t,1))
    print(j,res[j],flush=True)
json.dump(res,open('poly_a1.json','w'),indent=1)
