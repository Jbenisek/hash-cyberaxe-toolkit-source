import sys, json
from math import log2
sys.argv=['x']
import ledger_new as L
import frontline as F
rows=json.load(open('listrows.json'))
cnt={}
for t in (0,1):
    st,p16,dead=F.level16(t); cnt[t]={s:st.count(s) for s in set(st)}
# weight: a live block of type t (members half/half), class uniform, state by live low-half share
num=0;den=0;num_w=0;num_n=0
for t,cls,s2,w,n2,n in rows:
    wt=cnt[t][s2]
    den+=wt; num+=wt*(2*((1<<17)+1)+6*n2); num_w+=wt*w
cost_prefix_plus_list=num/den
print('weighted mean rebuild-from-typed cost per live block (units): %.1f (prefix %d + 6*entries %.1f)'%(cost_prefix_plus_list,2*((1<<17)+1),cost_prefix_plus_list-2*((1<<17)+1)))
def res(c,extra=0):
    r=L.ledger(c); N=r['N']+extra
    return N, L.certificate(N)
N0,k0=res(L.NEW); print('shipped N',N0,'time',(k0+1)/1e4,'log2(N/430)=%.8f'%log2(N0/430))
live_b=L.ledger(L.NEW)['LIVE_B']; print('LIVE_B',live_b,'log2 %.4f'%log2(live_b), 'RUN_CONTEXTS log2 %.4f'%log2(L.RUN_CONTEXTS))
out={}
def rep(name,N,k,mem_words):
    tl=(k+1)/1e4
    print('%-34s time_log2 %.4f  (dT vs shipped %+.5f)  list words %d = %d B = 2^%.3f B'%(name,tl,log2(N/N0),mem_words,32*mem_words,log2(32*mem_words)))
    out[name]=(tl,log2(N/N0),mem_words)
W_ship=160506+12583008
rep('V0 shipped (96 lists, 1 word/prefix)',N0,k0,W_ship)
# V1 typed lists
c=dict(L.NEW); c.update(e_count=L.E_COUNT,u_member=68,build=0)
N1,k1=res(c); rep('V1 typed lists only (12 lists)',N1,k1,12*((1<<17)+1)+23823)
# V1b typed, but keep BUILD
# V2 recompute class list per live block from typed lists
ex=int(live_b*cost_prefix_plus_list)
N2,k2=res(L.NEW,ex); rep('V2 rebuild list per live block (from typed)',N2,k2,12*((1<<17)+1)+23823)
# V3 DFS from scratch per live block
ex3=live_b*(L.BUILD//96)
N3,k3=res(L.NEW,ex3); rep('V3 DFS-from-scratch per live block',N3,k3,12*((1<<17)+1)+23823)
print('per-list DFS build units',L.BUILD//96,'log2 %.3f'%log2(L.BUILD/96))
# breakeven: max cost per live block that keeps time unchanged within 0.001 bit
print('cost per live block that adds 0.01 bit: %.1f units'%((2**0.01-1)*N0/live_b))
print('cost per live block that adds 1 bit: %.3e units'%(N0/live_b))
# S terms
for tag,Bl in (('declared 2^60',60.0),('search-only 2^42.001',42.001)):
    for nm,(tl,d,mw) in out.items():
        print(tag,nm,'S=%.4f'%(tl+Bl-20))
# marginal memory term of lists vs search bytes
lb=32*W_ship
print('lists/2^42.001 B ratio %.3e ; log2(1+ratio)=%.3e'%(lb/2**42.001, log2(1+lb/2**42.001)))
print('lists/2^60 ratio %.3e'%(lb/2**60))
tb=32*(12*((1<<17)+1)+23823)
print('typed bytes',tb,'saving bytes',lb-tb,'dS_mem (search-only base) %.3e'%(log2((2**42.001)/(2**42.001-(lb-tb)))))
# what fits 2^20 B
print('2^20 B =',2**20//32,'words; shipped lists words/ (2^15)=%.1f'%(W_ship/2**15), '; list words only (no prefix) undeduped',160506,'distinct 42090 typed 23823')
json.dump(out,open('mvar.json','w'))
