# MACHINE.REGS Q2/Q3/Q4: register pressure of the filed 595-op batch (+4 filter ops), exact liveness; spill cost with Belady eviction
# at R registers (loads and stores each charged 1 operation); greedy re-ordering as alternative.
import re, math
from common import rho as R
src=[l.strip() for l in R._SRC.split('\n')[1:-2]]
ops=[]   # (dst, [operand value names])
for ln in src:
    d,rhs=ln.split('=',1)
    names=re.findall(r'\b[ti]\d+\b',rhs)
    ops.append((d,names))
outs=re.findall(r'\bt\d+\b',R._SRC.split('return')[1])
assert len(outs)==8
# filter on output word 0: f1=z0+K ; f2=f1&B ; compare-branch uses f2 (2 ops: charged as the "4" with the cmp+br counted as 2)
ops_f=ops+[('f1',[outs[0]]),('f2',['f1']),('cb1',['f2']),('cb2',[])]
inputs=['i%d'%i for i in range(8,16)]
def liveness(order):
    n=len(order); last={}
    for p,(d,u) in enumerate(order):
        for x in u: last[x]=p
    for o in outs: last[o]=n   # needed after the batch (next batch inputs)
    live=set(inputs); peak=len(live); prof=[]
    for p,(d,u) in enumerate(order):
        before=len(live)
        for x in set(u):
            if last.get(x,-1)==p: live.discard(x)
        live.add(d) if (d in last) else None
        after=len(live)
        need=max(before, after, before-len([x for x in set(u) if last.get(x,-1)==p])+1)
        peak=max(peak,need); prof.append(need)
    return peak,prof
def belady(order,Rn):
    n=len(order)
    uses={}
    for p,(d,u) in enumerate(order):
        for x in set(u): uses.setdefault(x,[]).append(p)
    for o in outs: uses.setdefault(o,[]).append(n)
    ptr={}
    def nxt(x,p):
        L=uses.get(x,[])
        for q in L:
            if q>=p: return q
        return 10**9
    regs=set(inputs[:Rn]); mem=set(inputs[Rn:]) | set(inputs[:Rn])  # inputs also have a memory home (loop-carried)
    loads=stores=0
    def evict(p,protect):
        nonlocal stores
        cand=[x for x in regs if x not in protect]
        v=max(cand,key=lambda x:nxt(x,p+0))
        regs.discard(v)
        if nxt(v,p)<10**9 and v not in mem: stores+=1; mem.add(v)
    for p,(d,u) in enumerate(order):
        prot=set(u)
        for x in set(u):
            if x not in regs:
                loads+=1
                if len(regs)>=Rn: evict(p,prot)
                regs.add(x)
        for x in set(u):
            if nxt(x,p+1)>=10**9 and x not in outs: regs.discard(x)
        if d.startswith('cb'): continue
        if len(regs)>=Rn: evict(p,prot-{x for x in regs if nxt(x,p+1)>=10**9})
        regs.add(d)
    for o in outs:
        if o not in regs: loads+=1
    return loads,stores
def greedy(order):
    prod={d:i for i,(d,u) in enumerate(order)}
    remaining=list(range(len(order))); done=set(inputs); sched=[]
    last={}
    for i,(d,u) in enumerate(order):
        for x in u: last.setdefault(x,set()).add(i)
    pend={x:set(s) for x,s in last.items()}
    live=set(inputs)
    while remaining:
        ready=[i for i in remaining if all((x in done) for x in order[i][1])]
        def score(i):
            d,u=order[i]; fr=sum(1 for x in set(u) if pend[x]=={i} and x not in outs)
            return (1-fr, i)
        i=min(ready,key=score)
        remaining.remove(i); sched.append(order[i]); done.add(order[i][0])
        for x in set(order[i][1]): pend[x].discard(i)
    return sched
print('ops',len(ops),'+ filter',len(ops_f)-len(ops),' (batch 595 + filter 4)')
pk,prof=liveness(ops_f)
print('emitted order: exact peak simultaneously live 256-bit values (3-address, dst may reuse a dying source): %d'%pk)
print('  profile max positions:',sorted(set(prof))[-5:], 'mean live %.1f'%(sum(prof)/len(prof)))
g=greedy(ops_f); pkg,_=liveness(g)
print('greedy re-ordered (list scheduling, free-most-operands first): peak',pkg)
main=0.99441  # main-loop share of the ledger (rho --ledger)
base=595+4+3/16
print('per-batch ops in the unrolled loop: %.4f (595 + 4 filter + 3/16 control)'%base)
rows=[]
for Rn in (8,10,12,14,16,20,24,28,32,36,40,44,48,56,64):
    for nm,od in (('emitted',ops_f),('greedy',g)):
        l,s=belady(od,Rn)
        d=main*math.log2((base+l+s)/base)
        rows.append((Rn,nm,l,s,d))
        print('R=%2d %-8s loads %4d stores %4d extra %4d ops/batch -> time +%.4f bit'%(Rn,nm,l,s,l+s,d))
# smallest R with zero spill
for nm,od in (('emitted',ops_f),('greedy',g)):
    for Rn in range(8,80):
        l,s=belady(od,Rn)
        if l+s==0: print('smallest R with no loads/stores (Belady) %s: %d'%(nm,Rn)); break
