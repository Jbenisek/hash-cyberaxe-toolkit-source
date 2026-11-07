"""blake3-r3 dig-scan: all numbers for the 18 round-0 steps C0..C3 q1-q4, D0 q1-q2. Own code. Output: scan_out.json"""
import sys, os, json, random
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
import b3steps as B
from b3steps import *

STEPS=[(0,c,q) for c in ("C0","C1","C2","C3") for q in (1,2,3,4)]+[(0,"D0",1),(0,"D0",2)]
FREE=set(range(8,16))
base_src,base_ops,base_by,base_rec,_=build()
vals={}; build(vals=vals)
res={"base_total":base_ops,"base_by":base_by,"steps":{}}

# scalar trace with prefix zero and a random x (constants must agree; variable outputs skipped)
rng=random.Random(11); tr_ok=True
for _ in range(20):
    msg=[0]*8+[rng.getrandbits(32) for _ in range(8)]
    tr={}; digest_words(msg,3,trace=tr)
    for k,vv in vals.items():
        if k[0]!=0: continue
        for got,exp in zip(vv,tr[k]):
            if got is not None and got!=exp: tr_ok=False
res["const_values_match_scalar_trace"]=tr_ok

# dependency sets on message words (taint through scalar structure)
def taint(rounds=1):
    v=[frozenset() for _ in range(16)]; m=[frozenset([i]) for i in range(16)]; dep={}
    for r in range(rounds):
        for j,(a,b,c,d) in enumerate(GC):
            x,y=m[2*j],m[2*j+1]
            v[a]=v[a]|v[b]|x; v[d]=v[d]|v[a]; dep[(r,NAMES[j],1)]=(v[a],v[d])
            v[c]=v[c]|v[d]; v[b]=v[b]|v[c]; dep[(r,NAMES[j],2)]=(v[c],v[b])
            v[a]=v[a]|v[b]|y; v[d]=v[d]|v[a]; dep[(r,NAMES[j],3)]=(v[a],v[d])
            v[c]=v[c]|v[d]; v[b]=v[b]|v[c]; dep[(r,NAMES[j],4)]=(v[c],v[b])
    return dep
dep=taint()

def ops_for(**kw):
    src,ops,by,rec,tr=build(**kw); return ops,rec

# --- Q2 variants
unf={}
for s in STEPS:
    ops,rec=ops_for(unfold={s}); unf[s]=(ops,rec[s][0],rec[s][1])
rand_total=set(); rand_step={s:set() for s in STEPS}; DR=300
rng=random.Random(2026)
for _ in range(DR):
    cs=[rng.getrandbits(32) for _ in range(8)]+[0]*8
    ops,rec=ops_for(consts=cs, ctr=0)
    rand_total.add(ops)
    for s in STEPS: rand_step[s].add(rec[s][0])
# prefix words made free (all 16 words variable) and counter/length random
allfree_ops,allfree_rec=ops_for(free=range(16))
# --- Q4 variants
pitchres={}
for P in (33,34,35,36):
    ops,rec=ops_for(pitch=P,lanes=7); pitchres[P]=(ops,{s:rec[s][0] for s in STEPS})
# no immediate merging (one op per constant operand, zero skipped)
class TrNoMerge(B.Tr):
    def add(s,*xs):
        vs=[x for x in xs if x[0]=="v"]; cs=[x[1] for x in xs if x[0]=="c" and x[1]]
        if not vs: return ("c",sum(x[1] for x in xs if x[0]=="c")&M32)
        acc=vs[0]
        for v in vs[1:]:
            while acc[2]+v[2]>=s.LIM:
                if acc[2]>=v[2]: acc=s.mask(acc)
                else: v=s.mask(v)
            acc=("v",s.emit("add","%s+%s"%(acc[1],v[1])),acc[2]+v[2])
        for c in cs:
            if acc[2]+c>=s.LIM: acc=s.mask(acc)
            acc=("v",s.emit("add","%s+%d"%(acc[1],s.REP*c)),acc[2]+c)
        return acc
_orig=B.Tr
B.Tr=TrNoMerge
nm_ops,nm_rec=ops_for()
B.Tr=_orig

# --- zero-immediate constructions for D0 (prefix would have to differ from 0^32; not available for the target)
def f_state(msg, upto):
    """state words v[0..15] after round-0 columns (all 4 column calls) for message msg[0..7]."""
    v=list(IV)+list(IV[:4])+[0,0,64,11]
    for j,(a,b,c,d) in enumerate(GC[:4]):
        x,y=msg[2*j],msg[2*j+1]
        v[a]=(v[a]+v[b]+x)&M32; v[d]=B._ror(v[d]^v[a],16); v[c]=(v[c]+v[d])&M32; v[b]=B._ror(v[b]^v[c],12)
        v[a]=(v[a]+v[b]+y)&M32; v[d]=B._ror(v[d]^v[a],8); v[c]=(v[c]+v[d])&M32; v[b]=B._ror(v[b]^v[c],7)
    return v
