# tailnum.py DIR QDECL : every tail number the template text quotes, from the pair's 14 public-seed runs (out_01..14.json)
import json, math, sys
D=sys.argv[1]; QD=float(sys.argv[2]); NCH,NB,LF=20,80,2048; n=14
rows=[]
for i in range(1,15):
    d=json.load(open("%s/out_%02d.json"%(D,i)))["trials"]; o0=d[0]["observations"]
    hs=sum(t["observations"]["hits"] for t in d[1:NCH+1]); cls=[sum(t["observations"]["c%s"%c] for t in d[1:NCH+1]) for c in ("00","01","10","11")]
    rows.append((o0["log2_carrier"],hs,cls,o0["calib_c18"]))
qlin=[(2.0**r[0])*(r[1]/float(NCH*NB*LF)) for r in rows]; qlog=[math.log2(q) for q in qlin]
m=sum(qlin)/n; sd=math.sqrt(sum((q-m)**2 for q in qlin)/(n-1))
ml=sum(qlog)/n; sdl=math.sqrt(sum((x-ml)**2 for x in qlog)/(n-1))
q01=[(2.0**r[0])*(4.0*r[2][1]/float(NCH*NB*LF)) for r in rows]; m01=sum(q01)/n; sd01=math.sqrt(sum((q-m01)**2 for q in q01)/(n-1))
cl=[sum(r[2][k] for r in rows) for k in range(4)]; H=sum(cl); e=H/4; chi=sum((c-e)**2/e for c in cl)
lq01=[math.log2(q) for q in q01]; ml01=sum(lq01)/n; sdl01=math.sqrt(sum((x-ml01)**2 for x in lq01)/(n-1))
t=(m-2**QD)/(sd/math.sqrt(n))
print("hits",H,"classes",cl,"chi %.2f"%chi,"c18",set(r[3] for r in rows),"per-run hits %d..%d"%(min(r[1] for r in rows),max(r[1] for r in rows)))
print("mean_lin %.4f lcb99 %.4f lcb_log %.4f lcb999 %.4f par01_99 %.4f"%(math.log2(m),math.log2(m-2.650308*sd/math.sqrt(n)),ml-2.650308*sdl/math.sqrt(n),math.log2(m-3.852*sd/math.sqrt(n)),math.log2(m01-2.650308*sd01/math.sqrt(n))))
print("class01 mean_lin %.4f sd_log2 %.4f | sd_log2 %.4f | t_decl %.4f | margin999 %.4f | per-run log2 %.3f..%.3f"%(math.log2(m01),sdl01,sdl,t,math.log2(m-3.852*sd/math.sqrt(n))-QD,min(qlog),max(qlog)))
