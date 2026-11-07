"""check_probe.py - cross-check walk32's generated CUDA lines and group sampler against walk_model.py (Python, the
shipped frontline LINES) and the shipped tables T1/T2: reads PROBE lines on stdin."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import walk_model as W  # noqa: E402

F = W.F
M64 = (1 << 64) - 1


def splitmix(s):
    s = (s + 0x9E3779B97F4A7C15) & M64
    z = s
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & M64
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & M64
    return s, z ^ (z >> 31)


def group_words(seed, gi):
    s = seed ^ ((gi * 0xD1B54A32D192ED03) & M64)
    ow = []
    for _ in range(7):
        s, z = splitmix(s)
        ow.append(z & 0xFFFFFFFF)
    s, z = splitmix(s)
    k = z & 0x7FFFF
    e1, y = F.member(k)
    return ow, y, k


ok = bad = 0
for line in sys.stdin:
    if not line.startswith("PROBE"):
        continue
    f = line.split()
    d = {f[i]: f[i + 1] for i in range(1, len(f) - 1) if not f[i][0].isdigit()}
    seed, gi = int(d["seed"]), int(d["gi"])
    ow, y, k = group_words(seed, gi)
    thi = int(d["thi"])
    v = W.co_walk(ow, y, thi)
    gpu = {n: int(d[n], 16) for n in ("X0", "omega", "Y9", "Y1", "Y12", "w12", "w5")}
    same = (k == int(d["k"]) and y == int(d["y"], 16) and all(gpu[n] == v[n] for n in gpu)
            and int(d["m2"]) == F.T2(v["omega"]) and int(d["m1"]) == F.T1(v["Y9"]) and thi < (1 << 19))
    ok += same
    bad += not same
print("probe cross-check: %d equal, %d different" % (ok, bad))
