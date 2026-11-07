import sys, math
sys.path.insert(0,'b7/pkg/blake3/experiments')
import bsrho as b
from math import log2
st=b.step256()
ph,filt,body,code,_=b.machine_constants(st,b.REGISTERS)
base=code+b.REGFILE+b.COUNTERS+b.ADVICE
print("code",code,"base",base)
res=[]
for tmax in [int(x) for x in sys.argv[1:]]:
    b.MEM_LIMIT=base+b.SPARE+b.ENTRY*tmax
    p=b.plan(256)
    if p is None: print(tmax,"none"); continue
    lg=b.ledger(p,st); t=log2(lg["total"]/b.UNIT)
    mem=base+b.ENTRY*p["tmax"]
    print(tmax,p["tmax"],"Tp",p["Tp"],"B",p["B"],"time",round(t,5),"mem",mem,"memterm",round(log2(mem/2**20),5),"score",round(t+log2(mem/2**20),5),"P",round(b.loss(p)["P_lower"],5),flush=True)
