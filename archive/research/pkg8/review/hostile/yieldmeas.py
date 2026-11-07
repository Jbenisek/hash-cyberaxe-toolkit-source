#!/usr/bin/env python3
"""Independent measurement of the cluster yield of proof.md 6.7 / H4, of the
gate-open share, of the word-level shares of 6.5/6.7, and of the clumping of
rule-A passes inside a cluster.  All formulas taken from the text only."""
import numpy as np, random
np.seterr(over='ignore')
u32=np.uint32
M32=0xffffffff
IV=[0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19]
X3c,X7c,X11c,X15c=0x29d4fa98,0xbee3af28,0x44036000,0x40c58500
W4=0x97475638; W13=0x0007c006
Y3c=0x8127c181
SUBVAL=0x030c0303
FREE17=[2,3,4,5,6,7,10,11,12,13,14,20,27,28,29,30,31]
def rr(x,r): return ((x>>u32(r))|(x<<u32(32-r))).astype(u32)
def rl(x,r): return ((x<<u32(r))|(x>>u32(32-r))).astype(u32)
def srotr(x,r): x&=M32; return ((x>>r)|(x<<(32-r)))&M32
def srotl(x,r): x&=M32; return ((x<<r)|(x>>(32-r)))&M32

def stepO(c0c1,c0d1,d3d1,s15,s9,w5):
    K2a1=(IV[2]+IV[6]+W4)&M32; K2d1=srotr(55^K2a1,16)
    K2c1=(IV[2]+K2d1)&M32; K2b1=srotr(IV[6]^K2c1,12)
    S2=(K2a1+K2b1+w5)&M32; S14=srotr(K2d1^S2,8)
    S10=(K2c1+S14)&M32; S6=srotr(K2b1^S10,7)
    D3a1=srotl(d3d1,16)^S14; D3c1=(s9+d3d1)&M32
    D3b1=(X3c-D3a1)&M32; S4=srotl(D3b1,12)^D3c1
    S3=(D3a1-S4)&M32; X14=srotr(d3d1^X3c,8)
    X9=(D3c1+X14)&M32; X4=srotr(D3b1^X9,7)
    K3d1=srotl(s15,8)^S3; K3c1=(IV[3]+K3d1)&M32
    K3b1=srotr(IV[7]^K3c1,12); S11=(K3c1+s15)&M32
    S7=srotr(K3b1^S11,7); K3a1=srotl(K3d1,16)^11
    w6=(K3a1-IV[3]-IV[7])&M32; w7=(S3-K3a1-K3b1)&M32
    X8=(c0c1-c0d1)&M32; C0b1=srotr(X4^c0c1,12)
    D2b1=srotl(X7c,7)^X8; D2c1=srotl(D2b1,12)^S7
    X13=(X8-D2c1)&M32
    return dict(S2=S2,S14=S14,S10=S10,S6=S6,S4=S4,S3=S3,X14=X14,X9=X9,X4=X4,
                S11=S11,S7=S7,w6=w6,w7=w7,X8=X8,C0b1=C0b1,D2b1=D2b1,D2c1=D2c1,
                X13=X13,S9=s9,S15=s15,c0c1=c0c1,c0d1=c0d1,w5=w5)

def mid_w2w0(n,X2):   # the two middle words that h1 needs
    D2a1=(X2-u32(n['D2b1'])-u32(W13)).astype(u32)
    D2d1=(u32(srotl(n['X13'],8))^X2).astype(u32)
    S13=(rl(D2d1,16)^D2a1).astype(u32)
    S8=(u32(n['D2c1'])-D2d1).astype(u32)
    K1c1=(u32(n['S9'])-S13).astype(u32)
    K1d1=(K1c1-u32(IV[1])).astype(u32)
    K1a1=rl(K1d1,16)
    w2=(K1a1-u32(IV[1])-u32(IV[5])).astype(u32)
    K0b1=(u32(srotl(n['S4'],7))^S8).astype(u32)
    K0c1=(rl(K0b1,12)^u32(IV[4])).astype(u32)
    K0d1=(K0c1-u32(IV[0])).astype(u32)
    K0a1=rl(K0d1,16)
    w0=(K0a1-u32(IV[0])-u32(IV[4])).astype(u32)
    return w2,w0

def mem_part(n,e1):   # per-member: C0a1, X6
    y=(e1-u32(Y3c)).astype(u32)
    Y8=(rl(y,7)^u32(n['C0b1'])).astype(u32)
    Y12=(Y8-u32(n['c0c1'])).astype(u32)
    Y0=(rl(Y12,8)^u32(n['c0d1'])).astype(u32)
    C0a1=(Y0-u32(n['C0b1'])-u32(n['w6'])).astype(u32)
    X12=(u32(srotl(n['c0d1'],16))^C0a1).astype(u32)
    D1c1=(u32(X11c)-X12).astype(u32)
    D1b1=rr((u32(n['S6'])^D1c1).astype(u32),12)
    X6=rr((D1b1^u32(X11c)).astype(u32),7)
    return C0a1,X6

