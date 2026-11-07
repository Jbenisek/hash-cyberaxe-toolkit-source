# exact integer recount of the B3U (c994a61f) ledger rows and the S_old (SEL) sensitivity. Our code.
from fractions import Fraction
from math import log2
import math
def L2(n,d=430):  # log2(n/d) via integer-safe float on big ints
    return math.log2(n)-math.log2(d)
rows=dict(WB=58673448711009395272, W_CTX=32833716, credit=4766763973273283351,
 ctx=2011846272234187368, block=293521644581279472, once=2537846523297832,
 S_old=4859252056537550848, final=36146994518950876)
N=70643517498710778735
s=sum(rows.values())
print("sum rows",s,"N",N,"equal",s==N)
# certificate 2^571889 * 430^10000 <= N^10000 < 2^571890 * 430^10000
lo=2**571889*430**10000; hi=2**571890*430**10000
print("certificate holds", lo<=N**10000<hi)
print("log2(N/430)=%.8f"%L2(N))
S_old=116*18021*(1<<42)//2+116*((1<<51)+(1<<10))+(1<<50)
print("S_old recomputed",S_old, S_old==rows['S_old'])
print("  of which 116 logged-max term", 116*18021*(1<<42)//2, "= 2^%.3f"%log2(116*18021*(1<<42)/2))
cap_S=116*5*(1<<53)+116*((1<<51)+(1<<10))+(1<<50)
one_pair=5*(1<<53)+(1<<51)+(1<<10)+(1<<50)
run20=int(4770*(1<<42))+(1<<51)+(1<<10)+(1<<50)   # logged run 20 only at 2^42/s, plus count caps
N0=N-S_old
def tl(S): return L2(N0+S)
print("variant                          S            share_of_N   time_log2   delta_vs_filed")
base=tl(S_old)
for name,S in [("filed (logged maxima 116 lines)",S_old),("cap-based 116*5*2^53 (5a08fffa form)",cap_S),
  ("SEL one pair at caps (5*2^53+..)",one_pair),("run 20 only: 4770s*2^42+counts",run20),("no SEL charge",0)]:
    print("%-38s %.4e  %.4f  %.5f  %+.5f"%(name,S,S/(N0+S),tl(S),tl(S)-base))
# sensitivity
for f in (0.5,2,10):
    print("S_old x%g: %+.5f bits"%(f,tl(int(S_old*f))-base))
print("bits per unit: d time/d ln S_old at filed point = %.5f bits per e-fold; per doubling %.5f"%(S_old/N/ math.log(2), tl(2*S_old)-base))
# rate sensitivity: ops/s used for the logged maximum, 2^42 vs the instruction ceiling in 12.2 (2^35.5 instr/s x 2 ops)
for e in (36.5,38,40,42):
    S=int(116*18021*(2**e)/2)+116*((1<<51)+(1<<10))+(1<<50)
    print("rate 2^%.1f ops/s: S %.4e time_log2 %.5f (%+.5f)"%(e,S,tl(S),tl(S)-base))
print("rounded-up claim 57.1890 slack: %.8f bits"%(57.1890-L2(N)))
# how much extra S_old fits before 4-decimal round-up moves to 57.1891
Smax=None
lo_,hi_=S_old,S_old*50
while hi_-lo_>1:
    mid=(lo_+hi_)//2
    if tl(mid)<=57.1890: lo_=mid
    else: hi_=mid
print("largest S_old keeping claim 57.1890: %.4e = %.4f x filed"%(lo_,lo_/S_old))
# preprocessing allowance: 2^54 units *430 ops
print("S_old in units: 2^%.4f ; preprocessing_log2=54 allowance 2^54 units = %.4e ops"%(math.log2(S_old/430), 2**54*430))
