from math import log2
from fractions import Fraction
N=2674847206571284730500; S_old=5486510246044225536
T=Fraction(N+S_old,430)+2**38
print("time_log2",float(log2(T)), "search part", log2(Fraction(N,430)+2**38))
tl=62.43471; mem=43.00001
print("S now",tl+mem-20)
search=6013036259648; code=2**37; out=8796093155510
print("out phase",log2(out),"search",log2(search))
sS=tl+log2(search)-20; print("S stream(search peak)",sS, "gain",tl+mem-20-sS, "with 42.45124:",tl+42.45124-20)
nocode=search-code
print("search w/o code",log2(nocode),"dmem",log2(search)-log2(nocode))
# regen code lower bound: each executed instr costs >=1 unit
Tn=Fraction(2*N+S_old,430)+2**38; print("T regen LB",float(log2(Tn)),"dT",float(log2(Tn)-log2(T)))
# SEL co-resident
for sel in (2**34+2**20,2**35):
    print("search+SEL",log2(search+sel)-log2(search))
print("SEL double dT",float(log2(T+Fraction(S_old,430))-log2(T)))
# SEL 2^34 vs 2^33 saving in sum scenario
print(log2(search+2**34+2**20)-log2(search+2**33+2**19))
# output t-dependence: out bytes at t: 2*(1024t+55 or 63)
print("out at 2^32-1:",(1024*(2**32-1)+55)+(1024*(2**32-1)+63))
print("cursor +2/batch:",log2(1+4682/213439)  )
