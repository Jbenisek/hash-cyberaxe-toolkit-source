"""Exact GF(2) accounting of the leader's prefix conditions (own code). Forms are python ints: bit k<1080 = message bit k, bit 1080 = constant."""
import sys, json
sys.path.insert(0,'.')
from kk6 import RHO, PAD16
CB=1080
def ROT(i,n): return i  # placeholder
class Elim:
    def __init__(s): s.b={}  # pivot(highest var bit) -> row
    def reduce(s,r):
        while True:
            v=r&((1<<CB)-1)
            if v==0: return r
            p=v.bit_length()-1
            if p in s.b: r^=s.b[p]
            else: return r
    def add(s,r):
        r=s.reduce(r); v=r&((1<<CB)-1)
        if v==0: return 'dup' if r==0 else 'INCONSISTENT'
        s.b[v.bit_length()-1]=r; return 'new'
    def rank(s): return len(s.b)
    def implied(s,r): return s.reduce(r)==0
# initial state forms: lane l bit b
F=[[0]*64 for _ in range(25)]
for l in range(17):
    for b in range(64):
        k=64*l+b
        if k<1080: F[l][b]=1<<k
        elif k in (1080+1,1080+2,1080+7): F[l][b]=1<<CB   # byte 135 = 0x86 : bits 1,2,7 -> state bits 1081,1082,1087
# fix: lane16 bits 57,58,63 are pad
F16=[0]*64
for b in range(64):
    k=64*16+b
    F16[b]=(1<<k) if k<1080 else 0
for b in (57,58,63): F16[b]=1<<CB
F[16]=F16
def theta_forms(F):
    C=[[F[x][b]^F[x+5][b]^F[x+10][b]^F[x+15][b]^F[x+20][b] for b in range(64)] for x in range(5)]
    D=[[C[(x-1)%5][b]^C[(x+1)%5][(b-1)%64] for b in range(64)] for x in range(5)]
    return [[F[i][b]^D[i%5][b] for b in range(64)] for i in range(25)]
def rhopi_forms(F):
    B=[None]*25
    for x in range(5):
        for y in range(5):
            r=RHO[x+5*y]; src=F[x+5*y]
            B[y+5*((2*x+3*y)%5)]=[src[(b-r)%64] for b in range(64)]
    return B
T1=theta_forms(F); B1=rhopi_forms(T1)   # chi1 input forms
# --- leader's conditions on the message (groups)
groups={}
g=[]
for b in range(64):
    if 64*16+b<1080: g.append(F[16][b])       # message bytes 128..134 of lane16 = 0  (bits 0..55)
groups['lane16_msg_zero']=[x for x in g if x&((1<<CB)-1)]
groups['L8_zero']=[F[8][b] for b in range(64)]
# L5 = C4 ^ rot(C1,1) ; L15 = same; L12 = ~rot(C4,1) ^ L2 ^ L7
def lane_xor(*ls): return [ (lambda b: __import__('functools').reduce(lambda a,c:a^c,[l[b] for l in ls]))(b) for b in range(64)]
C4=lane_xor(F[4],F[9],F[14]); C1=lane_xor(F[1],F[6],F[11],F[16])
rotC1=[C1[(b-1)%64] for b in range(64)]
rotC4=[C4[(b-1)%64] for b in range(64)]
groups['L5_eq']=[F[5][b]^C4[b]^rotC1[b] for b in range(64)]
groups['L15_eq']=[F[15][b]^C4[b]^rotC1[b] for b in range(64)]
groups['L12_eq(D3=ones)']=[F[12][b]^rotC4[b]^F[2][b]^F[7][b]^(1<<CB) for b in range(64)]
allE=Elim(); out={}
for name,rows in groups.items():
    e=Elim(); st=[e.add(r) for r in rows]
    out[name]=dict(rows=len(rows),rank_alone=e.rank(),inconsistent=st.count('INCONSISTENT'))
    for r in rows: allE.add(r)
out['ALL_leader_conditions']=dict(rank=allE.rank(),message_dim=1080-allE.rank())
print(json.dumps(out,indent=1))
# --- needed conditions derived from the z-directions themselves
need={}  # neighbor input bits: (Bidx,plane,value)
def neigh(Bidx,p):
    X=Bidx%5;Y=Bidx//5
    return (((X+1)%5)+5*Y,p,0),(((X+4)%5)+5*Y,p,1)
for j in range(32):
    # lane4 -> B lane (X=0,Y=3), plane j+27 ; lane14 -> (X=2,Y=4) plane j+39
    for Bidx,p in ((0+5*3,(j+27)%64),(2+5*4,(j+39)%64)):
        for (nb,pp,val) in neigh(Bidx,p): need[(nb,pp)]=val
print("neighbor chi1-input bits needed constant:",len(need))
byword={}
for (nb,pp),val in need.items(): byword.setdefault((nb,val),[]).append(pp)
print({k:len(v) for k,v in byword.items()})
# map B words to original lanes
inv={}
for x in range(5):
    for y in range(5): inv[y+5*((2*x+3*y)%5)]=x+5*y
print("neighbor words come from lanes (after theta):",{k:(inv[k[0]],len(v)) for k,v in byword.items()})
needE=Elim(); res=[]
need_rows=[]
for (nb,pp),val in need.items():
    f=B1[nb][pp]; need_rows.append(f^(val<<CB))   # f==val  <=> f^val ==0 ; constant bit toggles by val
needrank_by={}
for k,v in byword.items():
    e=Elim()
    for pp in v:
        e.add(B1[k[0]][pp]^(k[1]<<CB))
    needrank_by[str(k)]=e.rank()
for r in need_rows: res.append(needE.add(r))
print("needed eq rank (all %d neighbor bits):"%len(need_rows),needE.rank(),"inconsistent:",res.count('INCONSISTENT'),"dup:",res.count('dup'))
print("per neighbor word rank:",needrank_by)
imp=all(allE.implied(r) for r in need_rows)
print("all needed equations implied by the leader's 312 conditions:",imp)
# which needed equations are NOT implied by group-subsets (necessity of groups, exact)
import itertools
names=list(groups)
tbl={}
for drop in names:
    e=Elim()
    for nm in names:
        if nm!=drop:
            for r in groups[nm]: e.add(r)
    miss=sum(1 for r in need_rows if not e.implied(r))
    tbl[drop]=dict(rank_without=e.rank(),needed_eqs_not_implied=miss,of=len(need_rows))
print("drop-one-group (exact linear): ",json.dumps(tbl))
# minimal: only needed eqs
out['needed_neighbor_bits']=len(need_rows); out['needed_rank']=needE.rank(); out['needed_by_word_rank']=needrank_by
out['needed_implied_by_leader']=imp; out['drop_one_exact']=tbl
json.dump(out,open('t2_conditions_out.json','w'),indent=1)
