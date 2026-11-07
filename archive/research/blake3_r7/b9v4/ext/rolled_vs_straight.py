"""External check (not shipped): the rolled program (b8 bsrho.py Step) vs the straight-line b7 program (Step of bsrho_b7.py) on random inputs, lane by lane,
and the listing interpreter vs the compiled step.   usage: rolled_vs_straight.py <b8 experiments dir> <b7 experiments dir> <batches>"""
import sys, random, importlib.util
sys.dont_write_bytecode = True
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path + "/bsrho.py"); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
b8, b7 = load("b8", sys.argv[1]), load("b7", sys.argv[2])
nb = int(sys.argv[3])
s8, s7 = b8.step256(), b7.step256()
rnd = random.Random(777)
bad = tot = 0
for i in range(nb):
    xs = [rnd.getrandbits(256) for _ in range(256)]
    if i % 4 == 1: xs = [x & ((1 << 40) - 1) for x in xs]          # small inputs (many zero planes)
    if i % 4 == 2: xs = [(rnd.getrandbits(1) * ((1 << 256) - 1)) ^ (1 << rnd.randrange(256)) for _ in xs]   # sparse / dense
    o8 = b8.lanes_of(list(s8.step(*b8.pack_lanes(xs, 256, s8.pin))), 256, s8.pin)
    o7 = b7.lanes_of(list(s7.step(*b7.pack_lanes(xs, 256, s7.pin))), 256, s7.pin)
    for l in range(256):
        tot += 1
        bad += (o8[l] ^ s8.qint) != (o7[l] ^ s7.qint)
print("rolled vs straight-line: %d lanes, %d differences (b7 q = %064x, b8 q = %064x)" % (tot, bad, s7.qint, s8.qint))
pl = [rnd.getrandbits(256) for _ in range(256)]
print("interpreter (loop control) vs compiled rolled step, random planes:", b8.run_listing(s8.flat, pl, 256, s8.regs) == list(s8.step(*pl)))
