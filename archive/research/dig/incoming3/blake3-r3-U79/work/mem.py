# MEM.DPTAB / MEM.CODE / MEM.CNT M2-M4: exact memory accounting of the filed program and the S = T + max(0, log2(bytes) - 20) trade
from fractions import Fraction
from math import log2, sqrt, ceil
from common import rho as R
orig_plan=R.plan
lg0=R.ledger(256); T0=log2(lg0['total']/638)
P0=orig_plan(256)
TABLE=P0['tmax']*32; CODEI=10400; CODEB=CODEI*36; CNT=2048
print('filed: table %d entries x 32 B = %d B ; code <= %d instr x 36 B = %d B ; counters/working < %d B ; total %d B = 2^%.4f ; slack to 2^20: %d B (%.2f%%)'%(P0['tmax'],TABLE,CODEI,CODEB,CNT,TABLE+CODEB+CNT,log2(TABLE+CODEB+CNT),2**20-TABLE-CODEB-CNT,100*(2**20-TABLE-CODEB-CNT)/2**20))
def S(T,B): return T+max(0.0,log2(B)-20)
# instruction count of the filed code: main body 9587 (U=16), recovery 640, handlers about 170
assert 9587+640+170<=CODEI
# --- DPTAB: sweep of DP bits d (table = tmax entries)
def plan_d(d):
    p=orig_plan(256)
    L=1<<d; N=p['N']
    Q=p['Q']  # Q depends on d through INFLIGHT*L: recompute like plan()
    ureq=R.isqrt(2*N*R.LAMBDA.numerator//R.LAMBDA.denominator)+2
    num,den=ureq+R.INFLIGHT*L+1,R.CUTLOSS.denominator
    q=-(-num*den//(den-R.CUTLOSS.numerator)); b=-(-q//R.LANES)
    mean=b*R.LANES/L
    tmax=ceil(mean+16.2*sqrt(mean))
    c=R.KAPPA*L; sb=1<<48
    return dict(n=256,d=d,L=L,N=N,s1=32,Q=b*R.LANES,B=b,Sb=sb,c=c,capr=c+sb,tmax=tmax,e2max=2*b*R.LANES//(1<<32)+64)
print('--- DPTAB M3/M4: sweep of DP bits d (all else as filed; tmax = mean + 16.2 sigma, the filed margin); S = T + memory term, code and counters as filed')
rows=[]
for d in range(104,124):
    R.plan=lambda n,d=d: plan_d(d)
    lg=R.ledger(256); T=log2(lg['total']/638); p=plan_d(d)
    B=p['tmax']*32+CODEB+CNT
    rows.append((d,T,p['tmax'],B,S(T,B)))
    print('  d=%d: T=%.5f (%+.5f), tmax=%d, table %d B, total %d B = 2^%.3f, S=%.5f (%+.5f)'%(d,T,T-T0,p['tmax'],p['tmax']*32,B,log2(B),S(T,B),S(T,B)-T0))
R.plan=orig_plan
best=min(rows,key=lambda r:r[4]); print('  best S in sweep: d=%d S=%.5f (filed d=114: %.5f)'%(best[0],best[4],[r for r in rows if r[0]==114][0][4]))
# smallest table that keeps S = T0 + eps : which d gives memory <= 2^20 with the largest d? (all d>=114 do)
print('--- DPTAB M2: hold vs shrink the entry (key 8 + index 8 + length 16 = 32 B filed)')
for nm,eb in (('32 B filed',32),('25 B packed (key 8, index 2, length 15)',25),('16 B',16),('8 B key only (needs a second pass to find owner, +1 bit)',8)):
    print('  %-52s table %d B, total %d B = 2^%.3f ; S change 0 (memory term is 0 either way)'%(nm,P0['tmax']*eb,P0['tmax']*eb+CODEB+CNT,log2(P0['tmax']*eb+CODEB+CNT)))
# --- CODE: unroll U
print('--- CODE M2/M3/M4: unroll factor U (instructions U*599+3 main + 640 recovery + 170 handlers, 36 B each)')
base=lg0['plan']['B']
def T_U(U):
    per=U*(595+4)+3
    main=Fraction(per,U)*base
    return log2((lg0['total']-lg0['parts']['main']+main)/638)
for U in (1,2,4,8,16,17,18,19,20,24,32,48,64):
    ins=U*599+3+640+170; b=ins*36; B=TABLE+b+CNT; T=T_U(U)
    print('  U=%2d: %6d instr, code %7d B, total %8d B = 2^%.4f, T %.5f (%+.5f), S %.5f (%+.5f)'%(U,ins,b,B,log2(B),T,T-T0,S(T,B),S(T,B)-T0))
Umax=max(U for U in range(1,200) if TABLE+(U*599+3+640+170)*36+CNT<=2**20)
print('  largest U with total <= 2^20: %d (T %+.5f vs filed)'%(Umax,T_U(Umax)-T0))
print('  no-recompute alternative: code generated at run time is not cheaper: any instruction emitted costs >= 1 op per instruction executed once per emission (not priced here)')
# --- CNT
print('--- CNT: counters and working words: 64 registers x 32 B = %d B is the bound used; liveness peak of the batch circuit = 25 values (U81 regs.py)'%CNT)
for nm,words in (('25 live batch values + 7 lane t + 7 births + 8 counters/limits',25+7+7+8),('64 (filed bound)',64)):
    print('  %-62s %d words = %d B'%(nm,words,words*32))
print('  breakpoint at 2^20: slack %d B ; one extra doubling of anything costs 1 bit of S; a table of d=113 gives total %d B = 2^%.3f'%(2**20-TABLE-CODEB-CNT,2*TABLE+CODEB+CNT,log2(2*TABLE+CODEB+CNT)))
# --- joint optimum: DP bits d, entry bytes, unroll U ; S = T + max(0, log2(total) - 20)
print('--- JOINT M3/M4: S over (d, entry bytes, U). entry = key + 2 B index + 15 B length (length <= 2^117.6 batches needs 118 bits); key bytes kb; false-key-match probability tmax^2/2^(8kb+1) charged as success loss (0.5*log2 per prob via lambda)')
best=[]
for d in range(108,116):
    p=plan_d(d); R.plan=lambda n,d=d: plan_d(d)
    lgd=R.ledger(256); Td=log2(lgd['total']/638); R.plan=orig_plan
    tm=p['tmax']
    for kb in (4,5,6,8):
        fm=tm*tm/2.0**(8*kb+1)
        # success loss fm -> needs lambda up by fm/(1-0.39): time +0.5*log2(1+fm/(0.61*0.497))
        Tadj=Td+0.5*log2(1+fm/(0.61*0.497))-0.0
        for U in range(1,25):
            ent=kb+2+15
            B=tm*ent+(U*599+3+810)*36+CNT
            T=Tadj+T_U(U)-T0
            best.append((S(T,B),d,kb,U,ent,B,T,fm))
best.sort()
for r in best[:6]: print('  S=%.5f (%+.5f) d=%d key %d B entry %d B U=%d total %d B = 2^%.3f T=%.5f false-match loss %.1e'%(r[0],r[0]-T0,r[1],r[2],r[4],r[3],r[5],log2(r[5]),r[6],r[7]))
filed=[r for r in best if r[1]==114 and r[2]==8 and r[3]==16]
print('  filed-like point in this model (d=114, key 8 B, entry 25 B, U=16): S=%.5f'%filed[0][0] if filed else 'n/a')
