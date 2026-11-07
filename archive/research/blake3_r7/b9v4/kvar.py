import sys, importlib
sys.dont_write_bytecode=True
sys.path.insert(0,'pkg/blake3/experiments')
import bsrho as b
from math import log2
for K in (0,1,2):
    b.KPRE=K; b.LOOPS=7-K; b._STEP256.clear(); b._B.clear()
    try:
        st=b.step256()
    except Exception as e:
        print(K,"err",e); continue
    ph,filt,body,code,tmax=b.machine_constants(st)
    p=b.plan(256); lg=b.ledger(p); ls=b.loss(p)
    print("K",K,"ops",st.ops,"instr",st.instr,"regs",st.regs,"tmax",tmax,"Tp",p["Tp"],"time_log2 %.5f"%log2(lg["total"]/b.UNIT),"P %.5f"%ls["P_lower"])
