from math import log2
from fractions import Fraction
RATE=1355;P=100000
N=10377085310562   # from reproduced ledger
HV=48592224; HVB=24590628
def cert(n):
    NP,CP=n**P,RATE**P
    a=(NP//CP).bit_length()-1
    while (1<<(a+1))*CP<=NP:a+=1
    while (1<<a)*CP>NP:a-=1
    return a
def T(n): return log2(n/RATE)
def Tg(n): return (cert(n)+1)/P
# ledger-charged rebuild terms (row d applied): certified 7 levels, stopped 10 levels
R_cert=7*HV*38+3*19*HV; R_stop=10*HV*38+3*25*HV
H_cert=HV*(38+3*14);     H_stop=HV*(38+3*15)
# per-block stream bound: 41 per vector per block (38 + one key word x3), 127 and 138 blocks
S_cert=127*HV*41; S_stop=138*HV*41
print('R',R_cert,R_stop,'H',H_cert,H_stop,'S',S_cert,S_stop)
base=T(N);print('T shipped',base,Tg(N))
for name,d in [('hold across levels (W.4 schedule) both runs',(H_cert-R_cert)+(H_stop-R_stop)),
               ('hold, certified run only',H_cert-R_cert),
               ('stream per block (bound 41/vec/block), both runs',(S_cert-R_cert)+(S_stop-R_stop)),
               ('naive full-key rebuild per level (no row d), both',7*HV*80+10*HV*83-R_cert-R_stop)]:
    n=N+d; print(f'{name}: dprim={d:,} dunits={d/RATE:,.0f} log2units={log2(abs(d)/RATE):.3f} T={T(n):.6f} dT={T(n)-base:+.6f} grid={Tg(n):.5f}')
B_ph=2*9**5*22*32;B_arr=2*9**5*8
print(B_ph,B_arr,B_ph+B_arr,log2(B_ph),log2(B_arr),log2(B_ph+B_arr),2**20-B_arr)
print('native 320B/vec',2*9**5*320, log2(2*9**5*320))
