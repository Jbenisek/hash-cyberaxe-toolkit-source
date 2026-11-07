import sys,json,random,math,struct
M=0xffffffff
class Sw:
    def __init__(w,L):
        w.L=L;w.m=int.from_bytes((M).to_bytes(8,"little")*L,"little");w.o=int.from_bytes((1).to_bytes(8,"little")*L,"little")
    def bc(w,c):return(c&M)*w.o
    def rnd(w,rng):return rng.getrandbits(64*w.L)&w.m
    def S1(w,e):return((e>>6|e<<26)^(e>>11|e<<21)^(e>>25|e<<7))&w.m
    def S0(w,a):return((a>>2|a<<30)^(a>>13|a<<19)^(a>>22|a<<10))&w.m
    def s1(w,u):return((u>>17|u<<15)^(u>>19|u<<13)^(u>>10))&w.m
    def s0(w,v):return((v>>7|v<<25)^(v>>18|v<<14)^(v>>3))&w.m
    def neg(w,z):return((z&w.m)^w.m)+w.o
    def zero(w,x):
        f=(((x+w.m)>>32)&w.o)^w.o;out=[]
        while f:lo=f&-f;out.append((lo.bit_length()-1)>>6);f^=lo
        return out
    def get(w,x,i):return(x>>(64*i))&M
