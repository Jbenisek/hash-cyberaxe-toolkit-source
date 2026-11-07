import sys, time, flint
from u5_lib import P
p=P
known_small=[2,3,463,43,257,73,5839,12221196943,5187662682403,25457]
def strip(n, primes):
    for q in primes:
        while n%q==0: n//=q
    return n
C   = strip(p-1,[2,3,463])
Cp  = strip(p+1,[2,43,257,25457])
Cpp = strip(p*p+p+1,[3,73,5839,12221196943,5187662682403])
print("C bits",C.bit_length(),"C' bits",Cp.bit_length(),"C'' bits",Cpp.bit_length(), flush=True)
for name,n in [("C",C),("C''",Cpp),("C'",Cp)]:
    print(name,"probable prime:",flint.fmpz(n).is_probable_prime(), flush=True)
bits=int(sys.argv[1]) if len(sys.argv)>1 else 40
for name,n in [("C",C),("C''",Cpp)]:
    t=time.time()
    f=flint.fmpz(n).factor_smooth(bits, proved=False)
    print(name,"factor_smooth(%d bits) after %.1fs ->"%(bits,time.time()-t), [(str(a),b) for a,b in f], flush=True)
