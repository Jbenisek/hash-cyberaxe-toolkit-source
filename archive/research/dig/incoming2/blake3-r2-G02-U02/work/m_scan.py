# G02-U02 memory scan of blake3-r2 (pkgB3S2). Reuses ledger_ref.py (verbatim ledger.py of proof.md Sec 18) for RC, budgets, N.
import io, contextlib, math
from fractions import Fraction
ns={}
with contextlib.redirect_stdout(io.StringIO()):
    exec(open('ledger_ref.py').read(), ns)
N=ns['N']; P_B=ns['P_B']; A_B=ns['A_B']; F_B=ns['F_B']; RC=ns['RC']; U=ns['U']; ONCE=ns['ONCE']
l2=lambda x: math.log2(x) if isinstance(x,int) and x<2**1000 else (x.bit_length()-1+math.log2(x/(1<<(x.bit_length()-1))))
def L2(x):  # exact-ish log2 of a big int/Fraction
    x=Fraction(x); return math.log2(x.numerator)-math.log2(x.denominator) if x.numerator<2**1000 else (x.numerator.bit_length()-1)+math.log2(x.numerator/ (1<<(x.numerator.bit_length()-1)))-math.log2(x.denominator) if x.denominator<2**1000 else None
T=Fraction(N,430)
print('KNOWN ANSWER time_log2 =',round(L2(T),7),' (claim 62.43471)')
W=32
words=dict(ROT=3*2**32, BT=7*2**32, SMALLmax=168522+2**21+29952+2**18+4096+1024+512+512)
print('SMALL word-sum of component maxima',words['SMALLmax'],'(proof: fewer than 2,563,914)')
tables=171*2**30*W
code=2**32*W
small=2563914*W
search=tables+small+code
out=8796093155510
print('search phase bytes bound',search,'proof says 6,013,036,259,648 ->',search==6013036259648, ' log2',math.log2(search))
print('output phase',out,'log2',math.log2(out))
Smem=lambda b: max(0,math.log2(b)-20)
base_t=L2(T)
print('S current (peak=output): ',base_t+Smem(out), ' S with STREAM (peak=search):',base_t+Smem(search))
PL=P_B+2**19          # passing lanes budget (ledger row)
OC=A_B+16384          # opened clusters budget
def dT(du_pass=0,du_open=0,once_saved=0):
    return L2((N+du_pass*PL+du_open*OC-430*0-once_saved)/430) - base_t
obj={}
# rotation tables: per-table extra units per passing lane (4-op scalar ROR vs XOR+load)
cases=[('ROT_ROR16',3,0,2**32*W,0),('ROT_ROR7',4,0,2**32*W,2**32),('ROT_ROR12',6,0,2**32*W,0),('ROT_all3',12,0,3*2**32*W,3*2**35+2**32),
       ('BT_all7',0,12,7*2**32*W,30*2**32),('BT_lanecopies6',0,4,6*2**32*W,24*2**32)]
for name,dp,do,saved,once in cases:
    dt=L2((N+dp*PL+do*OC-430*0-once)/430)-base_t   # once-saved units removed from numerator (approx: build rows)
    for peak,label in ((out,'cur'),(search,'stream')):
        newpeak = peak if label=='cur' else peak-saved
        dm=Smem(newpeak)-Smem(peak)
        print(f'{name:16s} dT={dt:+.6f} bits  {label:6s} dMem={dm:+.6f}  dS={dt+dm:+.6f}   bytes saved={saved:,}')
# SMALL
lists_b=168522*W
per_ctx=2**26+2**20
dt_lists=L2((N+per_ctx*(RC-1)*1)/430)-base_t
print('SMALL member lists recompute per context: dT=',dt_lists,'bits; memory saved bytes',lists_b,'stream gain',Smem(search-lists_b)-Smem(search))
print('SMALL all bound removed (impossible) stream gain',Smem(search-small)-Smem(search))
# breakpoints: tables-only crossing of 2^20
print('bytes to hold peak at 2^20:',2**20,' search',search,'ratio log2',math.log2(search/2**20))
print('per-object total S (if object alone): ROT',math.log2(words['ROT']*W)-20,'BT',math.log2(words['BT']*W)-20,'SMALL',math.log2(small)-20)
print('ROT bytes',words['ROT']*W,'log2',math.log2(words['ROT']*W),'BT bytes',words['BT']*W,'log2',math.log2(words['BT']*W))
print('passing lane budget',PL,'opened',OC,'F_B',F_B,'RC',RC)
