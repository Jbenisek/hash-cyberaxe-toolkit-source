import sys, math, time
sys.argv=['x']
import frontline as F
t0=time.time()
res={}
tot_words_list=0; tot_pc=0
distinct={}
rows=[]
for t in (0,1):
    st,p16,dead=F.level16(t)
    ncount={s:st.count(s) for s in set(st)}
    for cls in range(8):
        lists=F.get_lists(t,F.KC[cls])
        for s2,v in lists.items():
            if v is None: continue
            words,pc=v
            n2=pc[1<<17]          # entries in doubled list = 2n
            rows.append((t,cls,s2,len(words),n2,pc[1<<16]))
            distinct[(t,s2,F.KD[F.KC[cls]].get(s2,0))]=(len(words),n2)
    # check typed E
    typ=sum(ncount[s]*p16[s].count(1) for s in p16 if s!=dead)
    print('type',t,'typed E',typ,F.TYPE_E[t],'live states',len(p16)-1,'lowhalves live',sum(ncount[s] for s in p16 if s!=dead))
print('lists (class,state) stored, undeduped:',len(rows))
lw=sum(r[3] for r in rows); pcw=len(rows)*((1<<17)+1)
print('list packed words (undeduped)',lw,' prefix entries',pcw)
dl=sum(v[0] for v in distinct.values()); print('distinct (t,state,mask) lists',len(distinct),'list words',dl,'prefix entries',len(distinct)*((1<<17)+1))
# per type breakdown
for t in (0,1):
    print('type',t,'undeduped list words',sum(r[3] for r in rows if r[0]==t),'max list words',max(r[3] for r in rows if r[0]==t),'sum of n',sum(r[5] for r in rows if r[0]==t))
# typed (no class cut): D=0
typed={}
for t in (0,1):
    for s2,v in F.get_lists(t,0).items():
        pass
print('KD0 lists not the pure typed ones; computing pure typed')
pure=0;purew=0
for t in (0,1):
    st,p16,dead=F.level16(t)
    for s2,bm in p16.items():
        if s2==dead: continue
        n=sum(bm); purew+= -(-2*n//7); pure+=1
print('pure typed lists',pure,'words',purew)
print('secs',time.time()-t0)
import json; json.dump(rows,open('listrows.json','w'))
