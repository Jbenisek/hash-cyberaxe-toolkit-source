import json,sys,collections
pc=lambda m: bin(m).count('1')
q=int(sys.argv[1]); d=json.load(open(f'tail_q{q}_s1.json'))
hist={int(k):v for k,v in d['hist'].items()}; col={int(k):v for k,v in d['col'].items()}
def dec(c): return tuple((c>>(9-3*i))&7 for i in range(4))
# infeasible chains must have zero count
bad=[c for c in hist if not (all(pc(dec(c)[k])+pc(dec(c)[k+1])>=4 for k in range(3)))]
print('q',q,'chains seen',len(hist),'(of 337 feasible total?) infeasible-by-branch seen:',len(bad))
badcol=[c for c in col if pc(dec(c)[3])<2]; print('collisions with |s3|<2:',len(badcol))
byw=collections.defaultdict(lambda:[0,0,set()])
for c,h in hist.items():
    s=dec(c); w=tuple(pc(m) for m in s); byw[w][0]+=h; byw[w][1]+=col.get(c,0); byw[w][2].add(c)
tot=sum(hist.values()); N=q**6
print('total ordered pairs',tot,'collisions',sum(col.values()),'expected q^5-ish',N/q)
print('weights | pairs | collisions | coll chains seen | pred collisions (dim)')
for w in sorted(byw,key=lambda t:(sum(t),t)):
    P,C,S=byw[w]
    nc=len({c for c in S if col.get(c,0)>0})
    ok= all(w[k]+w[k+1]>=4 for k in range(3)) and w[3]>=2
    dim=3+w[0]-sum(3-x for x in w[1:])-1
    print(w,P,C,nc,'feasible' if ok else 'INFEASIBLE','dim',dim if ok else '-','q^dim=',q**dim if ok else '-')
