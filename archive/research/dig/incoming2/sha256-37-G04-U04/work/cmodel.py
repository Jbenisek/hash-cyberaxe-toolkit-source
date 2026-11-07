# own arithmetic: class-threshold / no-class model on the exact class table of G (classes.txt from gdump.c)
import math
p7=68157440/2**32; p6=287309824/2**32; C=2644.0
cl=[int(l.split()[1]) for l in open('classes.txt')]
cl.sort(reverse=True)
V0=sum(cl[:222]); assert V0==782800
# ledger components (proof 11): per first block, exact expectations
fixed_other=46+172          # first block, scalars/planes
test_per_batch=397          # class test incl. scan, per 256 lanes (conservative: scaled by batches)
per_pair=(16269.77+4879.12+233.31)/(V0*p7*p6)   # group+survivor+hit ops per good pair
cls_avg=24666.75/(222*p7)   # prep+runs+sweeps+W6+scans+reps+members per passing class (avg over the 222)
scan=21.14/(222*p7)
def ops(n,V,F,cost_model):
    # F: fixed part of class cost; linear part scales with class size
    avg=V/n
    tot=0
    # per-class cost of class i with size s
    return None
def eval_(n,F,mode='mix'):
    sizes=cl[:n]; V=sum(sizes)
    avg222=V0/222
    b=(cls_avg-F)/avg222
    clsc=sum(p7*(F+b*s+scan) for s in sizes)
    batches=math.ceil(n/256)
    o=fixed_other+test_per_batch*batches+clsc+per_pair*V*p7*p6
    cost=1+o/C
    return V,o,cost,math.log2(cost/V)
base=eval_(222,700)
print("baseline ops/FB (should be ~46685):",round(base[1],1),"units",round(base[2],3))
res={}
for F in (0,700,3000,7002):
    b=eval_(222,F); line=[]
    best=None
    for n in list(range(50,500,10))+[500,1000,2000,5000,10000,22976]:
        r=eval_(n,F)
        d=r[3]-b[3]
        if best is None or d<best[1]: best=(n,d,r[0])
        if n in (100,150,200,222,260,300,400,1000,5000,22976): line.append((n,r[0],round(d,4)))
    print("F=",F," best n,delta_bits,V:",best[0],round(best[1],4),best[2]," sweep:",line)
# no class grouping: per-variant F7 gate (bit-sliced, 256 lanes per batch), all of G or the 222-class family
for name,V in (("222-class family 782,800",V0),("all of G 12,103,680",sum(cl))):
    batches=math.ceil(V/256)
    o=fixed_other+test_per_batch*batches+(V*p7)*(cls_avg*0+0)+per_pair*V*p7*p6
    # after the gate each passing variant needs W6 test: use per-good-pair ~ (cls_avg*222*p7/(V0*p7*p6)) ops per good pair for W6 etc
    w6=24666.75/(V0*p7*p6)
    o+= w6*V*p7*p6
    cost=1+o/C
    print("NO CLASS GROUPING, variants",name,": ops/FB",round(o),"units",round(cost,1),"delta_bits vs baseline",round(math.log2(cost/V)-base[3],3))
print("ratio of ops: baseline",round(base[1]))
