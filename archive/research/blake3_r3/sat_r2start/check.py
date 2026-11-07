# encoding check: fix a random valid pair; numpy HW h after 2 rounds; CNF must be SAT at W=h, UNSAT at W=h-1
import sys, json, random, subprocess, numpy as np
sys.path.insert(0, sys.argv[1]); import b3
M=np.uint32; random.seed(7)
m=[random.getrandbits(32) for _ in range(16)]; m[13]&=0xffffff; m[14]=m[15]=0
t0=random.getrandbits(32); t1=random.getrandbits(20)
K=(0x3C6EF372+0x1F83D9AB)&0xffffffff
w4b=(((K+m[4])^8)-K)&0xffffffff; w5b=(m[5]+m[4]-w4b)&0xffffffff
mB=list(m); mB[4]=w4b; mB[5]=w5b
def run(mm,blen):
    v=[np.full(1,x,dtype=M) for x in b3.IV+b3.IV[:4]+[t0,t1,blen,3]]; mm=[np.full(1,x,dtype=M) for x in mm]; s=[]
    for r in range(2): b3.rnd(v,mm); s.append([int(x[0]) for x in v]); mm=b3.perm(mm)
    return s
with np.errstate(over='ignore'): A=run(m,55); B=run(mB,63)
print('round0 equal', A[0]==B[0])
h=sum(bin(x^y).count('1') for x,y in zip(A[1],B[1])); print('h',h)
for W in (h,h-1):
    subprocess.run(['python3','gen.py',str(W),'chk.cnf'],check=True)
    mp=json.load(open('chk.cnf.map')); units=[]
    for name,val in [('t0',t0),('t1',t1)]+[(('m',i),m[i]) for i in range(16)]:
        bits=mp['m'][name[1]] if isinstance(name,tuple) else mp[name]
        units+=[[b if (val>>i)&1 else -b] for i,b in enumerate(bits)]
    lines=open('chk.cnf').read().split('\n'); hdr=lines[0].split()
    body='\n'.join(lines[1:])+''.join(f'{u[0]} 0\n' for u in units)
    open('chk2.cnf','w').write(f'p cnf {hdr[2]} {int(hdr[3])+len(units)}\n'+body)
    r=subprocess.run(['kissat','-q','chk2.cnf'],capture_output=True,text=True)
    print('W',W,'rc',r.returncode)
