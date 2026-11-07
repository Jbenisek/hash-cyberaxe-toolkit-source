'''List the nonzero blocks of the validation set that came back with zero damage (what are they?).'''
import sys, random
sys.dont_write_bytecode = True
from common import FRAMES
from harness import Harness
from validate import random_block
H = Harness(); rnd = random.Random(1); frames = ['D'] * 40 + ['O'] * 30 + ['R'] * 30; cases = []
for _ in range(1000):
    fr = rnd.choice(frames); ci = rnd.randrange(len(H.cfgs)); kind, m = random_block(rnd, fr); cases.append((ci, fr, m, kind))
res = H.apply_batch([c[:3] for c in cases])
for (ci, fr, m, kind), r in zip(cases, res):
    if r['zero_damage'] and any(m):
        print(fr, ci, kind, {FRAMES[fr][i]: '%08x' % x for i, x in enumerate(m) if x}, 'info', r['info_names'],
              'steer', {k: '%08x' % v for k, v in r['steer'].items() if v})
