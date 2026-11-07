import a0lean38 as L, itertools
M=L.M
CL=L.CLASSES; G=L.GRP
print('c7of(base)==c7:', sum(L.c7of(b)==c for c,b,m in CL), 'inG(base):', sum(L.in_G(b) for c,b,m in CL))
print('masks', sorted({hex(m) for c,b,m in CL}))
# mask determined by program?
pm={}
for (c,b,m),g in zip(CL,G): pm.setdefault(g,set()).add(m)
print('masks per program', {g:[hex(x) for x in s] for g,s in pm.items()})
# bits of base outside all masks that vary
allmask=0
for c,b,m in CL: allmask|=m
var=0
for c,b,m in CL: var|=(b^CL[0][1])&~m&M
print('varying const bits', bin(var), bin(var).count('1'))
# does program depend on base bits? find smallest decision tree on bits of (base & ~mask) w/ mask included as feature
items=[(b,m,g) for (c,b,m),g in zip(CL,G)]
def feats(b,m): return [(b>>i)&1 for i in range(32)]
def tree(idx,depth=0):
    gs={items[i][2] for i in idx}
    if len(gs)==1: return ('leaf',gs.pop())
    best=None
    for bit in range(32):
        a=[i for i in idx if (items[i][0]>>bit)&1]; z=[i for i in idx if not (items[i][0]>>bit)&1]
        if not a or not z: continue
        sc=max(len({items[i][2] for i in a}),len({items[i][2] for i in z}))*1000+abs(len(a)-len(z))
        sc=len({items[i][2] for i in a})+len({items[i][2] for i in z})
        if best is None or sc<best[0]: best=(sc,bit,a,z)
    if best is None: return ('unsep',sorted(gs))
    return ('bit',best[1],tree(best[3],depth+1),tree(best[2],depth+1))
t=tree(list(range(90)))
def cnt(t): return 0 if t[0] in('leaf','unsep') else 1+cnt(t[2])+cnt(t[3])
def dep(t): return 0 if t[0] in('leaf','unsep') else 1+max(dep(t[2]),dep(t[3]))
def has_unsep(t): return t[0]=='unsep' or (t[0]=='bit' and (has_unsep(t[2]) or has_unsep(t[3])))
print('tree internal nodes', cnt(t),'depth',dep(t),'unseparable',has_unsep(t))
