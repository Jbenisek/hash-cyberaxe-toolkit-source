# kdesc.py MOD NB START(hex8,comma) : coordinate descent (same rule as choose_key) with nb-bit top values from a start key; prints each improvement
import sys, importlib.util, time
sys.dont_write_bytecode = True; sys.setrecursionlimit(100000)
spec = importlib.util.spec_from_file_location("b", sys.argv[1]); b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
nb = int(sys.argv[2]); key = [int(h, 16) for h in sys.argv[3].split(",")]
ev = lambda k: len(b.used_gates(*b.trace(256, k)))
best = ev(key); n = 1; t0 = time.time(); imp = True
print("start", best, flush=True)
while imp:
    imp = False
    for i in range(8):
        for v in range(1 << nb):
            val = v << (32 - nb)
            if val == key[i]: continue
            k2 = key[:i] + [val] + key[i + 1:]; g = ev(k2); n += 1
            if g < best:
                best, key, imp = g, k2, True
                print("improve", best, ",".join("%08x" % x for x in key), n, round(time.time() - t0), flush=True)
print("done", best, ",".join("%08x" % x for x in key), n, round(time.time() - t0), flush=True)
