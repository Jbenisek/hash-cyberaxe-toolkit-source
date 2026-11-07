from fractions import Fraction
import math
DEN, RATE = 271000000000, 1355
old = Fraction(2133611670920905708573, DEN)
a = (374867584175-62313484289)
b = 39*24*((1<<20)*96+(1<<15)*512+(1<<22))-(107089798*96+3144113*512+751*(1<<22))
c = 39*(1<<31)
d = 16241153777-2573293728
e = 91*((1<<20)*96+(1<<15)*512+(1<<22)-(142596*96+4409*512+(1<<22)))
f = 1639088128*21-(1181844*64+3412138*32+6731804*64+1741*(1<<17))
g = 2176*((1<<18)-142596)*96
small = Fraction(532*41449*3, 5)
saving = Fraction(a+b+c+d+e+f+g, RATE) + small
N = old - saving
assert N == Fraction(2014712256488305708573, DEN)
ops = N*RATE
print("N_int", (ops.numerator+ops.denominator-1)//ops.denominator)
print("time_log2 = %.5f" % math.log2(N))
print("S(27.2) = %.5f" % (math.log2(N)+7.2))
# T1/T2 export charge
N1=8674833
t12 = N1*4096 + 1639088128*56 + 2**32
print("U.4 T1/T2/export prim", t12, "units", t12/RATE, "log2 %.4f" % math.log2(t12/RATE))
t2new = 1181844*64+3412138*32+6731804*64+1741*(1<<17)
print("T2 executed prim (J)", t2new, " old T2 prim", 1639088128*21)
print("U.4 with J T2 repricing: prim", N1*4096 + t2new + 2**32, "units %.1f" % ((N1*4096 + t2new + 2**32)/RATE))
