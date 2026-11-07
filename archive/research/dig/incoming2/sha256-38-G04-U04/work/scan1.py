# G04-U04 scan 1: validation on the published pair, exact G, F7, class table of G (own code; reuses our a0lean38 reference functions)
import sys, time, numpy as np, json
sys.setrecursionlimit(10000)
import a0lean38 as L
M=L.M
out={}
# ---- 1 validation on the published pair
cvx=L.compress(L.PCV,L.PMX); cvy=L.compress(L.PCV,L.PMY)
out['pair_digest_equal']= cvx==cvy
tx=L._tx; ty=L._ty
rows_ok=all(L.rowok(tx,ty,i) for i in range(0,38) if i<34) 
out['pair_rows_ok_0_33']=rows_ok
out['pair_exact_34_37']=L.exact(tx,ty)
# Lemma 4.1 rebuild: from cv and a0=published A0 reproduce W0..W13 of both members
wx,wy=L.words_from_cv(L.PCV,L.SAx[0])
out['lemma41_rebuild_x']= wx==L.PMX[:14]; out['lemma41_rebuild_y']= wy==L.PMY[:14]
out['pub_a0_in_G']=L.in_G(L.SAx[0]); out['pub_c7']=hex(L.c7of(L.SAx[0])); out['pub_in_F7_W7x']=L.inF7(L.PMX[7])
print(out)
# ---- 2 exact G by enumerating w=W8x over 2^32
m,v,df=L.CELLS[2][8][:3]; D8=L.D8
t=time.time()
ws=[]
CH_=1<<24
for c in range(1<<8):
    w=(np.arange(CH_,dtype=np.uint64)+np.uint64(c<<24)).astype(np.uint32)
    y=w+np.uint32(D8)
    ok=((w&np.uint32(m))==np.uint32(v))&((w^y)==np.uint32(df))
    b=lambda k:(w>>np.uint32(k))&np.uint32(1)
    ok&=(b(0)!=b(28))&(b(30)!=b(9))&(b(1)==b(18))
    ws.append(w[ok])
W=np.concatenate(ws); print('G size',len(W),time.time()-t)
out['G_size']=int(len(W))
a0=(np.uint32(L.W8C)-W-np.uint32(L.C4))   # uint32 wrap
a0=a0.astype(np.uint32)
# check vs in_G on samples
import random
smp=random.sample(range(len(a0)),2000)
out['inG_agrees_2000']=all(L.in_G(int(a0[i])) for i in smp)
# F7 count
t=time.time()
cnt=0
def ror(x,n): return (x>>np.uint32(n))|(x<<np.uint32(32-n))
def s0v(x): return ror(x,7)^ror(x,18)^(x>>np.uint32(3))
for c in range(1<<8):
    w=(np.arange(CH_,dtype=np.uint64)+np.uint64(c<<24)).astype(np.uint32)
    cnt+=int((((s0v(w+np.uint32(L.D7))-s0v(w))==np.uint32(L.T7))).sum())
print('F7',cnt,time.time()-t); out['F7_size']=cnt
# c7 for all G
def S0v(x): return ror(x,2)^ror(x,13)^ror(x,22)
def S1v(x): return ror(x,6)^ror(x,11)^ror(x,25)
def CHv(x,y,z): return (x&y)^(~x&z)
def MAJv(x,y,z): return (x&y)|(z&(x|y))
u=np.uint32
e4=a0+u(L.C4)
c7=(u(L.SE[7])-u(2*L.SAx[3]&M)+u(L.S0(L.SAx[2]))+MAJv(u(L.SAx[2]),u(L.SAx[1]),a0)-u(L.S1(L.SE[6]))-CHv(u(L.SE[6]),u(L.SE[5]),e4)-u(L.K[7]))
for i in smp[:200]: assert int(c7[i])==L.c7of(int(a0[i]))
np.save('G_a0.npy',a0); np.save('G_c7.npy',c7)
uc,inv,cn=np.unique(c7,return_inverse=True,return_counts=True)
out['n_c7_classes']=int(len(uc)); 
sizes,freq=np.unique(cn,return_counts=True)
out['class_size_hist']={int(s):int(f) for s,f in zip(sizes,freq)}
print(out['n_c7_classes'],'max',sizes.max())
big=sorted(out['class_size_hist'].items(),reverse=True)[:12]; print('top sizes',big)
# distinct W0..W5? injectivity trivially: W0 = bijective in a0. check class table
cls_c7=[c[0] for c in L.CLASSES]
out['K']=len(cls_c7); out['K_distinct_c7']=len(set(cls_c7))
cmap=dict(zip(uc.tolist(),cn.tolist()))
out['chosen_class_full_G_sizes']=sorted(set(cmap.get(c,0) for c in cls_c7))
out['n_size3840_classes_in_G']=int((cn==3840).sum())
out['chosen_in_size3840']=all(cmap.get(c)==3840 for c in cls_c7)
# members as filed vs full class of c7 in G
cnt_ok=0
for (c,b,mk) in L.CLASSES[:6]:
    mem=L.class_members(c,b,mk); full=set(a0[c7==u(c)].tolist()); cnt_ok+= (set(mem)==full)
out['first6_filed_members_equal_full_G_class']=cnt_ok
json.dump(out,open('scan1.json','w'),indent=1)
print(json.dumps(out)[:3000])
