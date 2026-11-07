"""Optimal mask placement / add order (exact search over the bound model) and rebuild of the optimum as a real circuit."""
import sys,itertools,json; sys.path.insert(0,'.')
import b3core as B
from b3core import M32,LIM,IV,GC
import q3_plan as P
def mg(out,o,c,pl):
    if o not in out or c<out[o][0]: out[o]=(c,pl)
_am={}
def add_rec(items):
    c=sum(i[1] for i in items if i[0]=='c')&M32
    vs=tuple(i[1] for i in items if i[0]=='v')
    if not vs: return {('c',c):(0,())}
    start=tuple(sorted(vs+((c,) if c else ())))
    if start in _am: return _am[start]
    memo={}
    def rec(st):
        if st in memo: return memo[st]
        out={}; memo[st]=out
        if len(st)==1: mg(out,('v',st[0]),0,())
        for idx,b in enumerate(st):
            if b>M32:
                ns=tuple(sorted(st[:idx]+(M32,)+st[idx+1:]))
                for o,(c0,p0) in rec(ns).items(): mg(out,o,c0+1,(('mask',idx),)+p0)
        for i in range(len(st)):
            for j in range(i+1,len(st)):
                if st[i]+st[j]<LIM:
                    ns=tuple(sorted(st[:i]+st[i+1:j]+st[j+1:]+(st[i]+st[j],)))
                    for o,(c0,p0) in rec(ns).items(): mg(out,o,c0+1,(('add',i,j),)+p0)
        return out
    r=rec(start); keep={}
    for o,(cst,pl) in sorted(r.items(),key=lambda kv:(kv[1][0],kv[0][1])):
        if not any(c2<=cst and o2[1]<=o[1] for o2,(c2,p2) in keep.items()): keep[o]=(cst,pl)
    _am[start]=keep; return keep
def call_rec(A,Bb,C,D,x,y):
    res={}
    for oa1,(c1,p1) in add_rec([A,Bb,x]).items():
        dd=P.xor_item(D,oa1); d1=P.ror_item(dd,16); cd=P.xor_cost(D,oa1)+P.ror_cost(dd)
        for oc1,(c2,p2) in add_rec([C,d1]).items():
            bb=P.xor_item(Bb,oc1); b1=P.ror_item(bb,12); cb=P.xor_cost(Bb,oc1)+P.ror_cost(bb)
            for oa2,(c3,p3) in add_rec([oa1,b1,y]).items():
                dd2=P.xor_item(d1,oa2); d2=P.ror_item(dd2,8); cd2=P.xor_cost(d1,oa2)+P.ror_cost(dd2)
                for oc2,(c4,p4) in add_rec([oc1,d2]).items():
                    bb2=P.xor_item(b1,oc2); b2=P.ror_item(bb2,7); cb2=P.xor_cost(b1,oc2)+P.ror_cost(bb2)
                    mg(res,(oa2,oc2,b2,d2),c1+c2+c3+c4+cd+cb+cd2+cb2,(p1,p2,p3,p4))
    return res
def replay(tr,items,plan):
    c=sum(i[1] for i in items if i[0]=='c')&M32
    vs=[i for i in items if i[0]=='v']
    if not vs: return ('c',c)
    key=lambda t:t[2]
    cur=sorted(vs+([('k',0,c)] if c else []),key=key)
    for st in plan:
        if st[0]=='mask': cur[st[1]]=tr.mask(cur[st[1]])
        else:
            i,j=st[1],st[2]; a,b=cur[i],cur[j]
            if a[0]=='k': a,b=b,a
            if b[0]=='k': r=('v',tr.emit('add',[a[1]],B.REP*b[2]),a[2]+b[2])
            else: r=('v',tr.emit('add',[a[1],b[1]]),a[2]+b[2])
            cur=[x for n,x in enumerate(cur) if n not in(i,j)]+[r]
        cur=sorted(cur,key=key)
    return cur[0]
def exec_call(tr,v,j,msgv,plans,rd):
    a,b,c,d=GC[j]; x,y=msgv; p1,p2,p3,p4=plans
    tr.tag=(rd,j,1); v[a]=replay(tr,[v[a],v[b],x],p1); v[d]=tr.ror(tr.xor(v[d],v[a]),16)
    tr.tag=(rd,j,2); v[c]=replay(tr,[v[c],v[d]],p2); v[b]=tr.ror(tr.xor(v[b],v[c]),12)
    tr.tag=(rd,j,3); v[a]=replay(tr,[v[a],v[b],y],p3); v[d]=tr.ror(tr.xor(v[d],v[a]),8)
    tr.tag=(rd,j,4); v[c]=replay(tr,[v[c],v[d]],p4); v[b]=tr.ror(tr.xor(v[b],v[c]),7)
