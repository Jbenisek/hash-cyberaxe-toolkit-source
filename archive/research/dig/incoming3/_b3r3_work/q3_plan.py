"""Exact search of mask placement / add order for the whole 3-round packed circuit, under the shipped op model (36-bit lanes, bounds).
Per add: every order / premask / postmask -> Pareto set of (cost, out bound). Per call: product over its 4 adds. Subsystems {cols s,s+2 / diags s,s+2}
(col j reads a from diag j, c from diag j+2 mod 4), so the circuit splits in two independent halves; DP over 3 rounds with Pareto pruning."""
import sys,json,itertools; sys.path.insert(0,'.')
import b3core as B
from b3core import M32,LIM,IV,GC
def merge(out,o,c,n):
    if o not in out or c<out[o][0]: out[o]=(c,n)
    elif c==out[o][0]: out[o]=(c,out[o][1]+n)
_am={}
def add_plans(items):
    c=sum(i[1] for i in items if i[0]=='c')&M32
    vs=tuple(i[1] for i in items if i[0]=='v')
    if not vs: return {('c',c):(0,1)}
    start=tuple(sorted(vs+((c,) if c else ())))
    if start in _am: return _am[start]
    memo={}
    def rec(st):
        if st in memo: return memo[st]
        out={}
        memo[st]=out
        if len(st)==1: merge(out,('v',st[0]),0,1)
        for idx,b in enumerate(st):
            if b>M32 and len(st)>1 or (b>M32 and len(st)==1):
                ns=tuple(sorted(st[:idx]+(M32,)+st[idx+1:]))
                for o,(c0,n0) in rec(ns).items(): merge(out,o,c0+1,n0)
        for i in range(len(st)):
            for j in range(i+1,len(st)):
                if st[i]+st[j]<LIM:
                    ns=tuple(sorted(st[:i]+st[i+1:j]+st[j+1:]+(st[i]+st[j],)))
                    for o,(c0,n0) in rec(ns).items(): merge(out,o,c0+1,n0)
        return out
    r=rec(start)
    keep={}
    for o,(cst,n) in sorted(r.items(),key=lambda kv:(kv[1][0],kv[0][1])):
        if not any(c2<=cst and o2[1]<=o[1] for o2,(c2,n2) in keep.items()): keep[o]=(cst,n)
    _am[start]=keep; return keep
def xor_item(a,b):
    if a[0]=='c' and b[0]=='c': return ('c',a[1]^b[1])
    if a[0]=='c' and a[1]==0: return b
    if b[0]=='c' and b[1]==0: return a
    return ('v',(1<<max(a[1].bit_length(),b[1].bit_length()))-1)
def xor_cost(a,b):
    if a[0]=='c' and b[0]=='c': return 0
    if (a[0]=='c' and a[1]==0) or (b[0]=='c' and b[1]==0): return 0
    return 1
def ror_item(a,r): return ('c',B.ror(a[1],r)) if a[0]=='c' else ('v',M32)
def ror_cost(a): return 0 if a[0]=='c' else 5
def call_plans(A,Bb,C,D,x,y):
    res={}
    for oa1,(c1,n1) in add_plans([A,Bb,x]).items():
        dd=xor_item(D,oa1); d1=ror_item(dd,16); cd=xor_cost(D,oa1)+ror_cost(dd)
        for oc1,(c2,n2) in add_plans([C,d1]).items():
            bb=xor_item(Bb,oc1); b1=ror_item(bb,12); cb=xor_cost(Bb,oc1)+ror_cost(bb)
            for oa2,(c3,n3) in add_plans([oa1,b1,y]).items():
                dd2=xor_item(d1,oa2); d2=ror_item(dd2,8); cd2=xor_cost(d1,oa2)+ror_cost(dd2)
                for oc2,(c4,n4) in add_plans([oc1,d2]).items():
                    bb2=xor_item(b1,oc2); b2=ror_item(bb2,7); cb2=xor_cost(b1,oc2)+ror_cost(bb2)
                    cost=c1+c2+c3+c4+cd+cb+cd2+cb2; key=(oa2,oc2,b2,d2)
                    merge(res,key,cost,n1*n2*n3*n4)
    return res
def dominated(k2,c2,k,c):
    return c2<=c and all(u==v or (u[0]=='v' and v[0]=='v' and u[1]<=v[1]) for u,v in zip(k2,k))
# (a half-split driver was here; it mis-folded round-0 b/d constants of the other half and is superseded by q3_opt.py)
