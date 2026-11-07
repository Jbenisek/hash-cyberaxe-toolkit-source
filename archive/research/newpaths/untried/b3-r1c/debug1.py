import random
from model import *

rng = random.Random(1)
p = rand_params(rng)
wA, t, wB = build(p)
TA, TB = trace(wA, t, 55), trace(wB, t, 63)
print("S equal:", [i for i in range(16) if TA["S%d" % i] != TB["S%d" % i]])
print("X equal:", [i for i in range(16) if TA["X%d" % i] != TB["X%d" % i]])
print("pins:", {i: (hex(TA["X%d" % i]), hex(PIN[i])) for i in PIN})
print("Y4 vs y:", hex(TA["Y4"]), hex(p["y"]))
print("S11:", hex(TA["S11"]), hex(p["S11"]), "S4:", hex(TA["S4"]), hex(p["S4"]), "X9:", hex(TA["X9"]), hex(p["X9"]))
print("D2.a1:", hex(TA["D2.a1"]), hex(p["D2a1"]), "D2.b1:", hex(TA["D2.b1"]), hex(p["D2b1"]), "C0.d1", hex(TA["C0.d1"]), hex(p["C0d1"]))
print("t", hex(t), "K2 inputs check w4", hex(wA[4]), hex(wB[4]))
