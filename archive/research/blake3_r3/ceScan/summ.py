import json,glob
rows=[]
for f in glob.glob("res_*_7.json")+glob.glob("res_k1_1.json"):
    for name,N,out in json.load(open(f)):
        for p,(o,e,z) in out.items(): rows.append((abs(z),z,name,p,o/e))
rows.sort(reverse=True)
print(len(rows),"tests;", len({r[2] for r in rows}),"families")
for r in rows[:14]: print("%.2f %+.2f %-36s %-9s ratio %.3f"%r)
import math
zs=[r[1] for r in rows]; print("mean z %.3f sd %.3f"%(sum(zs)/len(zs),(sum(z*z for z in zs)/len(zs))**.5))
