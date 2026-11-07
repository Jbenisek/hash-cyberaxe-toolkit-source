import json, math
NCH,NB,LF,NP,L18,NB18=20,80,2048,800,512,8
rows=[];lines=[]
for i in range(1,15):
    d=json.load(open("tail/out_%02d.json"%i))["trials"]
    o0=d[0]["observations"]; ks=[o0["k%d"%t] for t in range(18,24)]; l2=o0["log2_carrier"]
    hs=sum(t["observations"]["hits"] for t in d[1:NCH+1]); ver=sum(t["observations"]["verified"] for t in d[1:NCH+1])
    cls=[sum(t["observations"]["c%s"%c] for t in d[1:NCH+1]) for c in ("00","01","10","11")]
    assert hs==ver==sum(cls) and o0["kat"]==1 and o0["mask_viol"]==0
    rows.append((ks,l2,hs,cls,o0["calib_c18"]))
    lines.append("%s|%.6f|%d|%s"%(",".join(map(str,ks)),l2,hs,",".join(map(str,cls))))
n=14
qlin=[(2.0**r[1])*(r[2]/float(NCH*NB*LF)) for r in rows]; qlog=[math.log2(q) for q in qlin]
m=sum(qlin)/n; sd=math.sqrt(sum((q-m)**2 for q in qlin)/(n-1))
lcb99=math.log2(m-2.650308*sd/math.sqrt(n)); lcb999=math.log2(m-3.852*sd/math.sqrt(n))
ml=sum(qlog)/n; lcblog=ml-2.650308*math.sqrt(sum((x-ml)**2 for x in qlog)/(n-1))/math.sqrt(n)
q01=[(2.0**r[1])*(4.0*r[3][1]/float(NCH*NB*LF)) for r in rows]; m01=sum(q01)/n; sd01=math.sqrt(sum((q-m01)**2 for q in q01)/(n-1))
par99=math.log2(m01-2.650308*sd01/math.sqrt(n))
qdecl=math.floor((lcb999-0.01)*100)/100
print("c18",set(r[4] for r in rows),"hits",sum(r[2] for r in rows),"classes",[sum(r[3][k] for r in rows) for k in range(4)])
print("mean_lin %.4f  lcb99 %.4f  lcb999 %.4f  lcb_log %.4f  parity01_99 %.4f  -> QDECL %.2f"%(math.log2(m),lcb99,lcb999,lcblog,par99,qdecl))
print("stage18 frac", sum(r[0][0] for r in rows)/(n*NP*L18*8), "vs c18/65536", rows[0][4]/65536)
open("tail/EXP_S.txt","w").write("\n".join(lines)+"\n")
