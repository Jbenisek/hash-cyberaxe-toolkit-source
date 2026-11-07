# kdesc2.py MOD START : coordinate descent, values v << 4s (v 1..15, s 0..7) and 0 per word, from START; prints improvements
import sys, importlib.util, time
sys.dont_write_bytecode = True; sys.setrecursionlimit(100000)
spec = importlib.util.spec_from_file_location("b", sys.argv[1]); b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
key = [int(h, 16) for h in sys.argv[2].split(",")]
ev = lambda k: len(b.used_gates(*b.trace(256, k)))
vals = [0] + [v << (4 * s) for s in range(7, -1, -1) for v in range(1, 16)]
best = ev(key); n = 1; t0 = time.time(); imp = True
print("start", best, flush=True)
while imp and time.time() - t0 < 1080:
    imp = False
    for i in range(8):
        for val in vals:
            if val == key[i] or time.time() - t0 > 1080: continue
            k2 = key[:i] + [val] + key[i + 1:]; g = ev(k2); n += 1
            if g < best:
                best, key, imp = g, k2, True
                print("improve", best, ",".join("%08x" % x for x in key), n, round(time.time() - t0), flush=True)
        print("word", i, "done", n, round(time.time() - t0), flush=True)
print("done", best, ",".join("%08x" % x for x in key), n, round(time.time() - t0), flush=True)
