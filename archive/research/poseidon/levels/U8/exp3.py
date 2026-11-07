# U8: p-1, p+1 verification; ord of 5 on the cycle structure; factor p^2+1; (M order done in exp4)
import sys, time, threading
from math import gcd
from sympy import factorint, isprime
P = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
def pr(*a): print(' '.join(str(x) for x in a), flush=True)
f_pm1 = {2: 32, 3: 1, 463: 1, 539204044132271846773: 1, 8999194758858563409123804352480028797519453: 1}
f_pp1 = {2: 1, 43: 1, 257: 1, 25457: 1, 798828148463: 1, 64406061401325646461747376276669182911234205142335110909: 1}
def prod(f):
    r = 1
    for p, e in f.items(): r *= p**e
    return r
pr("p-1 product check:", prod(f_pm1) == P-1, "; all primes:", all(isprime(q) for q in f_pm1))
pr("p+1 product check:", prod(f_pp1) == P+1, "; all primes:", all(isprime(q) for q in f_pp1))
pr("bit sizes p-1 primes:", [q.bit_length() for q in f_pm1], " p+1 primes:", [q.bit_length() for q in f_pp1])
q69 = 539204044132271846773; q143 = 8999194758858563409123804352480028797519453
f143 = {2: 2, 3: 4, 11: 1, 2531: 1, 115603: 1, 1197907: 1, 22160661629: 1, 325086459374267: 1}
pr("q143-1 product check:", prod(f143) == q143-1, "all prime:", all(isprime(q) for q in f143))
def ordmod(a, m, fac):
    o = prod(fac)
    for pp, e in fac.items():
        for _ in range(e):
            if pow(a, o//pp, m) == 1: o //= pp
            else: break
    return o
o143 = ordmod(5, q143, f143)
o69 = q69-1
pr("ord 5 mod q143 =", o143, " index (q143-1)/ord =", (q143-1)//o143)
L = 1
for v in [1 << 30, 2, 462, o69, o143]:
    L = L*v//gcd(L, v)
pr("largest cycle of x->x^5 on F_p^* (lcm of ord_5 over the prime-power parts):", L, " = %.3e, bits %d" % (L, L.bit_length()))
pr("   factors: 2^30 from the 2-part, 462 from 463, q69-1 =", o69, "from the 69-bit prime, ord", o143, "from the 143-bit prime")
pr("   lcm(...)/2^30 odd part bits:", (L >> 30).bit_length())
# cycle lengths seen by order of the starting point's subgroup: list for small orders
def ord5(n, fac):
    return ordmod(5, n, fac) if n > 2 else 1
pr("cycle lengths of x->x^5 on small subgroups: order 3 ->", 2, "(5=2 mod 3: swaps the two primitive cube roots); order 463 ->", 462, "; order 2^k ->", "1 (k<=2) or 2^(k-2)")
# p^2+1
pr("\np^2+1 =", P*P+1)
t0 = time.time(); res = {}
def work():
    try: res['f'] = factorint(P*P+1, limit=2*10**6, use_ecm=True)
    except Exception as e: res['f'] = repr(e)
th = threading.Thread(target=work, daemon=True); th.start(); th.join(600)
pr("factor attempt p^2+1 (600 s cap, %.0fs):" % (time.time()-t0), res.get('f', 'not finished'))
