# Q1: factor C = (p-1)/(2^32*3*463) with sympy ECM (time-limited). Prints pieces as found.
import time,sys
from sympy import isprime
from sympy.ntheory import ecm, factorint
C=4852402207910482324454106387152561316357015077916052529702775169
p=0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
assert (p-1)==2**32*3*463*C
print("C prime?",isprime(C),flush=True)
t0=time.time(); LIMIT=float(sys.argv[1]) if len(sys.argv)>1 else 1500
todo=[C]; prime=[]
# small trial division first
from sympy import primerange
for q in primerange(2,10**7):
    while todo[0]%q==0: todo[0]//=q; prime.append(q); print("small",q,flush=True)
todo=[x for x in todo if x>1]
B1=2000
while todo and time.time()-t0<LIMIT:
    n=todo.pop()
    if isprime(n): prime.append(n); print("PRIME",n,flush=True); continue
    try:
        fs=ecm(n,B1=B1,B2=B1*100,max_curve=200)
    except Exception as e:
        fs=set(); 
    fs=set(fs)
    if len(fs)>1 or (fs and list(fs)[0]!=n):
        for f in fs:
            print("found",f,"bits",f.bit_length(),flush=True); todo.append(f)
    else:
        todo.append(n); B1*=2; print("B1->",B1,"t",int(time.time()-t0),flush=True)
        if B1>2*10**6: break
print("DONE primes",prime,"remaining",todo,"elapsed",time.time()-t0)
