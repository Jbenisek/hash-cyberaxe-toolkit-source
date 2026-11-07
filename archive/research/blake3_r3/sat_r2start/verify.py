import sys, json, numpy as np
sys.path.insert(0, sys.argv[3]); import b3
M=np.uint32
mp=json.load(open(sys.argv[1]+'.map')); val={}
for line in open(sys.argv[2]):
    if line.startswith('v'):
        for x in line.split()[1:]:
            x=int(x); val[abs(x)]=x>0
w=lambda bits: sum((1<<i) for i,b in enumerate(bits) if val.get(b,False))
m=[w(x) for x in mp['m']]; t0=w(mp['t0']); t1=w(mp['t1'])
mB=list(m); mB[4]=w(mp['w4b']); mB[5]=w(mp['w5b'])
def run(mm,blen):
    v=[np.full(1,x,dtype=M) for x in b3.IV+b3.IV[:4]+[t0,t1,blen,3]]
    mm=[np.full(1,x,dtype=M) for x in mm]; snaps=[]
    for r in range(3):
        b3.rnd(v,mm); snaps.append([int(x[0]) for x in v]); mm=b3.perm(mm)
    return snaps
with np.errstate(over='ignore'):
    A=run(m,55); B=run(mB,63)
hw=lambda a,b: sum(bin(x^y).count('1') for x,y in zip(a,b))
print('msgA',[hex(x) for x in m],'t',hex(t0),hex(t1),'w4b',hex(mB[4]),'w5b',hex(mB[5]))
for r in range(3): print('after round',r+1,'state diff HW',hw(A[r],B[r]),'active words',sum(1 for x,y in zip(A[r],B[r]) if x!=y))
dA=[A[2][i]^A[2][i+8] for i in range(8)]; dB=[B[2][i]^B[2][i+8] for i in range(8)]
print('3-round CV diff HW',hw(dA,dB),'words equal',sum(1 for x,y in zip(dA,dB) if x==y))
