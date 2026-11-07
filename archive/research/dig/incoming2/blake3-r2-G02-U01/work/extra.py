import io,contextlib
from math import log2
with contextlib.redirect_stdout(io.StringIO()):
    import g02u01 as g
SR=g.SRCH
def gain(x): return log2(SR/(SR-x))
print("T2' base single copy only: bytes",2*2**32*32,"gain B",gain(2*2**32*32))
print("T2G band all: bytes",(2**34+2**30)*32,"gain B",gain((2**34+2**30)*32))
print("REPL bytes",6*(2**34+2**30)*32,"gain B",gain(6*(2**34+2**30)*32), "remaining",SR-6*(2**34+2**30)*32)
print("PXF gain",gain(3*2**32*32))
print("T2 single copy all lanes bytes",14*2**32*32,"gain",gain(14*2**32*32))
print("dT bits PXF small", log2((g.N0+g.AB-2**37)/g.N0))
print("dT bits repl shift est/bound")
for est in (True,False):
    d,m=g.evaluate(3,1,1,1,False,est); print(est,d,log2((g.N0+d)/g.N0),g.tl(g.N0+d))
    d,m=g.evaluate(3,6,6,6,False,est); print("base",est,d,log2((g.N0+d)/g.N0),g.tl(g.N0+d))
    d,m=g.evaluate(1,1,1,1,True,est); print("all",est,d,log2((g.N0+d)/g.N0),g.tl(g.N0+d),m,g.S(g.N0+d,m))
print("bits output streamed gain",log2(g.OUTP/SR))
