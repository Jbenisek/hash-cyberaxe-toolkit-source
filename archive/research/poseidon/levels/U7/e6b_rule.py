# E6b: check the support rule  sum_j ceil(a_j/5) <= 5^(k-1)*... for F,F with constants (3 free vars)
import itertools
def cnt(limit, step=5, nv=3, maxd=200):
    c=0
    for a in itertools.product(range(maxd),repeat=nv):
        if sum(-(-x//step) for x in a)<=limit: c+=1
    return c
print("F,F const: #(a0,a1,a2) with sum ceil(a_j/5) <= 5 :", cnt(5,maxd=26), "(observed 2076)")
# P,P const (R4,R5): lane0 only nonlinear each round