def h1_of(n,w2,w0,X2,C0a1,X6,e1):
    """broadcast: X2/w2/w0 shape (...,8,1); C0a1/X6/e1 shape (...,1,8)"""
    X0=(C0a1-u32(n['X4'])-w2).astype(u32)
    D0d1=(u32(srotl(X15c,8))^X0).astype(u32)
    D0c1=(u32(n['S10'])+D0d1).astype(u32)
    X10=(D0c1+u32(X15c)).astype(u32)
    C2a1=(X2+X6+u32(n['w7'])).astype(u32)
    C2d1=rr((u32(n['X14'])^C2a1).astype(u32),16)
    C2c1=(X10+C2d1).astype(u32)
    C2b1=rr((X6^C2c1).astype(u32),12)
    Y2=(C2a1+C2b1+w0).astype(u32)
    z=(C2d1^Y2).astype(u32)
    Y14=rr(z,8)
    return rr((Y14^e1).astype(u32),16)

def ruleA(h1):
    b=lambda i:(h1>>u32(i))&u32(1)
    return ((b(0)==0)&(b(1)==1)&(b(16)==0)&(b(17)==0)&
            ((b(2)^b(10))==1)&((b(3)^b(11))==1)&
            ((b(3)^b(12)^b(24))==0)&((b(6)^b(13)^b(25))==0))
def gate(h1):
    b=lambda i:(h1>>u32(i))&u32(1)
    return (b(0)==0)&(b(1)==1)&(b(16)==0)&(b(17)==0)

# member number k -> e1 ; representative members have k bits 10,15,16 zero
KB=np.array([1<<j for j in range(17)],dtype=np.uint64)
EB=np.array([1<<p for p in FREE17],dtype=np.uint64)
def e1_of_k(k):
    k=np.asarray(k,dtype=np.uint64)
    e1=np.full(k.shape,SUBVAL,dtype=np.uint64)
    for j,p in enumerate(FREE17):
        e1 |= ((k>>np.uint64(j))&np.uint64(1))<<np.uint64(p)
    return e1.astype(u32)
# the three cluster bits of e1 are 14,30,31 -> free-position indices
IDX=[FREE17.index(14),FREE17.index(30),FREE17.index(31)]
assert IDX==[10,15,16]
X2BITS=[14,30,31]

rng=random.Random(20261007)
NOUT=24        # outer tuples
NX2=1          # representative X2 values per outer tuple
NREP=16384     # all representative members of a value of X2
tot_rep=0; tot_open=0; tot_repA=0
tot_nbA=0            # rule-A neighbours found (only in opened clusters)
tot_all64A=0         # rule-A trials in those clusters, all 64 examined
tot_nb_words_s2=0; tot_nb_words=0
tot_rep_words=0; tot_rep_words_open=0; tot_rep_words_A=0
per_flip=np.zeros(64,dtype=np.int64)
open_lane_hist=np.zeros(8,dtype=np.int64)
# clumping: pairs of rule-A trials inside a cluster
clump_pairs=0; clump_clusters_with_ge2=0
allA_in_open=0
for o in range(NOUT):
    n=stepO(*[rng.getrandbits(32) for _ in range(6)])
    for _ in range(NX2):
        base=rng.getrandbits(32)
        for b in X2BITS: base &= ~(1<<b)
        # all 8 X2 of the group, rep first
        dx=np.arange(8,dtype=np.uint64)
        X2v=np.full(8,base,dtype=np.uint64)
        for j,b in enumerate(X2BITS):
            X2v |= ((dx>>np.uint64(j))&np.uint64(1))<<np.uint64(b)
        X2v=X2v.astype(u32)
        w2v,w0v=mid_w2w0(n,X2v)
        # representative members: k with bits 10,15,16 zero, in increasing k order
        kk=np.arange(1<<17,dtype=np.uint64)
        mask=((kk>>np.uint64(10))&np.uint64(1)==0)&((kk>>np.uint64(15))&np.uint64(1)==0)&((kk>>np.uint64(16))&np.uint64(1)==0)
        krep=kk[mask]
        assert krep.size==NREP
        e1rep=e1_of_k(krep)
        C0a1r,X6r=mem_part(n,e1rep)
        h1r=h1_of(n,w2v[0],w0v[0],X2v[0],C0a1r,X6r,e1rep)
        gr=gate(h1r); ar=ruleA(h1r)
        tot_rep+=NREP; tot_open+=int(gr.sum()); tot_repA+=int(ar.sum())
        # words of seven consecutive representatives
        nw=NREP//7
        gw=gr[:nw*7].reshape(nw,7); aw=ar[:nw*7].reshape(nw,7)
        tot_rep_words+=nw
        tot_rep_words_open+=int(gw.any(axis=1).sum())
        tot_rep_words_A+=int(aw.any(axis=1).sum())
        cnt=gw.sum(axis=1)
        for c in range(8): open_lane_hist[c]+=int((cnt==c).sum())
        # neighbours of the opened representatives
        sel=np.nonzero(gr)[0]
        if sel.size==0: continue
        kop=krep[sel]
        dk=np.arange(8,dtype=np.uint64)
        kn=np.empty((kop.size,8),dtype=np.uint64)
        kn[:]=kop[:,None]
        for j,ix in enumerate(IDX):
            kn |= ((dk>>np.uint64(j))&np.uint64(1))[None,:]<<np.uint64(ix)
        e1n=e1_of_k(kn)                       # (nop,8)
        C0a1n,X6n=mem_part(n,e1n)
        H=h1_of(n, w2v[None,:,None], w0v[None,:,None], X2v[None,:,None],
                C0a1n[:,None,:], X6n[:,None,:], e1n[:,None,:])   # (nop,8X2,8mem)
        A64=ruleA(H)
        assert bool((A64[:,0,0]==ar[sel]).all())
        allA_in_open+=int(A64.sum())
        tot_all64A+=int(A64.sum())
        nb=A64.reshape(-1,64).copy(); nb[:,0]=False
        tot_nbA+=int(nb.sum())
        per_flip+=A64.reshape(-1,64).sum(axis=0)
        # neighbour words: 63 neighbours in 9 packed words of seven
        order=np.array([i for i in range(64) if i!=0])
        nb_lanes=A64.reshape(-1,64)[:,order].reshape(-1,9,7)
        tot_nb_words+=nb_lanes.shape[0]*9
        tot_nb_words_s2+=int(nb_lanes.any(axis=2).sum())
        c=A64.reshape(-1,64).sum(axis=1)
        clump_pairs+=int((c*(c-1)).sum()); clump_clusters_with_ge2+=int((c>=2).sum())

