# PREM.H3 R2 (own recount of 595), R3 (controls: extreme-input run of the guard-bit scheme; same tracer on the unfolded circuit vs organizer 638)
import re, random, struct, collections
from common import *
R=rho
src=R._SRC.split('\n')[1:-2]   # body lines
print('batch body lines (after def, before return):',len(src))
cnt=collections.Counter()
for ln in src:
    rhs=ln.split('=',1)[1]
    ops=re.findall(r'>>|<<|\+|&|\||\^',rhs)
    assert len(ops)==1,ln
    cnt[{'+':'add','&':'and','|':'or','^':'xor','>>':'shr','<<':'shl'}[ops[0]]]+=1
print('R2 recount from the emitted source: total',sum(cnt.values()),dict(cnt),'; tracer says',R.PH,R.PH_BY)
assert dict(cnt)==R.PH_BY and sum(cnt.values())==R.PH
# per phase replay
class T2(R.Tracer): pass
tr=R.Tracer()
v=[("c",w) for w in R.IV]+[("c",w) for w in R.IV[:4]]+[("c",0),("c",0),("c",64),("c",11)]
m=[("c",0)]*8+[("v","i%d"%i,R.M32) for i in range(8,16)]
marks=[]
for rd in range(3):
    for j,(a,b,c,d) in enumerate(R.GCALLS):
        x,y=m[2*j],m[2*j+1]
        v[a]=tr.add(v[a],v[b],x); v[d]=tr.ror(tr.xor(v[d],v[a]),16); v[c]=tr.add(v[c],v[d]); v[b]=tr.ror(tr.xor(v[b],v[c]),12)
        v[a]=tr.add(v[a],v[b],y); v[d]=tr.ror(tr.xor(v[d],v[a]),8); v[c]=tr.add(v[c],v[d]); v[b]=tr.ror(tr.xor(v[b],v[c]),7)
        if j==3: marks.append(('r%d columns'%rd,tr.ops))
    marks.append(('r%d end'%rd,tr.ops)); m=[m[i] for i in R.PERM]
for i in range(8):
    z=tr.xor(v[i],v[i+8])
    if z[2]>R.M32: z=tr.mask(z)
marks.append(('digest',tr.ops))
prev=0
for n,o in marks: print('  ',n,'cumulative',o,'delta',o-prev); prev=o
# extreme inputs: guard-bit scheme must hold for any 32-bit lane content
random.seed(11)
vals=[0,1,0xFFFFFFFF,0x80000000,0x7FFFFFFF,0xAAAAAAAA,0x55555555]
bad=0; tot=0
def check(xs):
    global bad,tot
    out=R.batch(*R.pack_x(xs))
    for l in range(7):
        tot+=1
        if R.lane_x(out,l)!=R.f_scalar(xs[l],256): bad+=1
for a in vals:
    for b in vals:
        xs=[ sum((a if (i%2==0) else b)<<(32*i) for i in range(8)) for _ in range(7)]
        check(xs)
for _ in range(2000):
    xs=[ sum(random.choice(vals+[random.getrandbits(32)])<<(32*i) for i in range(8)) for _ in range(7)]
    check(xs)
print('extreme/structured inputs: lanes checked',tot,'mismatches vs scalar',bad)
# intermediates: no value exceeds 256 bits (machine word) on an all-ones input
env={f'i{i}':R.pack([0xFFFFFFFF]*7) for i in range(8,16)}
mx=0
for ln in src:
    lhs,rhs=ln.split('=',1); lhs=lhs.strip()
    val=eval(rhs,{},env); env[lhs]=val
    if '<<' not in rhs: mx=max(mx,val.bit_length())
print('max bit length of any non-shl intermediate on all-ones input:',mx,'(machine word 256)')
# R3 control: same tracer, unfolded circuit (IV, counters, flags and m0..m7 are variables), single lane = organizer-like generic compress
tr=R.Tracer()
v=[("v","cv%d"%i,R.M32) for i in range(8)]+[("v","iv%d"%i,R.M32) for i in range(4)]+[("v","t0",R.M32),("v","t1",R.M32),("v","b",R.M32),("v","f",R.M32)]
m=[("v","m%d"%i,R.M32) for i in range(16)]
for rd in range(3):
    for j,(a,b,c,d) in enumerate(R.GCALLS):
        x,y=m[2*j],m[2*j+1]
        v[a]=tr.add(v[a],v[b],x); v[d]=tr.ror(tr.xor(v[d],v[a]),16); v[c]=tr.add(v[c],v[d]); v[b]=tr.ror(tr.xor(v[b],v[c]),12)
        v[a]=tr.add(v[a],v[b],y); v[d]=tr.ror(tr.xor(v[d],v[a]),8); v[c]=tr.add(v[c],v[d]); v[b]=tr.ror(tr.xor(v[b],v[c]),7)
    m=[m[i] for i in R.PERM]
for i in range(8):
    z=tr.xor(v[i],v[i+8])
    if z[2]>R.M32: z=tr.mask(z)
print('control: unfolded generic 3-round compress counted with our tracer (5-op rotations, guard bits): total',tr.ops,tr.by,'; organizer reference_cost(blake3,3) = 638 (orgcount.out: 145 and, 97 shr, 96 add, 108 xor, 96 shl, 96 or)')
print('folded fixed-key circuit (our target): 595 per batch; per lane-step',595/7,'= %.4f unit; one lane alone 595 = %.4f unit'%(595/7/638,595/638))
