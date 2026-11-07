# Written before run: R4 sensitivity = log2(N_new/N_base) for single-parameter changes of the proof's ledger (ledger_ext.py, verbatim).
import ledger_ext as L
from math import log2
N0=L.ledger(L.NEW)["N"]; B=log2(N0/430)
print("N",N0,"time_log2",B, "k",L.certificate(N0))
def d(**kw):
    c=dict(L.NEW); c.update(kw); r=L.ledger(c); return log2(r["N"]/N0), r
r0=L.ledger(L.NEW)
for k in ("WB","W_CTX","credit","once","final","context_and_member_rows","block_rows","S_old","N"):
    print(k, format(r0[k],","), "%.4f%%"%(100*r0[k]/N0))
print("--LIVE")
for k,v in (("setup",27),("setup",22),("setup",20),("piece",9),("piece",11),("wrap",1),("ranges",15),("ranges",17)):
    print(k,v,"%.6f"%d(**{k:v})[0])
print("per +1 unit u_live: %.3e"%( log2((N0+ r0["LIVE_B"]+L.NBLK)/N0)), "(live_b %d, NBLK %d)"%(r0["LIVE_B"],L.NBLK))
print("--PASSL")
for k,v in (("u_pass",40),("u_pass",31),("u_pass",27),("u_pass",35),("u_pass_x",0),("u_pass_x",2),("u_pass_x",12)):
    print(k,v,"%.6f"%d(**{k:v})[0])
print("shortcut analogue partial 31->27: %.6f"%d(partial=27)[0], " partial 34 (base):%.6f"%d(partial=34)[0])
print("--WCTX")
for k,v in (("words",("new",186-7)),("words",("new",186+7)),("words",("new",0)),("u_word",45),("u_word",47),("partial",27),("partial",35)):
    print(k,v,"%.6f"%d(**{k:v})[0])
# descriptor table term: 4*partial*NBLK etc is W_CTX part
print("W_CTX share %.3e of N"%(r0["W_CTX"]/N0), " 48,896->5,760 analogue: remove 43,136 units: %.3e bit"%log2((N0-43136)/N0))
print("--CREDIT")
for k,v in (("mu_millionths",4459),("mu_millionths",4425),("mu_millionths",1),("mu_millionths",4000),("mu_millionths",5000),("pre",0),("pre",30)):
    print(k,v,"%.6f"%d(**{k:v})[0])
print("credit/N %.4f%%  credit/(ctx_rows..)"%(100*r0["credit"]/N0))
capx=3*7466+614+64+3*20+15; lc=capx<<19; mc=L.cdiv(4425*L.RUN_STEPS,10**6)
print("capx",capx,"mc",mc,"sqrt term",L.isqrt(40*lc*mc-1)+1,"14lc",14*lc,"capx",capx)
print("14 L_C share of N %.4f%%, capx 14->13: %.6f bit"%(100*14*lc/N0, log2((N0-lc)/N0)))
print("--ONCE3")
print("ONCE", L.ONCE, "ONCE_BASE", L.ONCE_BASE, "extras", L.ONCE-L.ONCE_BASE)
for name,delta in (("-1%",-L.ONCE//100),("-1e14",-10**14),("+1e14",10**14),("drop extras",-(L.ONCE-L.ONCE_BASE))):
    print(name,"%.6f"%log2((N0+delta)/N0))
print("per -1e15: %.5f"%log2((N0-10**15)/N0))
print("--FINAL3")
for v in (96,64,100,127,129,256,512):
    print("fpc",v,"%.6f"%d(final_per_chunk=v)[0])
print("fpc term share %.4f%% ; per unit fpc: %.4e bit"%(100*128*2**48/N0, log2((N0+2**48)/N0)))