def search():
    mm=[('c',0)]*8+[('v',M32)]*8; msg=[]
    for r in range(3):
        msg.append([(mm[2*j],mm[2*j+1]) for j in range(8)]); mm=[mm[i] for i in B.PERM]
    v0=[('c',w) for w in IV]+[('c',w) for w in IV[:4]]+[('c',0),('c',0),('c',64),('c',11)]
    choice={}; tot=0
    v0c=list(v0)
    _t=B.Tr()
    _v=list(v0)
    _m=[('c',0)]*8+[('v','i%d'%i,M32) for i in range(8,16)]
    for j in range(4):
        a,b,c,d=GC[j]; x,y=_m[2*j],_m[2*j+1]
        _v[a]=_t.add(_v[a],_v[b],x); _v[d]=_t.ror(_t.xor(_v[d],_v[a]),16); _v[c]=_t.add(_v[c],_v[d]); _v[b]=_t.ror(_t.xor(_v[b],_v[c]),12)
        _v[a]=_t.add(_v[a],_v[b],y); _v[d]=_t.ror(_t.xor(_v[d],_v[a]),8); _v[c]=_t.add(_v[c],_v[d]); _v[b]=_t.ror(_t.xor(_v[b],_v[c]),7)
    assert len(_t.prog)==0
    v0c=_v
    def apply(st,j,k):
        a,b,c,d=GC[j]; st[a]=k[0]; st[c]=k[1]; st[b]=k[2]; st[d]=k[3]
    for s in (0,1):
        cc=[s,s+2]; dd=[4+s,6+s]
        states={tuple(v0c):(0,())}
        for r in range(3):
            new={}
            for st,(cst,hist) in states.items():
                if r==0:
                    cr=[{None:(0,((),(),(),()))} for _ in cc]   # round-0 columns are all constants (folded, free); post-column constants are in v0c
                else:
                    st=list(st)
                    for i in (4,5,6,7,12,13,14,15): st[i]=('v',M32)    # b, d words are clean rotation outputs (other half's included)
                    st=tuple(st)
                    cr=[call_rec(*[st[i] for i in GC[j]],*msg[r][j]) for j in cc]
                for (k0,(c0,p0)),(k1,(c1,p1)) in itertools.product(cr[0].items(),cr[1].items()):
                    st1=list(st)
                    if r>0: apply(st1,cc[0],k0); apply(st1,cc[1],k1)
                    dr=[call_rec(*[st1[i] for i in GC[j]],*msg[r][j]) for j in dd]
                    for (k2,(c2,p2)),(k3,(c3,p3)) in itertools.product(dr[0].items(),dr[1].items()):
                        st2=list(st1); apply(st2,dd[0],k2); apply(st2,dd[1],k3)
                        t=cst+c0+c1+c2+c3
                        if tuple(st2) not in new or t<new[tuple(st2)][0]:
                            new[tuple(st2)]=(t,hist+(((r,cc[0]),p0),((r,cc[1]),p1),((r,dd[0]),p2),((r,dd[1]),p3)))
            kept={}
            for k,(c,h) in sorted(new.items(),key=lambda kv:kv[1][0]):
                if not any(P.dominated(k2,c2,k,c) for k2,(c2,h2) in kept.items()): kept[k]=(c,h)
            states=kept
        best=None
        for st,(c,h) in states.items():
            fin=0
            for i in (s,s+2):
                z=P.xor_item(st[i],st[i+8]); fin+=P.xor_cost(st[i],st[i+8])+(1 if z[0]=='v' and z[1]>M32 else 0)+P.xor_cost(st[i+4],st[i+12])
            if best is None or c+fin<best[0]: best=(c+fin,h)
        for (rc,pl) in best[1]: choice[rc]=pl
        tot+=best[0]
    return choice,tot
def build_opt(choice,rounds=3):
    tr=B.Tr()
    v=[('c',w) for w in IV]+[('c',w) for w in IV[:4]]+[('c',0),('c',0),('c',64),('c',11)]
    m=[('c',0)]*8+[('v','i%d'%i,M32) for i in range(8,16)]
    for rd in range(rounds):
        for j in range(8): exec_call(tr,v,j,(m[2*j],m[2*j+1]),choice[(rd,j)],rd)
        m=[m[i] for i in B.PERM]
    tr.tag=('final',); out=[]
    for i in range(8):
        z=tr.xor(v[i],v[i+8])
        if z[2]>M32: z=tr.mask(z)
        out.append(z[1])
    return tr.prog,out,v
if __name__=='__main__':
    import random,pickle
    choice,tot=search(); print('model optimum',tot)
    prog,out,v=build_opt(choice); print('built circuit ops',len(prog))
    from collections import Counter; print(Counter(o['kind'] for o in prog))
    rnd=random.Random(5)
    print('equals scalar on 300 batches:',all(B.check(prog,out,[rnd.getrandbits(256) for _ in range(7)]) for _ in range(300)))
    pickle.dump((choice,prog,out),open('q3_opt.pkl','wb'))
    # where do masks sit
    for k,o in enumerate(prog):
        if o['kind']=='and' and o['imm']==B.REP*B.M32: print('mask op',k,o['tag'])
