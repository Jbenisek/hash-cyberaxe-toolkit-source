import math
from fractions import Fraction
L=math.log2
N=Fraction(2014712256488305708573,271000000000); T=L(N)
MiB=2**20
def S(t,b): return t+max(0,L(b)-20)
b_rule=2**27.2
bp=int(113.5*MiB); K=31*MiB; conn=2**23; code=2**18*32
print("T",T,"S rule 27.2:",S(T,b_rule))
print("B' 113.5MiB bytes",bp,"log2",L(bp)," B'+K",bp+K,L(bp+K))
# D152 phase split
dN=Fraction((62*MiB)//4+2**31,1355)
T2=L(N+dN); print("phase split dT bits",T2-T," units",float(dN))
cand=int((113.5+8+2+0.62)*MiB); Pph=84085776+2**18*32; Eph=50199808
print("cand phase",cand,L(cand)," P+code",Pph,L(Pph)," E+code",Eph,L(Eph))
print("S phase split m=2^27.0:",S(T2,2**27.0)," saving vs rule",S(T,b_rule)-S(T2,2**27.0))
# if B' phase fell under P phase (P+code the peak)
print("S if peak=P+code:",S(T2,Pph)," saving",S(T,b_rule)-S(T2,Pph))
# with cores.bin held in P phase (13,325,904 B)
cb=13325904
print("P+code+cores.bin",Pph+cb,L(Pph+cb)," delta bits vs P+code",L(Pph+cb)-L(Pph))
print("cores.bin log2",L(cb)," bits above 2^20",L(cb)-20)
print("bits-only list: 4574 bits*2B",4574*2,"; 1741 cores",17100*2)
print("MINW+WT2 bytes",32+1024)
# breakpoint 2^20 for a whole-run: T available
print("memory term at 2^26.46:",L(Pph)-20,"; at 2^27.2: 7.2")
# B' share of time
print("B' true max online 2^28.60 units share of N:",2**28.60/float(N), "B_TRUE 2^29:",2**29/float(N))
print("T1/T2/export post-J prim",131616018432-33576992448,"units",(131616018432-33576992448)/1355,"log2",L((131616018432-33576992448)/1355))
print("share of N (T1/T2 export units 97.13M):",97133592.94/float(N), "log2 N:",T)
