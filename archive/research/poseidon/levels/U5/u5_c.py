from u5_lib import *
import flint, time
T,S,D = charpoly(MDS); K=F3(T,S,D); al=(0,1,0)
p=P
print("is 5187662682403 prime:", flint.fmpz(5187662682403).is_probable_prime())
print("v3(p-1)=",next(k for k in range(1,9) if (p-1)%3**(k+1)),"; v3(p^2+p+1)=",next(k for k in range(1,9) if (p*p+p+1)%3**(k+1)))
n=p**3-1
small={2:32,3:2,463:1,73:1,5839:1,12221196943:1,5187662682403:1}
Ns=1
for q,e in small.items(): Ns*=q**e
U=n//Ns
assert n%Ns==0
C=(p-1)//(2**32*3*463); Cpp=(p*p+p+1)//(3*73*5839*12221196943*5187662682403)
assert U==C*Cpp and Ns*U==n
print("Ns bits",Ns.bit_length(),"U bits",U.bit_length(),"C bits",C.bit_length(),"C'' bits",Cpp.bit_length())
one=K.one()
print("--- order of alpha (= order of M) ---")
print("alpha^n == 1:",K.pw(al,n)==one)
ordsm=1
for q,e in small.items():
    # exact order of the q-part: smallest f with (alpha^(n/q^e))^(q^f)==1
    g=K.pw(al,n//q**e); f=0
    while g!=one: g=K.pw(g,q); f+=1
    print(f"  q={q}: exponent of q in ord(alpha) = {f} (max possible {e})")
    ordsm*=q**f
print("  smooth part of order of M =",ordsm,"= 2^? ...",ordsm.bit_length(),"bits; full smooth group order Ns bits",Ns.bit_length())
gC=K.pw(al,n//C); gCpp=K.pw(al,n//Cpp)
print("  alpha^(n/C)==1 (C-part of order trivial)?:",gC==one)
print("  alpha^(n/C'')==1 (C''-part trivial)?:",gCpp==one)
# order in projective group: image in F_{p^3}^*/F_p^*, order divides p^2+p+1
m=p*p+p+1
print("--- projective order (order of M modulo scalars) divides p^2+p+1 ---")
print("alpha^(p^2+p+1) = norm = detM (scalar):", K.pw(al,m)==(D,0,0))
for q in [3,73,5839,12221196943,5187662682403]:
    g=K.pw(al,m//q); print(f"  alpha^(m/{q}) is scalar (so projective order not divisible by {q})?", g[1]==0 and g[2]==0)
for name,c in [("C''",Cpp)]:
    g=K.pw(al,m//c); print(f"  alpha^(m/{name}) is scalar?",g[1]==0 and g[2]==0)
# det M multiplicative order structure in F_p^*
print("--- det M in F_p^* ---")
print("legendre(det)=",legendre(D)," => 2-part of ord(det) is 2^32")
g=pow(D,(p-1)//2**32,p)
for q in [3,463,C]:
    print(f"  det^((p-1)/{q if q<10**6 else 'C'}) == 1 ?", pow(D,(p-1)//q,p)==1)
print("--- same for each Cauchy-structured scalar of M: T,S ---")
