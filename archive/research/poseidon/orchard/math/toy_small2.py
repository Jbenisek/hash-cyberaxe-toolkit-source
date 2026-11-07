import sys, json, random, time
import toy
from toy import *
class SmallToy(toy.Toy):
    q = 4
    def rounds(self):
        full = [(k, True) for k in range(4)] + [(4 + i, False) for i in range(self.r)] + [(k, True) for k in range(60, 64)]
        return full[:2] + full[2:][-self.q:]
toy.Toy = SmallToy
p = int(sys.argv[1]); q = int(sys.argv[2]); ncent = int(sys.argv[3]); outf = sys.argv[4]
SmallToy.q = q
toy.ALT_EVERY = int(sys.argv[5])
rng = random.Random(9000 + q)
allst = []
for cs in range(2):
    for j in range(3):
        t = time.time()
        st = toy.run(p, 5000 + cs, 1, j, ncent, rng)   # r=1 so that q up to 5+... covers partial round
        for k in ('n_sq', 'n_nsq', 'alt_n', 'n_all'): st[k] = dict(st[k])
        allst.append(st)
        print(f"q={q} D={st['D']} cs={cs} j={j} succ={st['succ']}/{ncent} alt={st['alt_succ']}/{st.get('alt_tried',0)} verified={st['verified']} fail={st['verify_fail']} t={time.time()-t:.0f}s", flush=True)
        json.dump(allst, open(outf, 'w'))