# D0 q1 immediate K = v0 + v5 (mod 2^32) after columns; want 0 by choosing m1 (m1 enters v0 additively only through C0 q3)
msg=[0]*8
v=f_state(msg,4); K=(v[0]+v[5])&M32
msg1=list(msg); msg1[1]=(-K)&M32   # v0 shifts by m1 (a2 = a1+b1+m1; later q4 outputs c2,b2 change but v0 itself is a2 -> unchanged elsewhere? recheck below)
v1=f_state(msg1,4)
zero_q1_ok=((v1[0]+v1[5])&M32)==0
# changing m1 also changes d2,c2,b2 of C0 but not v5 (C1 independent of C0) -> verify, then recount
cs=list(msg1)+[0]*8
ops_zq1,rec_zq1=ops_for(consts=cs)
# D0 q2 immediate = v10 after columns (c-out of C2): want 0 via m5 closed form
def solve_q2():
    v=list(IV)+list(IV[:4])+[0,0,64,11]
    a,b,c,d=GC[2]; x=0
    A=(v[a]+v[b]+x)&M32; D=B._ror(v[d]^A,16); C=(v[c]+D)&M32; Bv=B._ror(v[b]^C,12)
    # a2=A+Bv+m5 ; d2=ror8(D^a2); c2=C+d2 ; want c2=0 -> d2=-C -> D^a2=rol8(-C)
    d2=(-C)&M32; t=B._ror(d2,24)           # rol 8 == ror 24
    a2=t^D; m5=(a2-A-Bv)&M32
    return m5
m5=solve_q2()
msg2=[0]*8; msg2[5]=m5; v2=f_state(msg2,4)
zero_q2_ok=(v2[10]==0)
ops_zq2,rec_zq2=ops_for(consts=msg2+[0]*8)
# both together (m1 and m5 are independent: C0 vs C2 calls)
msg3=[0]*8; msg3[1]=msg1[1]; msg3[5]=m5; v3=f_state(msg3,4)
zero_both_ok=((v3[0]+v3[5])&M32)==0 and v3[10]==0
ops_zboth,rec_zboth=ops_for(consts=msg3+[0]*8)
zero_chk=B.check(build(consts=msg3+[0]*8)[0],3,36,7,FREE,consts=msg3+[0]*8)

res.update({
 "unfold":{f"{s[1]}.q{s[2]}":unf[s] for s in STEPS},
 "rand_prefix_draws":DR,"rand_total_set":sorted(rand_total),
 "rand_step_sets":{f"{s[1]}.q{s[2]}":sorted(rand_step[s]) for s in STEPS},
 "allfree_total":allfree_ops,"allfree_step":{f"{s[1]}.q{s[2]}":allfree_rec[s][0] for s in STEPS},
 "pitch":{P:{"total":pitchres[P][0],"step":{f"{s[1]}.q{s[2]}":pitchres[P][1][s] for s in STEPS}} for P in pitchres},
 "nomerge_total":nm_ops,"nomerge_step":{f"{s[1]}.q{s[2]}":nm_rec[s][0] for s in STEPS},
 "base_step":{f"{s[1]}.q{s[2]}":(base_rec[s][0],base_rec[s][1]) for s in STEPS},
 "base_vals":{f"{s[1]}.q{s[2]}":[None if x is None else "%08x"%x for x in vals[s]] for s in STEPS},
 "dep":{f"{s[1]}.q{s[2]}":[sorted(x) for x in dep[s]] for s in STEPS},
 "zero":{"K_D0q1":"%08x"%K,"m1_for_zero":"%08x"%msg1[1],"zero_q1_ok":zero_q1_ok,"ops_q1":ops_zq1,"step_q1":rec_zq1[(0,"D0",1)],
         "m5_for_zero":"%08x"%m5,"zero_q2_ok":zero_q2_ok,"ops_q2":ops_zq2,"step_q2":rec_zq2[(0,"D0",2)],
         "both_ok":zero_both_ok,"ops_both":ops_zboth,"both_circuit_correct":zero_chk,
         "v15_after_cols":"%08x"%f_state([0]*8,4)[15],"v5_after_cols":"%08x"%f_state([0]*8,4)[5],"v10_after_cols":"%08x"%f_state([0]*8,4)[10],"v0_after_cols":"%08x"%f_state([0]*8,4)[0]},
})
json.dump(res,open(os.path.join(HERE,"scan_out.json"),"w"),indent=1)
print(json.dumps({k:res[k] for k in ("base_total","const_values_match_scalar_trace","allfree_total","nomerge_total","rand_total_set","zero")},indent=1))
print("unfold",{k:(v[0],v[1]) for k,v in res["unfold"].items()})
print("pitch totals",{P:res["pitch"][P]["total"] for P in res["pitch"]})