Z=Sw(1);S0,S1,s0,s1=Z.S0,Z.S1,Z.s0,Z.s1
def CH(e,f,g):return(e&f)^(~e&g&M)
def MJ(a,b,c):return(a&b)^(a&c)^(b&c)
def cr(n):
    x=1<<(n.bit_length()//3+1)
    while 1:
        y=(2*x+n//(x*x))//3
        if y>=x:return x
        x=y
K=[cr(p<<96)&M for p in[p for p in range(2,168)if all(p%q for q in range(2,p))]]
NR=39
CV=[int(x,16)for x in "347e7638 d589578a f49ec11a 5d2fe302 ee176950 3beb1b4f 62b5db32 b3e3932e".split()]
MX=[int(x,16)for x in("eb3315e8 bc4aa24c a2335258 d5195a6f 473d8744 9a094361 7b6069ac 1bf5bc7e "
"b5a3b6fe eaffcebb cbfadf87 99a06b31 a956f91e b05f04ad 43660038 d80d950f").split()]
DL=[0]*8+[0x40000000,0xf7801000,0xc0000000,0x0601dcd4,0xffefe800,0,0,0]
MY=[(a+b)&M for a,b in zip(MX,DL)]
PIN={16:0x9776869e,17:0x771adf7e}
T8,T9,MASK8,MASK9=0x087ff000,0x03010000,0xCC19E60C,0xF9983C0F
CA={18:"=u"+"="*30}
CE={18:"0=======0=====100==000=0=======0",19:"============u=============n=====",
20:"======uu=======u================",22:"=u"+"="*30,23:"=0"+"="*30}
LIN=[(0,17,16,0,18,16,0),(0,17,24,0,18,24,0),(0,17,26,0,18,26,0),(0,17,30,0,18,30,0),
(0,18,10,0,17,21,0),(0,18,7,0,18,19,1),(0,18,9,0,18,18,1),(1,17,5,1,18,5,0),
(1,17,19,1,18,19,0)]
def cell(s):
    m=v=d=0
    for i,c in enumerate(s):
        b=1<<(31-i);m|=b*(c in "01un");v|=b*(c in "1u");d|=b*(c in "un")
    return(m,v,M,d)
EQ=cell("="*32);CAr={t:cell(CA.get(t,"="*32))for t in range(18,24)};CEr={t:cell(CE.get(t,"="*32))for t in range(18,24)}
NF={t:bin(CEr[t][0]).count("1")for t in CEr}
def trace(cv,w,nr):
    W=list(w)
    for i in range(16,nr):W.append((s1(W[i-2])+W[i-7]+s0(W[i-15])+W[i-16])&M)
    A=[cv[3],cv[2],cv[1],cv[0]];E=[cv[7],cv[6],cv[5],cv[4]]
    for i in range(nr):
        e=(A[i]+E[i]+S1(E[i+3])+CH(E[i+3],E[i+2],E[i+1])+K[i]+W[i])&M
        A.append((e-A[i]+S0(A[i+3])+MJ(A[i+3],A[i+2],A[i+1]))&M);E.append(e)
    return A,E,W
def compress(cv,w):
    A,E,_=trace(cv,w,NR)
    return[(x+y)&M for x,y in zip(cv,A[-1:-5:-1]+E[-1:-5:-1])]
def dok(c,D):
    m,v,dm,d=c;cs=1
    for b in range(32):
        ns=0;db=(D>>b)&1
        for cin in(0,1):
            if(cs>>cin)&1:
                for xb in(0,1):
                    if(m>>b)&1 and xb!=(v>>b)&1:continue
                    if(dm>>b)&1 and db^cin!=(d>>b)&1:continue
                    ns|=1<<((xb&db)|(xb&cin)|(db&cin))
        cs=ns
        if not cs:return False
    return True
class St:pass
def cp(s):
    n=St();n.xa,n.xe,n.xw,n.ya,n.ye,n.yw=s.xa[:],s.xe[:],s.xw[:],s.ya[:],s.ye[:],s.yw[:];return n
def wd(s,u):return s1(s.yw[u-2])-s1(s.xw[u-2])+s.yw[u-7]-s.xw[u-7]+DL[u-16]+s0(s.yw[u-15])-s0(s.xw[u-15])
def consts(s,t):
    xa,xe,ya,ye=s.xa,s.xe,s.ya,s.ye;i=t+4
    rx=xa[i-4]+xe[i-4]+S1(xe[i-1])+CH(xe[i-1],xe[i-2],xe[i-3])
    ry=ya[i-4]+ye[i-4]+S1(ye[i-1])+CH(ye[i-1],ye[i-2],ye[i-3])
    cx=-xa[i-4]+S0(xa[i-1])+MJ(xa[i-1],xa[i-2],xa[i-3])
    cy=-ya[i-4]+S0(ya[i-1])+MJ(ya[i-1],ya[i-2],ya[i-3])
    d=wd(s,t);de=ry-rx+d
    return cx&M,(rx+K[t])&M,de&M,(de+cy-cx)&M,d&M,cy&M
def setrow(s,t,ex):
    cx,rx,de,da,d,cy=consts(s,t);i=t+4
    s.xe[i]=ex;s.xw[t]=(ex-rx)&M;s.xa[i]=(ex+cx)&M
    s.ye[i]=(ex+de)&M;s.yw[t]=(s.xw[t]+d)&M;s.ya[i]=(s.ye[i]+cy)&M
def cok(c,x,y):return(x&c[0])==c[1]and((x^y)&c[2])==c[3]
def rowok(s,t):
    i=t+4
    if not(cok(CAr[t],s.xa[i],s.ya[i])and cok(CEr[t],s.xe[i],s.ye[i])and cok(EQ,s.xw[t],s.yw[t])):return False
    g=lambda k,r:(s.xa if k==0 else s.xe)[r+4]
    return t!=18 or all(((g(k1,r1)>>b1)^(g(k2,r2)>>b2))&1==df for k1,r1,b1,k2,r2,b2,df in LIN)
def rowokv(s,t,xw,ex,ax,yw,ye,ay):
    if not(cok(CAr[t],ax,ay)and cok(CEr[t],ex,ye)and cok(EQ,xw,yw)):return False
    if t!=18:return True
    for k1,r1,b1,k2,r2,b2,df in LIN:
        v1=(ax if k1==0 else ex)if r1==18 else(s.xa if k1==0 else s.xe)[r1+4]
        v2=(ax if k2==0 else ex)if r2==18 else(s.xa if k2==0 else s.xe)[r2+4]
        if((v1>>b1)^(v2>>b2))&1!=df:return False
    return True
def look1(s,t,ex,ax,ye,ay):
    i=t+5
    d=wd(s,t+1)&M
    if d:return False
    rx=s.xa[i-4]+s.xe[i-4]+S1(ex)+CH(ex,s.xe[i-2],s.xe[i-3])
    ry=s.ya[i-4]+s.ye[i-4]+S1(ye)+CH(ye,s.ye[i-2],s.ye[i-3])
    cx=-s.xa[i-4]+S0(ax)+MJ(ax,s.xa[i-2],s.xa[i-3])
    cy=-s.ya[i-4]+S0(ay)+MJ(ay,s.ya[i-2],s.ya[i-3])
    de=ry-rx+d
    return dok(CAr[t+1],(de+cy-cx)&M)and dok(CEr[t+1],de&M)
def wd2(s,t,xw,yw):return(s1(yw)-s1(xw)+s.yw[t-5]-s.xw[t-5]+DL[t-14]+s0(s.yw[t-13])-s0(s.xw[t-13]))&M
def cands(s,t,nb,sw,rng):
    cx,rx,de,da,dw,cy=consts(s,t)
    if dw:return[]
    mA,vA,_,dA=CAr[t];mE,vE,_,dE=CEr[t];nx=t<23;m=sw.m
    xa,xe,ya,ye=s.xa,s.xe,s.ya,s.ye;i=t+4;bc=sw.bc;S0v,S1v=sw.S0,sw.S1
    DE,CX,DA,NM,VE,DEc,MA,VA,DAc=bc(de),bc(cx),bc(da),bc(~mE),bc(vE),bc(dE),bc(mA),bc(vA),bc(dA)
    if nx:
        CD=bc(ya[i-3]+ye[i-3]-xa[i-3]-xe[i-3]+wd(s,t+1));CN=bc(xa[i-3]-ya[i-3])
        xe1,xe2,ye1,ye2,xa1,xa2,ya1,ya2=[bc(z)for z in(xe[i-1],xe[i-2],ye[i-1],ye[i-2],xa[i-1],xa[i-2],ya[i-1],ya[i-2])]
    good=[]
    for _ in range(nb):
        ex=(sw.rnd(rng)&NM)|VE;ey=(ex+DE)&m;ax=(ex+CX)&m;ay=(ax+DA)&m
        bad=(ex^ey^DEc)|((ax&MA)^VA)|(ax^ay^DAc)
        if nx:
            deu=(CD+S1v(ey)+(ye2^(ey&(ye1^ye2)))+sw.neg(S1v(ex)+(xe2^(ex&(xe1^xe2)))))&m
            bad|=(deu+S0v(ay)+((ay&(ya1|ya2))|(ya1&ya2))+sw.neg(S0v(ax)+((ax&(xa1|xa2))|(xa1&xa2)))+CN)&m
        good+=[sw.get(ex,q)for q in sw.zero(bad)]
    out=[]
    for ex in good:
        axv=(ex+cx)&M;yev=(ex+de)&M;xwv=(ex-rx)&M;ywv=(xwv+dw)&M;ayv=(yev+cy)&M
        if not rowokv(s,t,xwv,ex,axv,ywv,yev,ayv):continue
        if nx and not look1(s,t,ex,axv,yev,ayv):continue
        if t<22 and wd2(s,t,xwv,ywv):continue
        out.append(ex)
    return out
def start():
    s=St();s.xa=[0]*43;s.xe=[0]*43;s.ya=[0]*43;s.ye=[0]*43
    s.xw=MX[:]+[0]*(NR-16);s.yw=MY[:]+[0]*(NR-16)
    Ax,Ex,_=trace(CV,MX,NR);Ay,Ey,_=trace(CV,MY,NR)
    for r in range(15,20):s.xa[r],s.xe[r],s.ya[r],s.ye[r]=Ax[r],Ex[r],Ay[r],Ey[r]
    for t in(16,17):setrow(s,t,PIN[t])
    return s
CFG={18:(512,8),19:(2048,8),20:(2048,8),21:(128,4),22:(256,6),23:(4,1)}
NP=800
def smc(rng):
    P=[start()]*NP;ks=[];l2=0.0;SW={}
    for t in range(18,24):
        L,nb=CFG[t];sw=SW.setdefault(L,Sw(L));pool=[]
        for pi,p in enumerate(P):
            for ex in cands(p,t,nb,sw,rng):pool.append((pi<<32)|ex)
        ks.append(len(pool))
        if not pool:return None,ks,None
        l2+=math.log2(len(pool)/(NP*nb*L))-NF[t]
        P2=[]
        for _ in range(NP):
            e=pool[rng.randrange(len(pool))];s2=cp(P[e>>32]);setrow(s2,t,e&M);P2.append(s2)
        P=P2
    return P,ks,l2
def inF(i,T,w):return((s0((w+DL[i])&M)-s0(w))&M)==T
def members(mask,i,T):
    out=[];sub=0
    while True:
        if inF(i,T,sub):out.append(sub)
        sub=(sub-mask)&mask
        if sub==0:return out
def finals(s,sw,x8,x9):
    m=sw.m;bc=sw.bc;S0v,S1v,s0v,s1v=sw.S0,sw.S1,sw.s0,sw.s1
    if not hasattr(sw,"kp"):sw.kp=(bc(DL[8]),bc(DL[9]),[bc(K[t])for t in range(NR)])
    kb8,kb9,kb=sw.kp
    xw=[bc(v)for v in s.xw[:24]]+[0]*(NR-24);yw=[bc(v)for v in s.yw[:24]]+[0]*(NR-24)
    xw[8]=x8;xw[9]=x9;yw[8]=(x8+kb8)&m;yw[9]=(x9+kb9)&m
    a,b,c,d=[bc(s.xa[i])for i in(27,26,25,24)];e,f,g,h=[bc(s.xe[i])for i in(27,26,25,24)]
    A,B,C,D=[bc(s.ya[i])for i in(27,26,25,24)];E,F,G,H=[bc(s.ye[i])for i in(27,26,25,24)]
    for t in range(24,NR):
        xw[t]=(s1v(xw[t-2])+xw[t-7]+s0v(xw[t-15])+xw[t-16])&m
        yw[t]=(s1v(yw[t-2])+yw[t-7]+s0v(yw[t-15])+yw[t-16])&m
        k=kb[t]
        t1=h+S1v(e)+(g^(e&(f^g)))+k+xw[t];t2=S0v(a)+((a&(b|c))|(b&c))
        h,g,f,e,d,c,b,a=g,f,e,(d+t1)&m,c,b,a,(t1+t2)&m
        t1=H+S1v(E)+(G^(E&(F^G)))+k+yw[t];t2=S0v(A)+((A&(B|C))|(B&C))
        H,G,F,E,D,C,B,A=G,F,E,(D+t1)&m,C,B,A,(t1+t2)&m
    return sw.zero((a^A)|(b^B)|(c^C)|(d^D)|(e^E)|(f^F)|(g^G)|(h^H))
def verify(s,w8,w9):
    xw=s.xw[:];xw[8]=w8;xw[9]=w9
    for t in range(23,15,-1):xw[t-16]=(xw[t]-s1(xw[t-2])-xw[t-7]-s0(xw[t-15]))&M
    w=xw[:16];A={r:s.xa[r+4]for r in range(12,16)};E={r:s.xe[r+4]for r in range(12,16)}
    for i in range(15,-1,-1):
        A[i-4]=(E[i]-A[i]+S0(A[i-1])+MJ(A[i-1],A[i-2],A[i-3]))&M
        E[i-4]=(E[i]-A[i-4]-S1(E[i-1])-CH(E[i-1],E[i-2],E[i-3])-K[i]-w[i])&M
    cv=[A[-1],A[-2],A[-3],A[-4],E[-1],E[-2],E[-3],E[-4]]
    return compress(cv,w)==compress(cv,[(a+b)&M for a,b in zip(w,DL)]),(A[0]&1)*2+(w[1]&1)
def known_answer():
    s=start();Ex=trace(CV,MX,NR)[1]
    for t in range(18,24):
        setrow(s,t,Ex[t+4])
        if not rowok(s,t):return 0
    return int(finals(s,Sw(1),MX[8],MX[9])==[0]and verify(s,MX[8],MX[9])[0])
NCH,NB,LF=20,80,2048
EXP_S="""
"""
def _exp_decode(t):
    out={}
    for i,ln in enumerate(t.strip().splitlines()):
        ks,l2,hs,cs=ln.split("|")
        out["r39-tail-%02d"%(i+1)]=([int(x)for x in ks.split(",")],float(l2),int(hs),[int(x)for x in cs.split(",")])
    return out
EXP=_exp_decode(EXP_S)
QDECL=-75.47
def verify_smc_stats(qdecl=None):
    c18=len(cands(start(),18,32,Sw(2048),random.Random(12345)))
    if not EXP:
        return c18
    L18,NB18=CFG[18];n=len(EXP)
    assert c18==206 and abs(c18/65536-sum(v[0][0]for v in EXP.values())/(n*NP*L18*NB18))<0.0003
    qlin=[(2.0**v[1])*(v[2]/float(NCH*NB*LF))for v in EXP.values()]
    qlog=[math.log2(q)for q in qlin]
    m_lin=sum(qlin)/n
    sd_lin=math.sqrt(sum((q-m_lin)**2 for q in qlin)/(n-1))
    lcb_lin=math.log2(m_lin-2.650308*sd_lin/math.sqrt(n))
    m_log=sum(qlog)/n
    lcb_log=m_log-2.650308*math.sqrt(sum((x-m_log)**2 for x in qlog)/(n-1))/math.sqrt(n)
    lcb999=math.log2(m_lin-3.852*sd_lin/math.sqrt(n))
    tcls=[sum(v[3][k]for v in EXP.values())for k in range(4)]
    assert sum(tcls)==sum(v[2]for v in EXP.values())
    assert lcb_lin>qdecl and lcb_log>qdecl and lcb999>qdecl
    q01=[(2.0**v[1])*(4.0*v[3][1]/float(NCH*NB*LF))for v in EXP.values()]
    m01=sum(q01)/n;sd01=math.sqrt(sum((q-m01)**2 for q in q01)/(n-1))
    assert math.log2(m01-2.650308*sd01/math.sqrt(n))>qdecl
    return c18
def main():
    req=json.loads(sys.stdin.read());eid=req.get("experiment_id","");tr=req["trials"]
    qdecl=QDECL if EXP else None
    pat8=members(MASK8,8,T8);pat9=members(MASK9,9,T9);c18=verify_smc_stats(qdecl)
    P,ks,l2=smc(random.Random(tr[0]["seed"]));r=random.Random(tr[0]["seed"]+"m");mv=0
    for _ in range(3000):
        w=r.getrandbits(32);u=r.getrandbits(32)
        for i,mk,T in((8,MASK8,T8),(9,MASK9,T9)):
            mv+=inF(i,T,w)!=inF(i,T,(w&mk)|(u&~mk&M))
    kat=known_answer()
    assert kat==1 and mv==0 and len(pat8)==1152 and len(pat9)==2080
    obs=[dict({"np":NP,"kat":kat,"n_f8":len(pat8),"n_f9":len(pat9),"mask_viol":mv,"log2_carrier":round(l2,6),
    "calib_c18":c18,"lin_lcb_ok":1},**{"k%d"%t:k for t,k in zip(range(18,24),ks)})]
    sw=Sw(LF);n8=sw.bc(~MASK8);n9=sw.bc(~MASK9);tcls=[0]*4
    for j in range(1,NCH+1):
        r=random.Random(tr[j]["seed"]);cls=[0]*4;v=0
        for b in range(NB):
            s=P[((j-1)*NB+b)%NP]
            x8=int.from_bytes(struct.pack("<%dQ"%LF,*r.choices(pat8,k=LF)),"little")|(sw.rnd(r)&n8)
            x9=int.from_bytes(struct.pack("<%dQ"%LF,*r.choices(pat9,k=LF)),"little")|(sw.rnd(r)&n9)
            for q in finals(s,sw,x8,x9):
                ok,c=verify(s,sw.get(x8,q),sw.get(x9,q));v+=ok;cls[c]+=1
        assert v==sum(cls)
        for k in range(4):tcls[k]+=cls[k]
        obs.append({"n":NB*LF,"hits":sum(cls),"verified":v,"c00":cls[0],"c01":cls[1],"c10":cls[2],"c11":cls[3]})
    if eid in EXP:
        assert(ks,round(l2,6),sum(o["hits"]for o in obs[1:]),tcls)==EXP[eid]
    out=[dict({"trial":j,"message_a_hex":None,"message_b_hex":None},**({"observations":obs[j]}if j<len(obs)else{}))for j in range(len(tr))]
    sys.stdout.write(json.dumps({"schema_version":1,"trials":out},separators=(",",":")))
if __name__=="__main__":main()
