"""U9 Q5 toy distribution: number of F_q roots of the lane-0 top form after R1, R2, R3 (random Cauchy MDS, many seeds). By the perfect-power law the output top form has exactly the root set of the R3 form."""
import sys, collections
from u9lib import Ring
from u9toy import *
for q in (1000003, 786433):
    ring = Ring(q); z = ring.x()
    cnt = {1: collections.Counter(), 2: collections.Counter(), 3: collections.Counter()}
    for seed in range(1, 301):
        Mx, RCx, cap = toy_params(q, seed)
        f = [z*Mx[i][0] + Mx[i][1] for i in range(3)]
        for idx in (1, 2, 3):
            g = [ring.pow5(x) for x in f]; f = [ring.lin(Mx[i], g) for i in range(3)]
            cnt[idx][len(f[0].roots())] += 1
    for idx in (1, 2, 3):
        tot = sum(cnt[idx].values()); mean = sum(k*v for k, v in cnt[idx].items())/tot
        print('q=%d 300 seeds, lane-0 top form after R%d: root-count histogram %s mean %.2f (a random polynomial has mean 1, P(0)=0.37, P(1)=0.37, P(2)=0.18)' % (q, idx, dict(sorted(cnt[idx].items())), mean))
