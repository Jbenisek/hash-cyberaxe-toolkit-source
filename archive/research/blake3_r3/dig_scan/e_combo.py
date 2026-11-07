from common import *
import json
from fractions import Fraction
from math import exp
B=base()
r1=led(group=True,extra=29,d=113.70004324885304,tmax=21004)
print("safe combo (group filter, extra29, frac d 32B)", r1["time"]-B["time"], r1["mem"])
cut11=Fraction(float(Fraction(15,100000)*Fraction(11*exp(-11)/(12*exp(-12)))) ).limit_denominator(10**9)
r2=led(group=True,extra=29,d=113.70004324885304,tmax=21004,kappa=11,cutloss=cut11,lam=Fraction(4945,10000),inflight=8)
print("aggressive combo", r2["time"]-B["time"], r2["mem"], r2["time"])
# 25B entries + U19 + group
tm=(2**20-39*600*19-2048)//25
r3=led(group=True,U=19,extra=29,d=113.4,tmax=tm)
print(tm, r3["time"]-B["time"])
json.dump(dict(safe=r1["time"]-B["time"],aggr=r2["time"]-B["time"]),open("e_combo.json","w"))
