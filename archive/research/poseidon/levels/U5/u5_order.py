from u5_lib import *
import flint
T,S,D = charpoly(MDS); K=F3(T,S,D); al=(0,1,0); p=P; n=p**3-1
f1=539204044132271846773; f2=8999194758858563409123804352480028797519453
g1=487887715480415483992657; g2=21186043132281546156793608169660962271252226488966104018788253841360240111557635227669180162173314659
C=(p-1)//(2**32*3*463); Cpp=(p*p+p+1)//(3*73*5839*12221196943*5187662682403)
print("f1*f2==C:",f1*f2==C,"; g1*g2==C'':",g1*g2==Cpp)
for nm,x in [("f1",f1),("f2",f2),("g1",g1),("g2",g2)]:
    print(nm,"bits",x.bit_length(),"probable prime:",flint.fmpz(x).is_probable_prime(), " p mod x (for group-order check):")
# prime factors of p^3-1 so far
primes={2:32,3:2,463:1,73:1,5839:1,12221196943:1,5187662682403:1,f1:1,g1:1}
rest={f2:1,g2:1}
print("exponent/orders:")
one=K.one()
for q in list(primes)+[f2,g2]:
    g=K.pw(al,n//q); 
    print(f"  alpha^(n/q)!=1 for q={q if q<10**30 else str(q)[:12]+'..('+str(q.bit_length())+'b)'} :", g!=one)
# n/(2^32 ...) all prime powers: since all listed are prime (check), alpha generates F_{p^3}^* iff all above True
