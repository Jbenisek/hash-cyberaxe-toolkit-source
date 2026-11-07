"""r39 joint (sha256-r39-prefix-v1). Credits: sraiw 38912d66, dariolina."""
import sys,os,json,random,time,hashlib
M=0xFFFFFFFF
K=[int(x,16)for x in """428a2f98 71374491 b5c0fbcf e9b5dba5 3956c25b 59f111f1 923f82a4 ab1c5ed5 d807aa98 12835b01 243185be 550c7dc3 72be5d74 80deb1fe 9bdc06a7 c19bf174 e49b69c1 efbe4786 0fc19dc6 240ca1cc 2de92c6f 4a7484aa 5cb0a9dc 76f988da 983e5152 a831c66d b00327c8 bf597fc7 c6e00bf3 d5a79147 06ca6351 14292967 27b70a85 2e1b2138 4d2c6dfc 53380d13 650a7354 766a0abb 81c2c92e""".split()]
IV=[0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19]
def ror(x,k):return((x>>k)|(x<<(32-k)))&M
def S0(x):return ror(x,2)^ror(x,13)^ror(x,22)
def S1(x):return ror(x,6)^ror(x,11)^ror(x,25)
def s0(x):return ror(x,7)^ror(x,18)^(x>>3)
def s1(x):return ror(x,17)^ror(x,19)^(x>>10)
def CH(e,f,g):return(e&f)^(~e&g&M)
def MAJ(a,b,c):return(a&b)^(a&c)^(b&c)
H=lambda s:[int(x,16)for x in s.split()]
CV_PUB=H("7af4aafd 1ce952e1 fe23c538 9f5d03c0 b5bd1df7 cc439008 83129864 e87f95fe")
M_PUB=H("2f5ec45a afb37096 9c936264 5ea06c00 67931754 54921569 475dcabb 327b8f77 648b7246 402cfb89 080047f4 3067a77a 778d09df 302606d1 4367003c d80d9523")
MP_PUB=H("2f5ec45a afb37096 9c936264 5ea06c00 67931754 54921569 475dcabb 327b8f77 248b7246 48aceb89 480047f4 2a65caa6 779d21df 302606d1 4367003c d80d9523")
ADVICE_BYTES=4*(8+16+16)
def expand(w,n=39):
  w=list(w)
  for i in range(16,n):w.append((w[i-16]+s0(w[i-15])+w[i-7]+s1(w[i-2]))&M)
  return w
def traj(cv,w16,n=39):
  w=expand(w16,n)
  A=[cv[3],cv[2],cv[1],cv[0]];E=[cv[7],cv[6],cv[5],cv[4]]
  for r in range(n):
    a,b,c,d=A[r+3],A[r+2],A[r+1],A[r]
    e,f,g,h=E[r+3],E[r+2],E[r+1],E[r]
    t1=(h+S1(e)+CH(e,f,g)+K[r]+w[r])&M
    t2=(S0(a)+MAJ(a,b,c))&M
    A.append((t1+t2)&M);E.append((d+t1)&M)
  return A,E,w
def compress(cv,w16,n=39):
  A,E,_=traj(cv,w16,n)
  st=[A[n+3],A[n+2],A[n+1],A[n],E[n+3],E[n+2],E[n+1],E[n]]
  return[(st[i]+cv[i])&M for i in range(8)]
BA,BE,BW=traj(CV_PUB,MP_PUB)[0],traj(CV_PUB,MP_PUB)[1],MP_PUB
CA,CE,CW_=traj(CV_PUB,M_PUB)[0],traj(CV_PUB,M_PUB)[1],M_PUB
Wp_,Wq_=expand(MP_PUB),expand(M_PUB)
G16=Wp_[16]
W17PUB=Wp_[17]
D8=(M_PUB[8]-MP_PUB[8])&M
D9=(M_PUB[9]-MP_PUB[9])&M
T8,T9=0x087FF000,0x03010000
def inF(w,D,T):return((s0((w+D)&M)-s0(w))&M)==T
def consts(cv):
  t20=(S0(cv[0])+MAJ(cv[0],cv[1],cv[2]))&M
  eb=(cv[3]-t20)&M
  k0=(-t20-cv[7]-S1(cv[4])-CH(cv[4],cv[5],cv[6])-K[0])&M
  c9=(BW[9]+BA[5])&M
  cw=(G16-s1(BW[14])-c9-k0+cv[6]+K[1])&M
  return(cw,eb,cv[0],cv[1],cv[4],cv[5])
def fstep(x,c):
  if x&1:return(s0(x)-x)&M
  cw,eb,cv0,cv1,cv4,cv5=c
  e0=(x+eb)&M
  return(cw+S0(x)+MAJ(x,cv0,cv1)+S1(e0)+CH(e0,cv4,cv5)-x)&M
def recover_a1(cv,a0,u):
  t20=(S0(cv[0])+MAJ(cv[0],cv[1],cv[2]))&M
  e0=(cv[3]+a0-t20)&M
  return(u+S0(a0)+MAJ(a0,cv[0],cv[1])+S1(e0)+CH(e0,cv[4],cv[5])+cv[6]+K[1])&M
def build(cv,a0,a1):
  A=[cv[3],cv[2],cv[1],cv[0],a0,a1,BA[6],BA[7],BA[8],BA[9]]
  E=[cv[7],cv[6],cv[5],cv[4]]+[None]*6
  W=[None]*16
  for r in range(6):
    a,b,c=A[r+3],A[r+2],A[r+1]
    t2=(S0(a)+MAJ(a,b,c))&M
    t1=(A[r+4]-t2)&M
    e,f,g,h=E[r+3],E[r+2],E[r+1],E[r]
    W[r]=(t1-h-S1(e)-CH(e,f,g)-K[r])&M
    E[r+4]=(A[r]+t1)&M
  A+=[BA[10],BA[11],BA[12],BA[13]]
  E+=[None]*4
  for k in range(10,14):E[k]=BE[k]
  for r in range(6,10):
    e,f,g,h=E[r+3],E[r+2],E[r+1],E[r]
    t1=(E[r+4]-A[r])&M
    W[r]=(t1-h-S1(e)-CH(e,f,g)-K[r])&M
  for r in range(10,16):W[r]=BW[r]
  return W
def second(W):
  V=list(W)
  V[8]=(W[8]+D8)&M;V[9]=(W[9]+D9)&M
  for r in range(10,16):V[r]=M_PUB[r]
  return V
def claw_pair(cv,a0,u):
  a1=recover_a1(cv,a0,u)
  W=build(cv,a0,a1)
  return W,second(W)
ROW_MASKS_16_17={16:(0x05010000,0x04010000,0x00000100,0,0x08801000,0x08800000),17:(0,0,0x80829C01,0x00029C00,0x40000000,0x40000000)}
_C1617=(14195250,7866380,13109778,8915986,4460562,530956,1580562,2110988,13675058,9183762,6293010,7342604,3684364,14989364,14956556,11568690,15875084,163880,11085388,7416402,8467020,9515602,5411890,10566220,5936680,6461490,80972,8035890,9085490,2163794,12234280,21570,23620,16432690,10028114,5324364,15270476,13143091,13667885,15769645,2755085,9476659,4493365,4329491,1091635,2141229,2663469,8658963,9052691,15249459,9577485,15774259,6861869,7386669,571443,1621043,12857363,9472045,9996851,13906963,14858293,14825491,4753459,12618291,11090003,12124237,3738189,15875091,7939667,13701709,6882381)
CONDS_16_17=tuple((16+(v&1),(((v>>5)&3,16+(v&1)-((v>>7)&3),(v>>9)&31),)+(()if(v>>14)&1 else(((v>>15)&3,16+(v&1)-((v>>17)&3),(v>>19)&31),)),(v>>1)&15)for v in _C1617)
def _build_by_bit():
  ex=list(CONDS_16_17)
  for _ in range(4):
    cs=set(ex)
    for kr1,t1,a1 in list(ex):
      for kr2,t2,a2 in list(ex):
        if kr1!=kr2 or len(t2)!=2 or a2 not in(6,9):continue
        for x,y in((t2[0],t2[1]),(t2[1],t2[0])):
          if len(t1)==2 and a1 in(6,9):
            for u,v in((t1[0],t1[1]),(t1[1],t1[0])):
              if v==x and u!=y and(kr1,(u,y),9 if a1==a2 else 6)not in cs:
                nc=(kr1,(u,y),9 if a1==a2 else 6);cs.add(nc);ex.append(nc)
          elif len(t1)==1 and t1[0]==x:
            nc=(kr1,(y,),a1 if a2==9 else(3^a1))
            if nc not in cs:cs.add(nc);ex.append(nc)
  bb={16:[[]for _ in range(32)],17:[[]for _ in range(32)]}
  for kr,terms,allowed in ex:bb[kr][max(b for _,rw,b in terms if rw==kr)].append((terms,allowed))
  return bb
