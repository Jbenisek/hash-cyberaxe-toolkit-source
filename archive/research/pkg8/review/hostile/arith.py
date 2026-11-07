from math import log2, exp, ceil
from fractions import Fraction as F

W=18725
P = W*47 + F(W*135,32) + 134 + 1 + F(W*74+260+8, 2**32) + F(16,2**64)
print("P per X2 =", float(P))
print("P/131072 =", float(P/131072))
print("rows: stageA", 18725*47, 18725*47/131072)
print("stage2", 18725*135/32, 18725*135/32/131072)
print("mid", 134/131072, "loopctl", 1.000000002/131072)
tot = 18725*47/131072 + 18725*135/32/131072 + 134/131072 + 0.000322622/131072 + 6.054e-08/131072 + 1.000000002/131072
print("sum of per-trial column =", tot)
print("printed budgeted per trial 1.6389 ; ratio", tot/1.6389)
print("charged per X2 1.71*131072 =", 1.71*131072)

N = 1424469 * 2**81
print("\nN =", N, "log2N =", log2(1424469)+81)
print("1.71*N/430 log2 =", log2(1.71)+log2(1424469)+81-log2(430))
print("2^46/49.4e6 =", 2**46/49_400_000)
print("N*2**-128*185355453 =", 185355453*1424469*2.0**81/2**128)
print("N*2^-102.442 =", 1424469*2.0**81*49_400_000/2**128)

# cluster loss
yield_=40.02; TE=41.02
print("\nTE/64 =", TE/64, " 64/TE =", 64/TE, "log2:", log2(64/TE))
exp_good = 0.5*TE/64
print("expected good =", exp_good, "success =", 1-exp(-exp_good))
print("success minus allowances", 1-exp(-exp_good)-0.003)
print("needed C0.d1 range:", ceil(1424468.5*64/TE))
print("new N log2:", log2(ceil(1424468.5*64/TE))+81)
print("new time log2:", log2(1.71)+log2(ceil(1424468.5*64/TE))+81-log2(430))

# per-representative measured cost
stageA_words = 1/7 + 0.5625
st2_words = 0.02622/7 + 0.5625*0.1367
cost = stageA_words*47 + st2_words*135
print("\nmeasured cost/rep (bare) =", cost, "per TE =", cost/TE, "per nominal trial =", cost/64)
print("grok 56.0007/41.02 =", 56.0007/41.02)
print("1.2*1.3652 =", 1.2*1.3652)

# yield if gate were exactly carried
print("\nlossless yield would be 63 ->", 63/63)
print("retention 40.02/63 =", 40.02/63)
# stage-2 share of batches under clusters vs budget 1/32
reps_words=2341; nb_words=16384*0.5625
share = (2341*0.02622 + nb_words*0.1367)/(2341+nb_words)
print("\nstage2 share of words under clusters =", share, " budget 1/32 =", 1/32)
print("reps per X2 value: 131072/8/7 =", 131072/8/7)
print("16384/7 =", 16384/7)
# sensitivity f
print("\nf needed:", 49323560, " check:", 1-exp(-49323560*1424469/2**47)-0.003)
print("2^119.038 check:", log2(1.71)+127-log2(430))
