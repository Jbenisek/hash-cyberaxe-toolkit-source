# Q1b: with C = q1*q2 known, get ord_q(5) for each prime q | p-1 (needs factoring q-1), cycle spectrum of x->x^5 on F_p.
import time, gmpy2
from sympy import factorint, isprime
from sympy.ntheory import ecm
from math import gcd
p=0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
q1=539204044132271846773; q2=8999194758858563409123804352480028797519453
C=4852402207910482324454106387152561316357015077916052529702775169
print("q1*q2==C:",q1*q2==C, " p-1 == 2^32*3*463*q1*q2:", p-1==2**32*3*463*q1*q2)
print("q1 prime (gmpy2 is_prime 50 rounds, sympy):",gmpy2.is_prime(q1,50),isprime(q1))
print("q2 prime:",gmpy2.is_prime(q2,50),isprime(q2))
t0=time.time()
def fac(n,limit=400):
    # full factorisation using trial division + sympy factorint (rho/pm1) + ecm fallback
    out={}
    todo=[n]
    from sympy import primerange
    for s in primerange(2,10**6):
        while todo[0]%s==0: todo[0]//=s; out[s]=out.get(s,0)+1
    todo=[x for x in todo if x>1]
    B1=2000
    while todo and time.time()-t0<limit:
        m=todo.pop()
        if isprime(m): out[m]=out.get(m,0)+1; continue
        fs=set(ecm(m,B1=B1,B2=B1*100,max_curve=100))
        if len(fs)>1 or (fs and list(fs)[0]!=m):
            todo+=list(fs)
        else:
            todo.append(m); B1*=2
    return out,todo
for name,q in (("q1",q1),("q2",q2)):
    f,rest=fac(q-1)
    print(name,"-1 factorisation:",f,"unfactored:",rest,flush=True)
    if rest: continue
    # multiplicative order of 5 mod q
    o=q-1
    for pr in f:
        while o%pr==0 and pow(5,o//pr,q)==1: o//=pr
    print(name,"ord_q(5) =",o,"factored:",fac(o)[0], " (q-1)/ord =",(q-1)//o, flush=True)