BY_BIT_16_17=_build_by_bit()
def solve_row_exact(A0,E0,W0,A1,E1,W1,r):
  ma_r,sa_r,me_r,se_r,mw_r,sw_r=ROW_MASKS_16_17[r]
  dsch=((s1(W1[r-2])+W1[r-7]+s0(W1[r-15]))-(s1(W0[r-2])+W0[r-7]+s0(W0[r-15])))&M
  idx=r+4
  t10=(E0[idx-4]+S1(E0[idx-1])+CH(E0[idx-1],E0[idx-2],E0[idx-3])+K[r])&M
  t11=(E1[idx-4]+S1(E1[idx-1])+CH(E1[idx-1],E1[idx-2],E1[idx-3])+K[r])&M
  t20=(S0(A0[idx-1])+MAJ(A0[idx-1],A0[idx-2],A0[idx-3]))&M
  t21=(S0(A1[idx-1])+MAJ(A1[idx-1],A1[idx-2],A1[idx-3]))&M
  ce0,ce1,ca0,ca1=(A0[idx-4]+t10)&M,(A1[idx-4]+t11+dsch)&M,(t10+t20)&M,(t11+t21+dsch)&M
  by_bit=BY_BIT_16_17[r];out=[];steps=[0]
  def dfs(b,w_low):
    if b==32:out.append(w_low);return
    steps[0]+=1
    mw,sw,me,se,ma,sa=(mw_r>>b)&1,(sw_r>>b)&1,(me_r>>b)&1,(se_r>>b)&1,(ma_r>>b)&1,(sa_r>>b)&1
    for bit in(0,1):
      w=w_low|(bit<<b);wx1=((w+dsch)>>b)&1
      if(bit^wx1)!=mw or(bit&mw)!=sw:continue
      ex_f=(ce0+w)&M;ex0,ex1=(ex_f>>b)&1,((ce1+w)>>b)&1
      if(ex0^ex1)!=me or(ex0&me)!=se:continue
      ax_f=(ca0+w)&M;ax0,ax1=(ax_f>>b)&1,((ca1+w)>>b)&1
      if(ax0^ax1)!=ma or(ax0&ma)!=sa:continue
      ok=True
      for terms,allowed in by_bit[b]:
        cidx=0
        for q,(kind,rw,cb)in enumerate(terms):
          wd=(w if kind==2 else(ex_f if kind==1 else ax_f))if rw==r else(W0[rw]if kind==2 else(E0[rw+4]if kind==1 else A0[rw+4]))
          cidx|=((wd>>cb)&1)<<q
        if not((allowed>>cidx)&1):ok=False;break
      if ok:dfs(b+1,w)
  dfs(0,0)
  return out,steps[0]
def invert_downward(A_top,E_top,W):
  A=[0]*14+list(A_top);E=[0]*14+list(E_top)
  for r in range(13,-1,-1):
    t2=(S0(A[r+3])+MAJ(A[r+3],A[r+2],A[r+1]))&M;t1=(A[r+4]-t2)&M
    A[r]=(E[r+4]-t1)&M;E[r]=(t1-S1(E[r+3])-CH(E[r+3],E[r+2],E[r+1])-K[r]-W[r])&M
  return[A[3],A[2],A[1],A[0],E[3],E[2],E[1],E[0]],A,E