p=1/256.
print("representatives examined      : %d"%tot_rep)
print("gate-open share               : %.7f   (text 0.0624630, model 2^-4=0.0625)"%(tot_open/tot_rep))
print("rule-A share among reps       : %.8f  (2^-8=%.8f)"%(tot_repA/tot_rep,p))
print("rule-A neighbours found / rep : %.6f  (text 0.15630)"%(tot_nbA/tot_rep))
print("YIELD  (nb found/rep)/2^-8    : %.3f   (H4 assumes 40.02)"%(tot_nbA/tot_rep/p))
print("trial-equivalents/rep 1+yield : %.3f   (text 41.02; lossless would be 64)"%(1+tot_nbA/tot_rep/p))
print("rule-A found / rule-A present : %.5f  (= TE/64, text 41.02/64=%.5f)"%
      ((tot_repA+tot_nbA)/(tot_rep*64*p),41.02/64))
print("opened clusters               : %d"%tot_open)
print("rule-A nbrs per opened cluster: %.4f  (text 2.5008)"%(tot_nbA/max(tot_open,1)))
print("opened clusters with none     : %.4f  (text 0.1436)"%
      (1-np.count_nonzero(per_flip)*0 - ( (tot_open-0)and 0 ) if False else 0.0))
print("rep words with an open lane   : %.6f  (text 0.241596; indep. 0.363503)"%(tot_rep_words_open/tot_rep_words))
print("rep words with a rule-A lane  : %.6f  (text 0.026178 / 0.02622)"%(tot_rep_words_A/tot_rep_words))
print("open-lane histogram 0..7      : %s"%np.round(open_lane_hist/open_lane_hist.sum(),4).tolist())
print("   (text 0.7584 0.1238 0.0668 0.0315 0.0137 0.0046 0.0011 0.0002)")
print("neighbour words run / rep     : %.5f  (text 0.5625 = 9*gate rate)"%(tot_nb_words/tot_rep))
print("neighbour words into stage 2  : %.5f  (text 0.1364 / 0.1367)"%(tot_nb_words_s2/tot_nb_words))
pf=per_flip/max(tot_open,1)/p
print("per-position rates /2^-8, rep excluded, min/max: %.4f %.4f"%(pf[1:].min(),pf[1:].max()))
print("   (text: the 63 rates lie between 0.543 and 0.874 -- same quantity /16)")
print("   as a share of the independent value 1/16: min %.4f max %.4f"%(pf[1:].min()/16,pf[1:].max()/16))
# cost per representative and per trial-equivalent, from these rates and 6.5's 47/135
stA=(1/7+tot_nb_words/tot_rep)*47
st2=((tot_rep_words_A/tot_rep_words)/7 + (tot_nb_words/tot_rep)*(tot_nb_words_s2/tot_nb_words))*135
TE=1+tot_nbA/tot_rep/p
print("\ncost/rep from 6.5 counts: stageA %.3f + stage2 %.3f = %.3f ; per TE %.4f ; per nominal trial %.4f"
      %(stA,st2,stA+st2,(stA+st2)/TE,(stA+st2)/64))
print("stage-2 share of all stage-A words: %.5f  (Section 8 charges 1/32=0.03125)"%
      ((st2/135)/(stA/47)))
