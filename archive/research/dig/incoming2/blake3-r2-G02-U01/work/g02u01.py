import io, contextlib, itertools, math
from math import log2
with contextlib.redirect_stdout(io.StringIO()):
    import ledger as L
N0=L.N; RC=L.RC; AB=L.A_B+16384; FB=L.F_B+128; EB=L.E_B+2**19
W=32  # bytes per word
def tl(N): # time_log2 rounded up 5 decimals, via float of N/430 (check below)
    return math.ceil(log2(N/430)*1e5-1e-9)/1e5
# known answer
assert tl(N0)==62.43471, tl(N0)
SRCH=6013036259648            # proof.md Section 12 search phase bytes (bound)
OUTP=8796093155510            # output phase bytes (bound)
CODE=137438953472
assert 171*2**30*32+2563914*32+CODE==SRCH
# lookup counts (charged bounds)
LT2=10*AB+31*FB          # T2' lane tests <=9 per opened cluster + representative read, +31 partner tests per straddling surcharge
LT1=EB                   # E lanes (each loads T1 replica)
LG =(7*2340+4)*RC        # gate tests, exact count of full+tail representative batches
LGsh=lambda k:(7-k)*2340*RC+max(0,4-k)*RC  # exact gate shifts if k copies, lanes 0..k-1 own a copy
def S(Nt,mem): return tl(Nt)+max(0,log2(mem)-20)
print("known answer time_log2",tl(N0),"RC",RC)
print("lookups: T2'",LT2,"T1",LT1,"gate",LG,"A",AB,"F",FB)
# objects (words): T2 copies c (c*2^32 per table copy), T1 2^32, gate 2^30, PXF 3*2^32
# one-time build savings (machine units, as charged): direct T2 2^37, extra T2 copies 2^36, repl T2 2^40, T1 2^37, repl T1 2^38, gate 2^34, repl gate 2^36, PXF 2^37
def evaluate(c,kT2,kT1,kG,pxs,est):
    # c: T2 copies 3 or 1 ; k*: copies held (1..7, base counts as one) ; pxs: PXF small (bool)
    words=c*2**32*kT2+2**32*kT1+2**30*kG+(0 if pxs else 3*2**32)
    rest=SRCH-(3*2**32*7+2**32*7+2**30*7+3*2**32)*W  # everything else
    mem=rest+words*W+(512*W if pxs else 0)
    d=0
    f=(lambda k:(7-k)/7) if est else (lambda k:1 if k<7 else 0)
    f=(lambda k:(7-k)/7) if est else (lambda k:(1 if k<7 else 0))
    d+=LT2*f(kT2)+LT1*f(kT1)+LGsh(kG)
    if pxs: d+=AB
    # build savings
    d-= (2**36*(1 if c==1 else 0)*0)  # placeholder, applied below
    sv=0
    if c==1: sv+=2**36 + (2**40*(2/3))*(kT2-1)/6  # extra copies and their replicas not built
    sv+=2**40*(7-kT2)/6*(1 if c==3 else 1/3)       # replica builds not done (6 replicas total)
    sv+=2**38*(7-kT1)/6 + 2**36*(7-kG)/6
    if pxs: sv+=2**37
    d-=sv
    return d,mem
base=evaluate(3,7,7,7,False,True)
print("check hold: d,mem",base,"mem vs SRCH",SRCH)
res=[]
for est in (True,False):
  for c in (3,1):
    for kT2 in range(1,8):
      for kT1 in range(1,8):
        for kG in range(1,8):
          for pxs in (False,True):
            d,mem=evaluate(c,kT2,kT1,kG,pxs,est)
            T=tl(N0+d)
            for regime,peak in (("A",max(mem,OUTP)),("B",mem)):
                res.append((S(N0+d,peak) if True else 0,regime,est,c,kT2,kT1,kG,pxs,T,mem,d))
def best(regime,est):
    r=[x for x in res if x[1]==regime and x[2]==est]
    return min(r)
S_hold_A=S(N0,OUTP); S_hold_B=S(N0,SRCH)
print("S shipped (A: peak=output)",S_hold_A,"S if output streamed (B)",S_hold_B)
for est in (True,False):
    for reg in "AB":
        print(reg,"est" if est else "bound",best(reg,est))
# single-factor table (regime B)
def one(label,**kw):
    p=dict(c=3,kT2=7,kT1=7,kG=7,pxs=False); p.update(kw)
    out=[]
    for est in (True,False):
        d,mem=evaluate(p['c'],p['kT2'],p['kT1'],p['kG'],p['pxs'],est)
        out.append((est,round(d/N0*100,4),mem,round(tl(N0+d),5),round(S(N0+d,mem),5),round(S(N0+d,max(mem,OUTP)),5)))
    print(label,out)
one("hold")
one("T2 1 copy (single-copy T2', all lanes)",c=1)
one("base band dropped T2/T1/gate (k=6 each)",kT2=6,kT1=6,kG=6)
one("T2G base T2 only k=6",kT2=6)
one("T1 only k=6",kT1=6)
one("gate only k=6",kG=6)
one("replicas shifted (k=1 all)",kT2=1,kT1=1,kG=1)
one("repl shifted + c=1",c=1,kT2=1,kT1=1,kG=1)
one("PXF small",pxs=True)
one("repl k=1 T2 only",kT2=1)
one("repl k=1 T1 only",kT1=1)
one("repl k=1 gate only",kG=1)
# recompute-by-automaton (no table at all) for reference
for nm,words,lk,cost in (("T2 all 21*2^32",21*2**32,LT2,31),("T1 all 7*2^32",7*2**32,LT1,31),("gate all 7*2^30",7*2**30,LG,39)):
    d=lk*cost; mem=SRCH-words*W
    print("recompute",nm,"dT bits",round(log2((N0+d)/N0),4),"mem",mem,"gain bits",round(log2(SRCH/mem),4))
# peak/size facts
print("bytes: T2G",(2**34+2**30)*W,"REPL",6*(2**34+2**30)*W,"PXF",3*2**32*W)
print("2^20 =",2**20,"min search floor (code)",CODE, log2(CODE))
print("log2 srch",log2(SRCH),"out",log2(OUTP))