def verify_advice_construction():
  cv0,A0_i,E0_i=invert_downward(BA[14:20],BE[14:20],MP_PUB)
  cv1,A1_i,E1_i=invert_downward(CA[14:20],CE[14:20],M_PUB)
  inv_ok=int(cv0==CV_PUB and cv1==CV_PUB and A0_i==BA[:20]and E0_i==BE[:20]and A1_i==CA[:20]and E1_i==CE[:20])
  sbits=(1,2,3,9,12,13,14,19);e0_15,e1_15,a0_15,a1_15=BE[19],CE[19],BA[19],CA[19]
  me_15,se_15,ma_15,sa_15=e0_15^e1_15,e0_15&(e0_15^e1_15),a0_15^a1_15,a0_15&(a0_15^a1_15)
  dsch16=((s1(M_PUB[14])+M_PUB[9]+s0(M_PUB[1]))-(s1(MP_PUB[14])+MP_PUB[9]+s0(MP_PUB[1])))&M
  hits=tot_steps=g16_sz=g17_sz=base_ops=0
  for idx in range(256):
    w15=MP_PUB[15]^sum(((idx>>k)&1)<<sbits[k]for k in range(8));dw=(w15-MP_PUB[15])&M
    ne0,ne1,na0,na1=(e0_15+dw)&M,(e1_15+dw)&M,(a0_15+dw)&M,(a1_15+dw)&M
    if(ne0^ne1)!=me_15 or(ne0&me_15)!=se_15 or(na0^na1)!=ma_15 or(na0&ma_15)!=sa_15:continue
    A0,E0,W0=BA[:19]+[na0],BE[:19]+[ne0],MP_PUB[:15]+[w15]
    A1,E1,W1=CA[:19]+[na1],CE[:19]+[ne1],M_PUB[:15]+[w15]
    g16,s16=solve_row_exact(A0,E0,W0,A1,E1,W1,16);tot_steps+=s16
    if idx==0:g16_sz=len(g16);assert G16 in g16
    for g in g16:
      w16_0,w16_1=g,(g+dsch16)&M
      t10=(E0[16]+S1(E0[19])+CH(E0[19],E0[18],E0[17])+K[16]+w16_0)&M;t20=(S0(A0[19])+MAJ(A0[19],A0[18],A0[17]))&M
      t11=(E1[16]+S1(E1[19])+CH(E1[19],E1[18],E1[17])+K[16]+w16_1)&M;t21=(S0(A1[19])+MAJ(A1[19],A1[18],A1[17]))&M
      g17,s17=solve_row_exact(A0+[(t10+t20)&M],E0+[(A0[16]+t10)&M],W0+[w16_0],
      A1+[(t11+t21)&M],E1+[(A1[16]+t11)&M],W1+[w16_1],17)
      tot_steps+=s17
      if idx==0 and g==G16:g17_sz=len(g17);base_ops=(s16+s17)*6;assert g17==[W17PUB]
      if g17:hits+=1
  return{"g16_fibre_size":g16_sz,"g17_fibre_size":g17_sz,"fibre_dfs_ops":base_ops,"downward_inv_ok":inv_ok,
  "advice_slice_cands":256,"advice_slice_hits":hits,"ops_per_cand":(288*256+16*tot_steps)//256}
def count_groups(dset):
  pa={}
  def fd(x):
    while pa[x]!=x:pa[x]=pa[pa[x]];x=pa[x]
    return x
  for _,a0,u in dset:
    ka,ku=(0,a0),(1,u);pa.setdefault(ka,ka);pa.setdefault(ku,ku);ra,ru=fd(ka),fd(ku)
    if ra!=ru:pa[ra]=ru
  return sum(1 for x in pa if pa[x]==x)
XOR,AND,OR,NOT=0,1,2,3
ONES=(1<<256)-1
class Gen:
  def __init__(s,nin):
    s.nin=nin;s.recs=[]
  def g(s,op,a,b=None):
    s.recs.append((op,a,b));return s.nin+len(s.recs)-1
  def X(s,a,b):
    if a[0]<0 and b[0]<0:return(-1,a[1]^b[1])
    if a[0]<0:return(b[0],b[1]^a[1])
    if b[0]<0:return(a[0],a[1]^b[1])
    if a[0]==b[0]:return(-1,a[1]^b[1])
    return(s.g(XOR,a[0],b[0]),a[1]^b[1])
  def NOTm(s,a):
    return(s.g(NOT,a[0]),0)
  def A(s,a,b,orr=False):
    if a[0]<0 or b[0]<0:
      if a[0]<0:a,b=b,a
      if(b[1]==0)!=orr:return(-1,0 if not orr else 1)
      return a
    if a[0]==b[0]:
      return a if a[1]==b[1]else(-1,1 if orr else 0)
    if a[1]==b[1]:
      if a[1]==0:return(s.g(OR if orr else AND,a[0],b[0]),0)
      return(s.g(AND if orr else OR,a[0],b[0]),1)
    if a[1]==1:a,b=b,a
    return(s.g(OR if orr else AND,a[0],s.g(NOT,b[0])),0)
  def O(s,a,b):return s.A(a,b,True)
  def full(s,a,b,c,ncy=True):
    cs=[t for t in(a,b,c)if t[0]<0];vs=[t for t in(a,b,c)if t[0]>=0]
    if len(cs)==0:
      pol=[a[1],b[1],c[1]]
      if pol[0]==pol[1]==pol[2]:p,x,y=c,a,b
      else:
        i=[k for k in range(3)if pol.count(pol[k])==1][0]
        p=(a,b,c)[i];x,y=[t for k,t in enumerate((a,b,c))if k!=i]
      u=s.X(x,p);sm=s.X(u,y)
      if not ncy:return sm,Z0
      return sm,s.X(s.A(u,s.X(y,p)),p)
    if len(cs)==1:
      x,y=vs;k=cs[0];t=s.X(x,y);p=x if x[1]==k[1]else y;sm=s.X(t,k)
      if not ncy:return sm,Z0
      if x[1]!=y[1]:return sm,(s.O(p,t)if k[1]else s.A(p,(t[0],0)))
      return sm,(s.O(x,y)if k[1]else s.A(x,y))
    if len(cs)==2:
      k=cs[0][1]^cs[1][1];x=vs[0]
      return s.X(x,(-1,k)),(x if cs[0][1]!=cs[1][1]else(-1,cs[0][1]))
    return(-1,sum(t[1]for t in cs)&1),(-1,1 if sum(t[1]for t in cs)>=2 else 0)
Z0=(-1,0);O1=(-1,1)
NREG_FIXED=224
DPREG=224
def allocate(g,out,acc,dst_bank,dpreg=None,nfixed=None):
  nin=g.nin;dpreg=DPREG if dpreg is None else dpreg;nfixed=NREG_FIXED if nfixed is None else nfixed
  outs=[]
  for j in range(32):
    node,pol=out[j];assert node>=0
    if pol:node=g.g(NOT,node)
    outs.append(node)
  accn=acc[0];assert accn>=0
  recs=g.recs;last={}
  for i,(op,a,b)in enumerate(recs):
    for t in(a,b):
      if t is not None:last[t]=nin+i
  forced={outs[j]:dst_bank*32+j for j in range(32)};forced[accn]=dpreg
  for t in list(forced):last[t]=1<<60
  reg={i:i for i in range(nin)};free=[];nxt=nfixed+1;res=[]
  for i,(op,a,b)in enumerate(recs):
    nid=nin+i;dying=[]
    for t in(a,b):
      if t is not None and t>=nin and last.get(t)==nid and t not in dying:dying.append(t)
    if nid in forced:d=forced[nid]
    elif dying:d=reg[dying[0]];dying=dying[1:]
    elif free:free.sort();d=free.pop(0)
    else:d=nxt;nxt+=1
    for t in dying:free.append(reg[t])
    reg[nid]=d
    res.append((op,d,reg[a],reg[b]if b is not None else 0))
  return res,acc[1],nxt
def to_source(recs,name,dpreg=None):
  dpreg=DPREG if dpreg is None else dpreg
  L=["def %s(R):"%name];ins=set();defined=set()
  for op,d,a,b in recs:
    for t in(a,b):
      if t not in defined:ins.add(t)
    defined.add(d)
  for t in sorted(ins):L.append(" r%d=R[%d]"%(t,t))
  sym={XOR:"^",AND:"&",OR:"|"}
  for op,d,a,b in recs:
    if op==NOT:L.append(" r%d=r%d^M"%(d,a))
    else:L.append(" r%d=r%d%sr%d"%(d,a,sym[op],b))
  for d in sorted({d for _,d,_,_ in recs if d<64 or d==dpreg}):L.append(" R[%d]=r%d"%(d,d))
  return "\n".join(L)
def build_folded(consts5,src_bank,dst_bank,dpb):
  cw,eb,P,R,G=consts5;g=Gen(65)
  x=[(src_bank*32+j,0)for j in range(32)];nx0=g.NOTm(x[0])
  def x0p(p):return(nx0[0],1)if p else x[0]
  def mux0(od,ev,wp=-1):
    if od==ev:return od
    if ev[0]<0:return g.A(od,(x0p(od[1]^ev[1])[0],x0p(od[1]^ev[1])[1]^ev[1]),bool(ev[1]))
    if od[0]<0:
      no=1-od[1]
      return g.A(ev,(x0p(ev[1]^no)[0],x0p(ev[1]^no)[1]^no),bool(od[1]))
    y=g.X(od,ev);uo=(wp!=od[1])if(wp>=0 and od[1]!=ev[1])else(y[1]==1)
    return g.X(od if uo else ev,g.A((x0p(y[1]^int(uo))[0],x0p(y[1]^int(uo))[1]^int(uo)),y))
  xe=[Z0]+x[1:];u=[None]*32;e0=[None]*32;cy=Z0
  for j in range(32):
    u[j]=g.X(xe[j],xe[(j+11)&31])
    e0[j],cy=g.full(xe[j],(-1,(eb>>j)&1),cy,j<31)
  cwe=(cw+P+1+(G&~R&~1)+(((eb^G)&1)if(R&1)else(G&1))+((~P)&1))&0xFFFFFFFF
  nxtb=[];res=[None]*32;cy=Z0
  for j in range(32):
    k7=(j+7)&31
    uoj=g.X(u[k7],O1)if k7 in(0,21)else u[k7]
    od=g.X(uoj,x[j+3]if j+3<32 else Z0);b=[]
    if(cwe>>j)&1:b.append(O1)
    b.extend(nxtb)
    if j>0 and((R>>j)&1):b.append(g.X(e0[j],(-1,(G>>j)&1)))
    b.append(g.X(u[(j+2)&31],xe[(j+22)&31]))
    b.append(g.X(g.X(e0[(j+6)&31],e0[(j+11)&31]),e0[(j+25)&31]))
    nxtb=[];hnx=(j>0 and not((P>>j)&1));tgt=1 if(j==0 or hnx)else 2
    while len(b)>tgt:
      take=2 if len(b)==tgt+1 else 3
      sm,c2=g.full(b[0],b[1],b[2]if take==3 else Z0,j<31);b=b[take:]
      if sm!=Z0:b.append(sm)
      if j<31 and c2!=Z0:nxtb.append(c2)
    if not hnx and len(b)==2 and od[1]==0 and b[0][1]==0 and b[1][1]==1:b[0],b[1]=b[1],b[0]
    sev=b[0]if len(b)>=1 else Z0
    cev=Z0 if j==0 else((x[j][0],1)if hnx else(b[1]if len(b)>=2 else Z0))
    if j==0:
      res[0]=mux0((od[0],od[1]^1),sev,0);cy=g.A(od,x0p(od[1]))
    else:
      nxj=(x[j][0],1)
      if cev[0]>=0 and cev[1]==0:
        aj=mux0(od,sev,cy[1]);bj=mux0(nxj,cev,aj[1]^cy[1])
      else:
        bj=mux0(nxj,cev,-1);aj=mux0(od,sev,bj[1]^cy[1])
      res[j],cy=g.full(aj,bj,cy,j<31)
    if res[j][1]:res[j]=g.NOTm(res[j])
  acc=res[0]
  for j in range(1,dpb):acc=g.O(acc,res[j])
  return g,res,acc
def consts5(c):
  cw,eb,cv0,cv1,cv4,cv5=c
  return((cw+(cv0&cv1))&0xFFFFFFFF,eb,cv0^cv1,cv4^cv5,cv5)
def make_kernels_folded(c,dpb):
  ks=[]
  for src,dst in((0,1),(1,0)):
    g,out,acc=build_folded(consts5(c),src,dst,dpb)
    recs,dppol,nreg=allocate(g,out,acc,dst,dpreg=64,nfixed=64)
    ns={"M":ONES};exec(to_source(recs,"k",dpreg=64),ns)
    ks.append(dict(recs=recs,dppol=dppol,nreg=nreg,fn=ns["k"],
    counts={o:sum(1 for r in recs if r[0]==o)for o in range(4)}))
  return ks
GEN_C=r'''// r39 joint, Lane A: the in-program GENERATOR of the folded 256-lane walk step, compact version (freestanding C, no libc, no malloc).
#include <stdint.h>
#define MAXN 1200
typedef int S;
static int nin, nrec, nreg_, dppol_, x0, nx0, gcy, outn[32];
static uint8_t gop[MAXN], isfree[400];
static int16_t ga[MAXN], gb[MAXN], last[MAXN], regof[MAXN], forced[MAXN];
static S u[32], e0[32], res[32], b[16], nxtb[8];
#define NN(s) ((s) >> 1)
#define PL(s) ((s) & 1)
static S K(int v) { return v - 2; }
static S xe(int j) { return j ? x0 + j * 2 : K(0); }
static int emit(int op, int a, int b) { gop[nrec] = op; ga[nrec] = a; gb[nrec] = b; return nin + nrec++; }
static S X(S a, S b) {
  int na = NN(a), nb = NN(b);
  if (na < 0 && nb < 0) return K(PL(a) ^ PL(b));
  if (na < 0) return b ^ PL(a);
  if (nb < 0) return a ^ PL(b);
  if (na == nb) return K(PL(a) ^ PL(b));
  return emit(0, na, nb) * 2 + (PL(a) ^ PL(b));
}
static S AO(S a, S b, int orr) {
  if (NN(a) < 0 || NN(b) < 0) { if (NN(a) < 0) { S t = a; a = b; b = t; } return ((PL(b) == 0) != (orr != 0)) ? K(orr) : a; }
  if (NN(a) == NN(b)) return PL(a) == PL(b) ? a : K(orr);
  if (PL(a) == PL(b)) return emit((PL(a) ? !orr : orr) ? 2 : 1, NN(a), NN(b)) * 2 + PL(a);
  if (PL(a)) { S t = a; a = b; b = t; }
  return emit(orr ? 2 : 1, NN(a), emit(3, NN(b), 0)) * 2;
}
static S full(S a, S b, S c, int ncy) {
  if (NN(a) < 0) { S t = a; a = b; b = c; c = t; }
  if (NN(a) < 0) { S t = a; a = b; b = c; c = t; }
  if (NN(b) < 0) { S t = b; b = c; c = t; }
  if (NN(c) >= 0) {
    if (PL(a) != PL(b)) { if (PL(a) == PL(c)) { S t = b; b = c; c = t; } else { S t = a; a = b; b = c; c = t; } }
    S u1 = X(a, c), sm = X(u1, b);
    gcy = ncy ? X(AO(u1, X(b, c), 0), c) : K(0);
    return sm;
  } else if (NN(b) >= 0) {
    S t = X(a, b), p = (PL(a) == PL(c)) ? a : b, sm = X(t, c);
    gcy = !ncy ? K(0) : (PL(a) != PL(b)) ? AO(p, PL(c) ? t : (t & ~1), PL(c)) : AO(a, b, PL(c));
    return sm;
  } else if (NN(a) >= 0) { gcy = (PL(b) != PL(c)) ? a : K(PL(b)); return X(a, K(PL(b) ^ PL(c))); }
  else { int s = PL(a) + PL(b) + PL(c); gcy = K(s >= 2); return K(s & 1); }
}
static S x0p(int p) { return p ? (nx0 | 1) : x0; }
static S mux0(S od, S ev, int wp) {
  if (od == ev) return od;
  if (NN(ev) < 0) return AO(od, x0p(PL(od) ^ PL(ev)) ^ PL(ev), PL(ev));
  if (NN(od) < 0) return AO(ev, x0p(PL(ev) ^ !PL(od)) ^ !PL(od), PL(od));
  S y = X(od, ev);
  int uo_ = (wp >= 0 && PL(od) != PL(ev)) ? (wp != PL(od)) : PL(y);
  return X(uo_ ? od : ev, AO(x0p(PL(y) ^ uo_) ^ uo_, y, 0));
}
int gen(uint32_t cw, uint32_t eb, uint32_t P, uint32_t R, uint32_t G, int src, int dst, int dpb, uint8_t *out) {
  nin = 65; nrec = 0; x0 = src * 64;
  nx0 = emit(3, src * 32, 0) * 2;
  gcy = K(0);
  for (int j = 0; j < 32; j++) {
    u[j] = X(xe(j), xe((j + 11) & 31));
    e0[j] = full(xe(j), K((eb >> j) & 1), gcy, j < 31);
  }
  uint32_t cwe = cw + P + 1 + (G & ~R & ~1u) + ((R & 1) ? ((eb ^ G) & 1) : (G & 1)) + ((~P) & 1);
  int nnb = 0; S cy = K(0);
  for (int j = 0; j < 32; j++) {
    int k7 = (j + 7) & 31, nb = 0, hd = 0, xj = x0 + j * 2;
    S uoj = (k7 == 0 || k7 == 21) ? X(u[k7], K(1)) : u[k7];
    S od = X(uoj, j + 3 < 32 ? xj + 6 : K(0));
    if ((cwe >> j) & 1) b[nb++] = K(1);
    for (int i = 0; i < nnb; i++) b[nb++] = nxtb[i];
    if (j > 0 && ((R >> j) & 1)) b[nb++] = X(e0[j], K((G >> j) & 1));
    b[nb++] = X(u[(j + 2) & 31], xe((j + 22) & 31));
    b[nb++] = X(X(e0[(j + 6) & 31], e0[(j + 11) & 31]), e0[(j + 25) & 31]);
    nnb = 0;
    int hnx = (j > 0 && !((P >> j) & 1)), tgt = (j == 0 || hnx) ? 1 : 2;
    while (nb - hd > tgt) {
      int take = (nb - hd == tgt + 1) ? 2 : 3;
      S sm = full(b[hd], b[hd + 1], take == 3 ? b[hd + 2] : K(0), j < 31);
      hd += take;
      if (sm != K(0)) b[nb++] = sm;
      if (j < 31 && gcy != K(0)) nxtb[nnb++] = gcy;
    }
    int rem = nb - hd; S b0 = rem >= 1 ? b[hd] : K(0), b1 = rem >= 2 ? b[hd + 1] : K(0);
    if (!hnx && rem == 2 && !PL(od) && !PL(b0) && PL(b1)) { S t = b0; b0 = b1; b1 = t; }
    S sev = b0, cev = (j == 0) ? K(0) : hnx ? (xj ^ 1) : b1;
    if (j == 0) {
      res[0] = mux0(od ^ 1, sev, 0);
      cy = AO(od, x0p(PL(od)), 0);
    } else {
      S aj, bj, nxj = xj ^ 1;
      if (NN(cev) >= 0 && !PL(cev)) { aj = mux0(od, sev, PL(cy)); bj = mux0(nxj, cev, PL(aj) ^ PL(cy)); }
      else { bj = mux0(nxj, cev, -1); aj = mux0(od, sev, PL(bj) ^ PL(cy)); }
      res[j] = full(aj, bj, cy, j < 31); cy = gcy;
    }
    if (PL(res[j])) res[j] = emit(3, NN(res[j]), 0) * 2;
    outn[j] = NN(res[j]);
  }
  S acc = res[0];
  for (int j = 1; j < dpb; j++) acc = AO(acc, res[j], 1);
  int accn = NN(acc), total = nin + nrec;
  for (int i = 0; i < total; i++) { last[i] = -1; forced[i] = -1; if (i < nin) regof[i] = i; if (i < 400) isfree[i] = 0; }
  for (int i = 0; i < nrec; i++) { last[ga[i]] = nin + i; if (gop[i] != 3) last[gb[i]] = nin + i; }
  for (int j = 0; j < 32; j++) { forced[outn[j]] = dst * 32 + j; last[outn[j]] = 30000; }
  forced[accn] = 64; last[accn] = 30000;
  int nxt = 65;
  for (int i = 0; i < nrec; i++) {
    int nid = nin + i, a = ga[i], b_ = gop[i] != 3 ? gb[i] : -1, dy[2], nd = 0, d, k0 = 0;
    if (a >= nin && last[a] == nid) dy[nd++] = a;
    if (b_ >= nin && b_ != a && last[b_] == nid) dy[nd++] = b_;
    if (forced[nid] >= 0) d = forced[nid];
    else if (nd) { d = regof[dy[0]]; k0 = 1; }
    else { d = -1; for (int r = 65; r < nxt; r++) if (isfree[r]) { d = r; break; } if (d >= 0) isfree[d] = 0; else d = nxt++; }
    for (int k = k0; k < nd; k++) isfree[regof[dy[k]]] = 1;
    regof[nid] = d;
    uint32_t w = (uint32_t)d | ((uint32_t)regof[a] << 10) | ((uint32_t)(b_ >= 0 ? regof[b_] : 0) << 20);
    uint8_t *q = out + 5 * i;
    q[0] = gop[i]; q[1] = w; q[2] = w >> 8; q[3] = w >> 16; q[4] = w >> 24;
  }
  nreg_ = nxt; dppol_ = PL(acc);
  return nrec;
}
int g_nreg(void) { return nreg_; }
int g_dppol(void) { return dppol_; }
'''
class GW:
  FALLBACK=575000
  AVAILABLE=False
  try:
    import wasmtime as _wt
    if os.environ.get("R39_WASM"):
      _cfg=_wt.Config();_cfg.consume_fuel=True;_eng=_wt.Engine(_cfg);_mod=_wt.Module.from_file(_eng,os.environ["R39_WASM"]);AVAILABLE=True
  except Exception:
    AVAILABLE=False
  @staticmethod
  def run(c5,src=0,dst=1,dpb=7):
    st=GW._wt.Store(GW._eng);inst=GW._wt.Instance(st,GW._mod,[]);ex=inst.exports(st);st.set_fuel(10**12)
    n=ex["gen"](st,*c5,src,dst,dpb,32768);used=10**12-st.get_fuel();raw=ex["memory"].read(st,32768,32768+5*n);recs=[]
    for i in range(n):
      w=raw[5*i+1]|raw[5*i+2]<<8|raw[5*i+3]<<16|raw[5*i+4]<<24
      recs.append((raw[5*i],w&1023,(w>>10)&1023,(w>>20)&1023))
    return used,recs
  @staticmethod
  def ops(c5):return GW.run(c5)[0]if GW.AVAILABLE else GW.FALLBACK
ONES=(1<<256)-1
M32=M
M20,M31,M39=(1<<20)-1,(1<<31)-1,(1<<39)-1
M25=(1<<25)-1
DBG=False
HIGHMASK=[sum(1<<p for p in range(256)if(p>>k)&1)for k in range(8)]
C_LOG8=sum(r<<((1<<r)^5)for r in range(8))
LOW128=(1<<128)-1
class Mach:
  def __init__(s):s.o=0;s.cat={};s.blk={};s.nest=0
  def bs(s):return(s.o,s.nest)
  def be(s,name,b,sub=False):
    d=(s.o-b[0])-(s.nest-b[1])
    if sub:s.nest+=d-1;d-=1
    if d>s.blk.get(name,0):s.blk[name]=d
  def x(s,a,b):s.o+=1;return a^b
  def a(s,a,b):s.o+=1;return a&b
  def r(s,a,b):s.o+=1;return a|b
  def n(s,a):s.o+=1;return a^ONES
  def ad(s,a,b):s.o+=1;return(a+b)&ONES
  def sb(s,a,b):s.o+=1;return(a-b)&ONES
  def sl(s,a,k):s.o+=1;return(a<<k)&ONES
  def sr(s,a,k):s.o+=1;return a>>k
  def rl(s,a,k):s.o+=1;k%=256;return a if k==0 else((a<<k)|(a>>(256-k)))&ONES
  def rr(s,a,k):return s.rl(a,256-(k%256))
  def ne(s,a,b):s.o+=1;return 1 if a!=b else 0
  def jz(s,a):s.o+=2;return a==0
  def jnz(s,a):s.o+=2;return a!=0
  def jeq(s,a,b):s.o+=2;return a==b
  def jne(s,a,b):s.o+=2;return a!=b
  def jge(s,a,b):s.o+=2;return a>=b
  def ld(s,arr,i):s.o+=3;return arr[i]
  def st(s,arr,i,v):s.o+=3;arr[i]=v
  def mv(s):s.o+=1
  def tick(s,name,t0):
    d=s.o-t0
    s.cat[name]=s.cat.get(name,0)+d
  def blkmax(s,name,d):
    if d>s.blk.get(name,0):s.blk[name]=d
def mS0(m,v):
  d=m.r(v,m.sl(v,32));return m.a(m.x(m.x(m.sr(d,2),m.sr(d,13)),m.sr(d,22)),M32)
def mS1(m,v):
  d=m.r(v,m.sl(v,32));return m.a(m.x(m.x(m.sr(d,6),m.sr(d,11)),m.sr(d,25)),M32)
def ms0(m,v):
  d=m.r(v,m.sl(v,32));return m.a(m.x(m.x(m.sr(d,7),m.sr(d,18)),m.sr(v,3)),M32)
def mMAJ(m,a,b,c):return m.r(m.a(a,b),m.a(c,m.r(a,b)))
def mCH(m,e,f,g):return m.x(m.a(e,f),m.a(m.x(e,M32),g))
def a32(m,a,b):return m.a(m.ad(a,b),M32)
def s32(m,a,b):return m.a(m.sb(a,b),M32)
class P:
  DPB=7
  MAXS=1536
  CUTP=512
  LMIN=32
  WIN=1<<26
  KTRY=8
  QCAP,QFULL=3584,3328
  WHEEL=2048
  WDIG=((14,1),(13,1),(10,1),(8,1),(7,1),(6,1),(2,1))
  GCAP=575000
  RCAP=206
  KCAP=780
  CMP1=12
  D0,KRES=82,6
def table_words(wdig=P.WDIG):return sum(sg*(1<<k)for k,sg in wdig)
class Attack:
  def __init__(s,win=P.WIN,seed=1,check=False):
    s.m=Mach();s.win=win;s.check=check;s.dpreg=DPREG;s.W=table_words()
    s.ks=None;s.R=[0]*512
    s.rnd=random.SystemRandom()if seed is None else random.Random(seed)
    s.st=dict(windows=0,iters=0,hits=0,matches=0,raw=0,trails=0,cuts=0,s2phases=0,s2iters=0,pairs=0,f9=0,f8=0,w17=0,parks=0,resumes=0,
    verify=0,qmax=0,opp=0,same=0,claws_distinct=0,moves=0,drops=0,waits=0)
    s.idc0=256;s.distinct=set();s.cv_id=0;s.cv_try=False;s.measure=True
    s.LA=[0]*256;s.sav=[0]*32
    s.base_setup()
  def base_setup(s):
    m=s.m;t0=m.o
    m.o+=2*2812+120
    s.K24=S0(BA[7])
    s.A7,s.A6=BA[7],BA[6]
    t25=(S0(BA[8])+MAJ(BA[8],BA[7],BA[6]))&M32
    s.CE5=(BA[9]-t25)&M32
    s.NE11=(~BE[11])&M32;s.CH0=BE[11]&BE[10]
    s.CW8=(BE[12]-BA[8]-S1(BE[11])-K[8])&M32
    s.C17=(s1(BW[15])+BW[10])&M32
    s.C9=(BW[9]+BA[5])&M32
    m.tick('run_setup',t0)
  def window_setup(s,cv=None):
    m=s.m;t0=m.o;s.m0=None;s.skip=False;tries=0
    while True:
      if cv is None or s.cv_try:
        blk=[s.rnd.getrandbits(32)for _ in range(16)];m.o+=2
        s.m0=blk;m.o+=16
        cv=compress(IV,blk);m.o+=2812
      s.cv_try=True
      ks_try=make_kernels_folded(consts(cv),P.DPB)
      gops=GW.ops(consts5(consts(cv)))
      if len(ks_try[0]['recs'])<=P.KCAP and gops<=P.GCAP and max(ks_try[0]['nreg'],ks_try[1]['nreg'])<=P.RCAP:break
      m.o+=min(gops,P.GCAP);s.st['kskip']=s.st.get('kskip',0)+1
      tries+=1;m.o+=2
      if tries>=P.KTRY:s.skip=True;return
    s.cv=cv;s.cv_id+=1
    s.c=consts(cv);m.o+=140
    cw=s.c[0]
    s.CA1=(cv[6]+K[1]-cw)&M32
    tg=m.o;c5=consts5(s.c);s.ks=ks_try
    m.o+=gops+8*len(s.ks[0]['recs'])
    if s.check and GW.AVAILABLE:
      assert GW.run(c5,0,1,P.DPB)[1]==[tuple(r)for r in s.ks[0]['recs']]
      assert GW.run(c5,1,0,P.DPB)[1]==[tuple(r)for r in s.ks[1]['recs']]
    s.dpreg=64;m.tick('generator',tg)
    s.tab=[0]*s.W;m.o+=4*s.W
    s.qn=0;s.qw=[0]*(P.QCAP//4+1)
    s.cur=0;s.it=0;tb=m.bs();s.s2=None;m.o+=1;m.be('w_s2',tb)
    for j in range(32):s.R[j]=(sum(1<<l for l in range(256)if(l>>j)&1)if j<8 else 0)
    m.o+=32
    for l in range(256):s.LA[l]=l;m.o+=3
    s.idc=s.idc0
    s.st['windows']+=1
    m.tick('window_setup',t0)
  def insert_lane(s,base,low,l,val,nbits=20):
    m=s.m;R=s.R;b=m.bs();m.o+=2
    Z=m.rl(val,l);nl=m.n(low)
    for j in range(nbits):
      t=Z if j==0 else m.rr(Z,j);p=R[base+j]
      R[base+j]=m.x(p,m.a(m.x(p,t),low))
    for j in range(nbits,32):R[base+j]=m.a(R[base+j],nl)
    m.be('insert_lane',b,True)
  def delta_lanes(s,base,G,Z):
    m=s.m;R=s.R;b=m.bs();m.o+=2
    for j in range(20):
      t=Z if j==0 else m.rr(Z,j);R[base+j]=m.x(R[base+j],m.a(t,G))
    nG=m.n(G)
    for j in range(20,32):R[base+j]=m.a(R[base+j],nG)
    m.be('delta_lanes',b,True)
  def find_lane(s,mask):
    m=s.m;bb=m.bs();m.o+=2
    low=m.a(mask,m.sb(0,mask));l=0
    for k in range(7,2,-1):
      b=m.ne(m.a(low,HIGHMASK[k]),0)
      l=m.sl(b,k)if k==7 else m.r(l,m.sl(b,k))
    l=m.r(l,m.a(m.sr(C_LOG8,m.x(m.sr(low,l),5)),7))
    m.be('find_lane',bb,True)
    return low,l
  def extract(s,base,jlo,jhi,low,l,name):
    m=s.m;R=s.R;b=m.bs();m.o+=2
    Z=m.a(R[base+jhi],low)
    for j in range(jhi-1,jlo-1,-1):Z=m.r(m.rl(Z,1),m.a(R[base+j],low))
    v=m.rr(Z,l)
    m.be(name,b,True)
    return v
  def claw(s,a,b):
    m=s.m;t0=m.o;tb0=m.bs();s.st['raw']+=1
    if m.jnz(m.a(a,1)):a0,u=b,a
    else:a0,u=a,b
    m.mv()
    if s.measure and(s.cv_id,a0,u)not in s.distinct:
      s.distinct.add((s.cv_id,a0,u));s.st['claws_distinct']+=1
    if s.check:assert fstep(a0,s.c)==fstep(u,s.c)and a0%2==0 and u%2==1
    a1=a32(m,m.ad(ms0(m,u),a0),s.CA1)
    W9=s32(m,s.C9,a1)
    ok=m.jeq(s32(m,ms0(m,a32(m,W9,D9)),ms0(m,W9)),T9)
    if s.check:
      Wc=build(s.cv,a0,recover_a1(s.cv,a0,u));Wx=expand(Wc)
      assert Wc[9]==W9 and Wx[16]==G16 and Wc[1]==u and ok==inF(Wc[9],D9,T9)
    m.be('claw_filter',tb0);m.tick('claw_filter',t0)
    if not ok:return 0
    s.st['f9']+=1;t1=m.o;tb1=m.bs()
    e4=s32(m,a32(m,a0,BA[8]),a32(m,s.K24,mMAJ(m,s.A7,s.A6,a1)))
    e5=a32(m,a1,s.CE5)
    W8=s32(m,s32(m,s.CW8,e4),m.x(s.CH0,m.a(e5,s.NE11)))
    ok8=m.jeq(s32(m,ms0(m,a32(m,W8,D8)),ms0(m,W8)),T8)
    if s.check:assert W8==Wc[8]and ok8==inF(Wc[8],D8,T8)
    m.be('claw_f8',tb1);m.tick('claw_f8',t1)
    if not ok8:return 0
    s.st['f8']+=1;t2=m.o;tb2=m.bs();cv=s.cv
    e1=s32(m,s32(m,a32(m,cv[2],a1),mS0(m,a0)),mMAJ(m,a0,cv[0],cv[1]))
    e0=a32(m,a0,s.c[1])
    w2=s32(m,s32(m,s32(m,s32(m,s32(m,BA[6],mS0(m,a1)),mMAJ(m,a1,a0,cv[0])),cv[5]),mS1(m,e1)),mCH(m,e1,e0,cv[4]))
    w2=s32(m,w2,K[2])
    w17=a32(m,a32(m,s.C17,ms0(m,w2)),u)
    okw=m.jeq(w17,W17PUB)
    if s.check:assert w17==Wx[17]
    m.be('claw_w17',tb2);m.tick('claw_w17',t2)
    if not okw:return 0
    s.st['w17']+=1;s.st['verify']+=1
    m.o+=2*2812+400
    W1m,W2m=claw_pair(s.cv,a0,u)
    if W1m!=W2m and compress(s.cv,W1m)==compress(s.cv,W2m):
      s.st['collisions']=s.st.get('collisions',0)+1;s.pairs_found=getattr(s,'pairs_found',[])+[(list(s.cv),W1m,W2m,getattr(s,'m0',None))]
      if getattr(s,'m0',None)is not None:s.messages=getattr(s,'messages',[])+[(list(s.m0)+list(W1m),list(s.m0)+list(W2m))]
      s.success=True
      return 1
    return 0
  def qpush(s,pk):
    m=s.m;b=m.bs();m.o+=2
    wi=m.sr(s.qn,2);sh=m.sl(m.a(s.qn,3),6)
    w=m.ld(s.qw,wi)
    w=m.x(w,m.a(m.x(w,m.sl(pk,sh)),m.sl((1<<64)-1,sh)))
    m.st(s.qw,wi,w);s.qn=m.ad(s.qn,1)
    m.be('qpush',b,True)
  def qpop(s,qi):
    m=s.m;b=m.bs();m.o+=2
    w=m.ld(s.qw,m.sr(qi,2));v=m.a(m.sr(w,m.sl(m.a(qi,3),6)),(1<<64)-1)
    m.be('qpop',b,True)
    return v
  def iter1(s):
    m=s.m;R=s.R;ks=s.ks;k=ks[s.cur]
    k['fn'](R);m.o+=len(k['recs']);tb=m.bs();s.cur^=1;s.it+=1;s.st['iters']+=1
    n0=R[s.dpreg];m.o+=5;dp=m.jne(n0,ONES);m.be('iter1',tb)
    if dp:
      t0=m.o
      tb=m.bs();hit=m.n(n0);G=0;W=0;nl=0;HL=0;m.o+=4;m.be('hb_init',tb)
      while True:
        tb=m.bs();low,l=s.find_lane(hit);hit=m.x(hit,low);wl=m.rl(M25,l);cf=m.jnz(m.a(wl,W));m.be('hb_sel',tb)
        if cf:
          tb=m.bs();tc=m.o;tn=m.nest;s.hit_group(G,nl,HL);m.nest=tn+(m.o-tc-2);G=0;W=0;nl=0;HL=0;m.o+=4;m.be('hb_close',tb)
        tb=m.bs();W=m.r(W,wl);G=m.r(G,low);HL=m.r(HL,m.sl(l,nl));nl=m.ad(nl,8);assert not s.check or nl<=80;s.st['hlanes']=s.st.get('hlanes',0)+1;more=m.jnz(hit);m.be('hb_add',tb)
        if not more:break
      tb=m.bs();tc=m.o;tn=m.nest;s.hit_group(G,nl,HL);m.nest=tn+(m.o-tc-2);m.be('hb_last',tb)
      full=m.jge(s.qn,P.QFULL);m.blkmax('iter1h',8)
      m.tick('hits',t0)
      if full:s.stage2()
    tb=m.bs();cs=m.jz(m.a(s.it,P.CUTP-1));m.be('iter1c',tb)
    if cs:s.cutscan()
  def wr(s,word,w,w1,st2,sh,e,en):
    m=s.m;d=m.x(e,en);m.st(s.tab,word,m.x(w,m.sl(d,sh)))
    if m.jnz(st2):m.st(s.tab,m.ad(word,1),m.x(w1,m.sr(d,m.sb(256,sh))))
  def hit_group(s,G,nl,HL):
    m=s.m;base=s.cur*32;m.o+=2;tg=m.bs();s.st['hgroups']=s.st.get('hgroups',0)+1
    s.GI=0;s.ZI=0;i=0;m.o+=3
    Z=s.extract(base,P.DPB,31,G,0,'extract25')
    m.be('hb_ext',tg)
    while True:
      tv=m.bs();l=m.a(m.sr(HL,i),255);low=m.sl(1,l);r=m.a(m.rr(Z,l),M25);i=m.ad(i,8);m.be('hb_v',tv)
      if s.check:assert sum(((s.R[base+j]>>l)&1)<<j for j in range(32))==r<<P.DPB
      s.hit(low,l,r)
      tv=m.bs();more=m.jne(i,nl);m.be('hb_lp',tv)
      if not more:break
    tv=m.bs();s.delta_lanes(base,s.GI,s.ZI);m.be('hb_ins',tv)
  def hit(s,low,l,r):
    m=s.m;base=s.cur*32;s.st['hits']+=1;ta=m.bs()
    t=m.sb(m.ad(m.sl(r,5),m.ad(m.sl(r,7),m.sl(r,9))),m.sl(r,2))
    bk=m.sr(t,17);pos=m.sb(m.ad(m.sl(bk,5),m.sl(bk,3)),bk)
    word=m.sr(pos,8);sh=m.a(pos,255);chk=m.a(r,255)
    w=m.ld(s.tab,word);v=m.sr(w,sh);w1=0;st2=m.jge(sh,218)
    if st2:w1=m.ld(s.tab,m.ad(word,1));v=m.r(v,m.sl(w1,m.sb(256,sh)))
    e=m.a(v,M39)
    lw=m.ld(s.LA,l);idv=m.a(lw,M20);ln=m.sb(s.it,m.sr(lw,20))
    if s.check:assert 0<=ln<2048 and pos==39*((r*171008)>>25)
    en=m.r(m.r(idv,m.sl(ln,20)),m.sl(chk,31))
    if m.jeq(m.sr(e,31),chk)and m.jnz(m.a(e,M31)):
      m.be('hit_a',ta);tb=m.bs();s.st['matches']+=1
      if not m.jge(m.a(m.sr(e,20),2047),ln):s.wr(word,w,w1,st2,sh,e,en)
      s.qpush(m.r(m.sl(m.a(e,M31),32),m.a(en,M31)));s.st['qmax']=max(s.st['qmax'],s.qn)
      m.be('hit_m',tb)
    else:
      m.be('hit_a',ta);tb=m.bs()
      if m.jge(ln,P.LMIN):s.wr(word,w,w1,st2,sh,e,en)
      m.be('hit_n',tb)
    td=m.bs()
    nid=s.idc
    if m.jge(nid,1<<20):s.lim=0;m.o+=1;m.be('hit_c',td);s.st['stop_grp']=s.st.get('stop_grp',0)+int(s.GI!=0);return
    s.idc=m.ad(nid,1)
    m.st(s.LA,l,m.r(nid,m.sl(s.it,20)));s.st['trails']+=1
    s.ZI=m.r(s.ZI,m.rl(m.a(m.x(m.sl(r,P.DPB),nid),M20),l));s.GI=m.r(s.GI,low)
    m.be('hit_c',td)
  def cutscan(s):
    m=s.m;t0=m.o;base=s.cur*32
    for l in range(256):
      tl=m.bs()
      lw=m.ld(s.LA,l);age=m.sb(s.it,m.sr(lw,20));m.o+=3
      if m.jge(age,P.MAXS):
        if not m.jge(s.idc,1<<20):
          low=m.sl(1,l);nid=s.idc;s.idc=m.ad(nid,1);s.st['cuts']+=1
          m.st(s.LA,l,m.r(nid,m.sl(s.it,20)));s.insert_lane(base,low,l,nid)
        else:s.lim=0;m.o+=1
      m.be('cut_lane',tl)
    m.tick('cutscan',t0)
  def bank(s,src,dst):
    m=s.m;R=s.R;m.o+=3
    for j in range(32):
      if src is None:m.st(R,dst+j,m.ld(s.sav,j))
      elif dst is None:m.st(s.sav,j,m.ld(R,src+j))
      else:x=m.ld(R,src+j);m.st(R,dst+j,m.ld(s.sav,j));m.st(s.sav,j,x)
      m.o+=3
    m.blkmax('bank_sw' if src is not None and dst is not None else('bank_in' if src is None else 'bank_out'),18 if src is not None and dst is not None else 12)
  def qins(s,base,low,l,val):
    m=s.m;bb=m.bs();m.o+=2
    wl=m.rl(M20,l)
    if m.jnz(m.a(wl,s.QW)):s.qflush(base);s.st['qconf']=s.st.get('qconf',0)+1
    s.QW=m.r(s.QW,wl);s.QZ=m.r(s.QZ,m.rl(val,l));s.QG=m.r(s.QG,low);s.st['qins']=s.st.get('qins',0)+1
    m.be('qins',bb,True)
  def qflush(s,base):
    m=s.m;bb=m.bs();m.o+=2
    if m.jnz(s.QG):
      s.insert_lane(base,s.QG,0,s.QZ);s.QW=0;s.QZ=0;s.QG=0;m.o+=3;s.st['qfl']=s.st.get('qfl',0)+1
    m.be('qflush',bb,True)
  def move_lane(s,base,q,r,lowr):
    m=s.m;R=s.R;bb=m.bs();m.o+=2
    k=m.a(m.sb(r,q),255)
    for j in range(32):
      p=R[base+j];R[base+j]=m.x(p,m.a(m.x(p,m.rl(p,k)),lowr))
    m.be('move_lane',bb,True)
  def link(s,rec,wh,it2,d,q,v):
    m=s.m;tb=m.bs();m.o+=2
    idx=m.a(m.ad(it2,d),P.WHEEL-1);wi=m.sr(idx,4);sh=m.sl(m.a(idx,15),4)
    w=m.ld(wh,wi);head=m.a(m.sr(w,sh),0xFFFF)
    v=m.r(v,m.sl(head,21));ri=m.sr(q,3);rs=m.sl(m.a(q,7),5);rw=m.ld(rec,ri)
    m.st(rec,ri,m.x(rw,m.sl(m.x(m.a(m.sr(rw,rs),M32),v),rs)))
    m.st(wh,wi,m.x(w,m.sl(m.x(head,m.ad(q,1)),sh)))
    m.be('link',tb,True)
  def fpop(s,fs,nf):
    m=s.m;tb=m.bs();m.o+=2
    nf=m.sb(nf,1);w=m.ld(fs,m.sr(nf,5));q=m.a(m.sr(w,m.sl(m.a(nf,31),3)),255)
    m.be('fpop',tb,True)
    return nf,m.sl(1,q),q
  def stage2(s,final=0):
    m=s.m;R=s.R;t0=m.o;s.st['s2phases']+=1
    sv=s.cur
    tb=m.bs()
    if m.jz(s.s2 is not None):
      m.be('s2_in',tb);s.bank(sv*32,None)
      ti=m.bs();cur=0;it2=0;bact=0;live=0;occ=0;nf=128
      rec=[0]*32;wh=[0]*(P.WHEEL//16);fs=[sum(((32*i+j)<<(8*j))for j in range(32))for i in range(4)];m.o+=22;m.be('s2_init',ti)
    else:
      cur,it2,bact,live,occ,nf,rec,wh,fs=s.s2;m.o+=18;m.be('s2_in',tb);s.bank(sv*32,cur*32);s.st['resumes']+=1
    tq=m.bs();qi=0;qn=s.qn;pw=0;s.QW=0;s.QZ=0;s.QG=0;m.o+=6;m.be('s2_q',tq)
    while True:
      tw=m.bs();idx=m.a(it2,P.WHEEL-1);wi=m.sr(idx,4);sh=m.sl(m.a(idx,15),4)
      w=m.ld(wh,wi);head=m.a(m.sr(w,sh),0xFFFF)
      if m.jnz(head):m.st(wh,wi,m.x(w,m.sl(head,sh)))
      m.be('wheel_check',tw)
      while m.jnz(head):
        tl=m.bs()
        q=m.sb(head,1);v=m.a(m.sr(m.ld(rec,m.sr(q,3)),m.sl(m.a(q,7),5)),M32);head=m.sr(v,21);cB=m.a(v,M20)
        qp=m.x(q,128);lowq=m.sl(1,q)
        if m.jnz(m.a(v,1<<20)):
          m.be('cb_a',tl);tl=m.bs()
          s.qins(cur*32,m.sl(lowq,128),qp,cB);bact=m.r(bact,lowq)
          m.be('cb_in',tl)
        elif m.jz(m.a(m.sr(occ,qp),1)):
          m.be('cb_a',tl);tl=m.bs()
          lowp=m.sl(1,qp);s.qins(cur*32,lowp,qp,cB)
          occ=m.r(occ,lowp);bact=m.r(bact,m.sl(1,m.a(q,127)))
          m.be('cb_free',tl)
        elif m.jnz(nf):
          m.be('cb_a',tl);tl=m.bs()
          nf,lowr,r=s.fpop(fs,nf)
          if s.check:assert not(occ>>r)&1 and not(occ>>(r+128))&1
          s.qflush(cur*32);s.move_lane(cur*32,q,r,lowr)
          s.qins(cur*32,m.sl(lowr,128),m.ad(r,128),cB)
          occ=m.r(m.x(occ,lowq),m.r(lowr,m.sl(lowr,128)));bact=m.r(bact,lowr);s.st['moves']+=1
          m.be('cb_move',tl)
        else:
          m.be('cb_a',tl);tl=m.bs()
          occ=m.x(occ,lowq);live=m.sb(live,1);s.st['drops']+=1
          m.be('cb_drop',tl)
      while True:
        tl=m.bs()
        if m.jz(pw):
          m.o+=4
          if not qi<qn:m.be('launch_t',tl);break
          pk=s.qpop(qi);qi+=1;m.o+=1
          x1=m.sr(pk,32);x2=m.a(pk,M32)
          l1=m.sr(x1,20);l2=m.sr(x2,20)
          if m.jge(l1,l2):xA,lA,xB,lB=x1,l1,x2,l2
          else:xA,lA,xB,lB=x2,l2,x1,l1
          m.o+=2
          d=m.sb(lA,lB);sg=m.jge(d,P.D0)
          pw=m.r(m.r(m.a(xA,M20),m.sl(m.a(xB,M20),20)),m.r(m.sl(d,40),m.sl(m.r(sg,2),51)))
          m.be('launch',tl);tl=m.bs()
        if m.jnz(m.a(pw,1<<51)):
          hm=m.a(m.n(occ),m.rl(occ,128))
          if m.jnz(hm):
            m.be('l_try',tl);tl=m.bs()
            lowq,q=s.find_lane(hm)
            m.be('l_half',tl)
          elif m.jge(nf,P.KRES):
            m.be('l_try',tl);tl=m.bs()
            nf,lowq,q=s.fpop(fs,nf)
            m.be('l_f2s',tl)
          else:
            m.be('l_try',tl);s.st['waits']+=1;break
          tl=m.bs();iA=m.a(pw,M20);iB=m.a(m.sr(pw,20),M20);d=m.a(m.sr(pw,40),2047)
          s.qins(cur*32,lowq,q,iA);occ=m.r(occ,lowq)
          s.link(rec,wh,it2,d,q,iB)
          m.be('l_single',tl)
        else:
          if not m.jge(nf,P.KRES):
            m.be('l_try',tl);s.st['waits']+=1;break
          m.be('l_try',tl);tl=m.bs();iA=m.a(pw,M20);iB=m.a(m.sr(pw,20),M20);d=m.a(m.sr(pw,40),2047)
          nf,lowq,q=s.fpop(fs,nf)
          s.qins(cur*32,lowq,q,iA);occ=m.r(occ,m.r(lowq,m.sl(lowq,128)))
          if m.jz(d):
            s.qins(cur*32,m.sl(lowq,128),m.ad(q,128),iB);bact=m.r(bact,lowq)
          else:
            s.link(rec,wh,it2,d,q,m.r(iB,1<<20))
          m.be('l_pair',tl)
        tl=m.bs();live=m.ad(live,1);pw=0;m.o+=1;s.st['pairs']+=1;m.be('l_end',tl)
      tb=m.bs();s.qflush(cur*32);m.be('s2_fl',tb)
      if m.jz(live):break
      tb=m.bs();sp=m.jz(final)and m.jge(qi,qn)and m.jz(pw);m.be('s2_susp',tb)
      if sp:break
      assert not s.check or s.QG==0
      k=s.ks[cur];k['fn'](R);m.o+=len(k['recs']);ts=m.bs();cur^=1;it2+=1;s.QW=0;s.QZ=0;s.QG=0;m.o+=6;m.be('s2_step',ts);s.st['s2iters']+=1
      tc=m.bs();base=cur*32;acc=0
      for j in range(P.CMP1):
        pl=R[base+j];dj=m.x(pl,m.rl(pl,128));acc=dj if j==0 else m.r(acc,dj)
      cand=m.a(m.n(acc),bact)
      m.be('cmp1',tc)
      if m.jnz(cand):
        tc=m.bs();acc2=0
        for j in range(P.CMP1,32):
          pl=R[base+j];dj=m.x(pl,m.rl(pl,128));acc2=dj if j==P.CMP1 else m.r(acc2,dj)
        full=m.a(cand,m.n(acc2))
        m.be('cmp2',tc)
        while m.jnz(full):
          tm=m.bs()
          low,l=s.find_lane(full);full=m.x(full,low)
          pp=R[(cur^1)*32]
          if m.jnz(m.a(m.x(pp,m.rl(pp,128)),low)):
            s.st['opp']+=1
            low2=m.r(low,m.sl(low,128))
            Z=s.extract((cur^1)*32,0,31,low2,l,'extract32x2')
            a=m.a(Z,M32);b=m.a(m.sr(Z,128),M32)
            tcl=m.o;r_cl=s.claw(a,b);m.nest+=m.o-tcl
            if r_cl:s.success=True
          else:s.st['same']+=1
          bact=m.x(bact,low);occ=m.x(occ,m.r(low,m.sl(low,128)));live=m.sb(live,1)
          fi=m.sr(nf,5);fsh=m.sl(m.a(nf,31),3);fw=m.ld(fs,fi);m.st(fs,fi,m.x(fw,m.sl(m.x(m.a(m.sr(fw,fsh),255),l),fsh)));nf=m.ad(nf,1)
          m.be('merge',tm)
    if s.check:assert pw==0
    tb=m.bs()
    if m.jnz(live):
      s.s2=(cur,it2,bact,live,occ,nf,rec,wh,fs);m.o+=18;m.be('s2_out',tb);s.bank(cur*32,sv*32);s.st['parks']+=1
    else:
      m.be('s2_out',tb);s.s2=None;s.bank(None,sv*32)
      if s.check:assert not any(wh)
    s.qn=0;m.tick('stage2',t0)
  def run_window(s,cv=None,iters=None):
    s.success=False;s.window_setup(cv)
    if s.skip:return s.st
    s.lim=iters if iters else s.win//256
    while s.it<s.lim:
      s.iter1()
      if s.success:break
    m=s.m;tb=m.bs();go=(m.jnz(s.qn)or m.jnz(s.s2 is not None))and m.jz(s.success);m.be('w_end',tb);m.blkmax('w_end',6)
    if go:s.stage2(final=1)
    return s.st
GEN_EXPERIMENTS=("r39-transplant-claw","r39-window-small")
WIN_EXP={
7365741297968335814:(817,817,33229,1744,2874,840,17,3,60,1,0,730,22914523,580840,1238),
14152957579836449138:(795,795,32736,1660,2355,809,11,1,54,0,0,714,22090605,580712,1238),
17548137956998735317:(909,909,32545,1771,2659,926,12,3,73,4,0,710,22284239,580680,1236),
11186828115432487819:(797,797,32820,1653,2529,804,11,0,53,2,0,699,21944236,580592,1168),
}
def _e1(i,sd):
  """r39-transplant-claw (proof Section 10)"""
  if i==0:
    A=Attack(win=1<<20,check=True)
    A.window_setup(cv=CV_PUB)
    a0,u=BA[4],MP_PUB[1]
    assert a0%2==0 and fstep(a0,A.c)==(s0(u)-u)&M
    A.check=False;o0=A.m.o
    r=A.claw(a0,u);A.check=True
    W1m,W2m=A.pairs_found[0][1:3]if r==1 else(None,None)
    adv=verify_advice_construction()
    assert adv=={"g16_fibre_size":2,"g17_fibre_size":1,"fibre_dfs_ops":1944,"downward_inv_ok":1,
    "advice_slice_cands":256,"advice_slice_hits":1,"ops_per_cand":408}
    out={"claw_returned_pair":r,"passed_f9":A.st["f9"],"passed_f8":A.st["f8"],"passed_w17":A.st["w17"],
    "pair_is_advice":int(W1m==MP_PUB and W2m==M_PUB),
    "sfs_collision":int(compress(CV_PUB,MP_PUB)==compress(CV_PUB,M_PUB)and MP_PUB!=M_PUB),
    "advice_w16_is_g":int(expand(MP_PUB)[16]==G16),"advice_w17":int(expand(MP_PUB)[17]==W17PUB),
    "kernel_records":len(A.ks[0]["recs"]),"claw_ops":A.m.o-o0,"blk_census":sum(A.m.blk.values()),
    "g16_fibre_size":adv["g16_fibre_size"],"g17_fibre_size":adv["g17_fibre_size"],
    "fibre_dfs_ops":adv["fibre_dfs_ops"],"advice_slice_hits":adv["advice_slice_hits"],"ops_per_cand":adv["ops_per_cand"]}
    assert out=={"claw_returned_pair":1,"passed_f9":1,"passed_f8":1,"passed_w17":1,"pair_is_advice":1,
    "sfs_collision":1,"advice_w16_is_g":1,"advice_w17":1,"kernel_records":731,"claw_ops":6173,
    "blk_census":150,"g16_fibre_size":2,"g17_fibre_size":1,"fibre_dfs_ops":1944,
    "advice_slice_hits":1,"ops_per_cand":408}
    return out
  rnd=random.Random(sd)
  cv=[rnd.getrandbits(32)for _ in range(8)]
  a0=rnd.getrandbits(32)&~1;u=rnd.getrandbits(32)|1
  c=consts(cv)
  a1=recover_a1(cv,a0,u);W=build(cv,a0,a1);V=second(W)
  A1,E1,_=traj(cv,W);A2,E2,_=traj(cv,V)
  out={"transplant_ok":int(A1[6:20]==BA[6:20]and E1[10:20]==BE[10:20]and A2[6:20]==CA[6:20]and E2[10:20]==CE[10:20]),
  "w1_is_u":int(W[1]==u),"w16_identity":int(((expand(W)[16]-G16)&M)==((fstep(u,c)-fstep(a0,c))&M))}
  assert out=={"transplant_ok":1,"w1_is_u":1,"w16_identity":1}
  if i==1:out.update(verify_advice_construction())
  return out
_W17_HIST=[0]*256;_W18_HIST=[0]*256;_G_SEQ=[]
def _e2(i,sd):
  """r39-window-small (proof Section 10)"""
  if i==4:return _t4(sd)
  if i>4:return None
  A=Attack(win=1<<22,seed=sd,check=True)
  A.run_window()
  st=A.st;dg=count_groups(A.distinct);f8_all=w17_8=w17_12=0;triples=set()
  for _,a0,u in sorted(A.distinct):
    a1=recover_a1(A.cv,a0,u);W=build(A.cv,a0,a1);ex=expand(W);w17,w18=ex[17],ex[18]
    in8=int(((s0((W[8]+D8)&M)-s0(W[8]))&M)==T8)
    in9=int(((s0((W[9]+D9)&M)-s0(W[9]))&M)==T9)
    f8_all+=in8;w17_8+=((w17&0xff)==(W17PUB&0xff));w17_12+=((w17&0xfff)==(W17PUB&0xfff))
    triples.add((W[8],W[9],w17,w18))
    if sd in WIN_EXP:
      _W17_HIST[w17&0xff]+=1;_W18_HIST[w18&0xff]+=1;_G_SEQ.append((in9,w17&1,w18&1))
  assert len(triples)==st["claws_distinct"]and st["opp"]==st["raw"]
  tup=(st["claws_distinct"],dg,st["hits"],st["matches"],st["s2iters"],st["raw"],st["f9"],st["f8"],
  f8_all,w17_8,w17_12,len(A.ks[0]["recs"]),A.m.o,A.m.cat.get("generator",0),sum(A.m.blk.values()))
  if sd in WIN_EXP:assert tup==WIN_EXP[sd]
  NB=('hb_init','hb_sel','hb_close','hb_add','hb_last','hb_ext','hb_v','hb_lp','hb_ins','qins','qflush','s2_fl','delta_lanes')
  assert all(A.m.blk.get(k,0)>0 for k in NB)and st['hgroups']<st['hlanes']==st['hits']and st['qconf']>0 and st['qfl']<st['qins']and st['moves']>0
  return{"iterations":st["iters"],"dp_hits":st["hits"],"matches":st["matches"],"stage2_iterations":st["s2iters"],"raw_claws":st["raw"],
  "distinct_claws":st["claws_distinct"],"distinct_groups":dg,"passed_f9":st["f9"],"passed_f8":st["f8"],"f8_all":f8_all,
  "w17_low8":w17_8,"w17_low12":w17_12,"kernel_records":len(A.ks[0]["recs"]),"ops":A.m.o,
  "generator_ops":A.m.cat.get("generator",0),"blk_census":sum(A.m.blk.values())}
T4_EXP=(7466204727408384999,(473,477,32719,978,748,15,15,7317,21892301,1234,0,996,493))
def _t4(sd):
  o=(P.QFULL,P.MAXS,P.CUTP);r=[]
  try:
    for q in(64,o[0]):P.QFULL,P.MAXS,P.CUTP=q,192,64;A=Attack(win=1<<22,seed=sd,check=True);A.run_window();r.append(A)
  finally:P.QFULL,P.MAXS,P.CUTP=o
  A,B=r;dr=A.st['drops']+B.st['drops']
  assert(dr>0 or(A.distinct==B.distinct and A.st['raw']==B.st['raw']))and B.st['parks']==0 and A.s2 is None and A.qn==0
  C=Attack(win=1<<22,seed=sd,check=True);C.idc0=(1<<20)-1998;C.run_window()
  assert C.lim==0 and C.idc==1<<20 and C.it<1<<14 and C.s2 is None and C.qn==0 and(sd!=T4_EXP[0]or C.st.get('stop_grp',0)==1)
  st=A.st;c=st['cuts'];A.it+=1536;A.cutscan()
  assert st['cuts']-c==256 and all(A.LA[l]>>20==A.it for l in range(256))
  t=(st['claws_distinct'],st['raw'],st['hits'],st['matches'],st['s2iters'],st['parks'],st['resumes'],c,A.m.o,sum(A.m.blk.values()),dr,C.it,C.st['s2iters'])
  assert st['opp']==st['raw']and min(t[5:8])>0 and(sd!=T4_EXP[0]or t==T4_EXP[1])
  return dict(zip(("distinct_claws","raw_claws","dp_hits","matches","stage2_iterations","parks","resumes","cuts","ops","blk_census","drops","idc_stop_iteration","idc_stop_stage2_iterations"),t))
def serve():
  req=json.load(sys.stdin)
  eid=req["experiment_id"]
  if eid not in GEN_EXPERIMENTS:raise SystemExit("unknown experiment id")
  fn=_e1 if eid==GEN_EXPERIMENTS[0]else _e2
  rows=[]
  for t in req["trials"]:
    obs=fn(t["trial"],int(t["seed"][:16],16))
    row={"trial":t["trial"],"message_a_hex":None,"message_b_hex":None}
    if obs:row["observations"]=obs
    rows.append(row)
  if eid==GEN_EXPERIMENTS[1]and len(_G_SEQ)==3318:
    exp=3318/256.0
    c17=sum((c-exp)**2/exp for c in _W17_HIST);c18=sum((c-exp)**2/exp for c in _W18_HIST)
    assert round(c17,2)==268.01 and round(c18,2)==280.2
    for k in range(3):
      xs=[g[k]for g in _G_SEQ];m=sum(xs)/3318.0;v=sum((x-m)**2 for x in xs)
      assert abs(sum((xs[j]-m)*(xs[j+1]-m)for j in range(3317))/v)*3318**0.5<3
  sys.stdout.write(json.dumps({"schema_version":1,"trials":rows},sort_keys=True,separators=(",",":"))+"\n")
B_WINDOWS=875224534025647266674449055745
W_BUDGET=434312448423543105820061636936834482177
def main():
  a=sys.argv[1:]
  if "--gen-c" in a:sys.stdout.write(GEN_C);return
  if "--windows" in a:
    nwin=int(a[a.index("--windows")+1]);seed=int(a[a.index("--seed")+1])if "--seed" in a else 1;res=[]
    for w in range(nwin):
      A=Attack(win=P.WIN,seed=seed*1000+w,check="--check" in a)
      t=time.time();A.run_window()
      st=dict(A.st);st.update(ops=A.m.o,cat=dict(A.m.cat),blk=dict(A.m.blk),sec=time.time()-t,kernel_len=len(A.ks[0]["recs"]),
      kernel_nreg=max(A.ks[0]["nreg"],A.ks[1]["nreg"]),distinct_claws=len(A.distinct),distinct_groups=count_groups(A.distinct),seed=seed*1000+w)
      res.append(st)
      print("window %d: %d distinct claws, %d operations, %.1f per claw"%(w,st["distinct_claws"],st["ops"],st["ops"]/max(1,st["distinct_claws"])),flush=True)
    if "--out" in a:json.dump(res,open(a[a.index("--out")+1],"w"))
    return
  if "--attack" in a:
    seed=int(a[a.index("--seed")+1])if "--seed" in a else None;w=0
    work=0
    while w<B_WINDOWS and work<W_BUDGET:
      A=Attack(win=P.WIN,seed=None if seed is None else seed*1000+w,check=False);A.measure=False;A.run_window();w+=1;work+=A.m.o+6
      for M1,M2 in getattr(A,"messages",[]):
        print("collision","".join("%08x"%x for x in M1),"".join("%08x"%x for x in M2),flush=True);return
    print("no collision after %d windows (%d charged operations; B = %d, budget %d)"%(w,work,B_WINDOWS,W_BUDGET),flush=True);sys.exit(1)
  serve()
if __name__=="__main__":
  main()
