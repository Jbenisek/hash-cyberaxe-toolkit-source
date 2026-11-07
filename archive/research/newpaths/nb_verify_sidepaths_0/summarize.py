"""Tabulate out/*.txt: counts per configuration, ratio to the pooled mean of all real configurations, and the
z-score of each configuration against the pooled others (Poisson)."""
import glob, math, os, re
d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
rows = {}
for fn in sorted(glob.glob(os.path.join(d, "*.txt"))):
    name = os.path.basename(fn)[:-4]
    t = open(fn).read()
    if "N " not in t:
        continue
    r = {}
    r["N"] = int(re.search(r"^N (\d+)", t, re.M).group(1))
    a = list(map(int, re.search(r"low16zero r1 r3 r4 r6: (.*)", t).group(1).split()))
    b = list(map(int, re.search(r"wordzero  r1 r3 r4 r6: (.*)", t).group(1).split()))
    p = list(map(int, re.search(r"pairs low8 zero \(13 14 16 34 36 46\): (.*)", t).group(1).split()))
    m = re.search(r"all four low8 zero: (\d+)   all four low4 zero: (\d+)", t)
    w = re.search(r"weight mean ([\d.]+) var ([\d.]+)  weight<=40: (\d+)", t)
    for i, k in enumerate(("r1", "r3", "r4", "r6")):
        r["lo16_" + k] = a[i]; r["z32_" + k] = b[i]
    for i, k in enumerate(("13", "14", "16", "34", "36", "46")):
        r["lo8pair_" + k] = p[i]
    r["all_lo8"] = int(m.group(1)); r["all_lo4"] = int(m.group(2))
    r["hw<=40"] = int(w.group(3)); r["hw_mean"] = float(w.group(1)); r["hw_var"] = float(w.group(2))
    rows[name] = r
names = list(rows)
keys = [k for k in rows[names[0]] if k not in ("N", "hw_mean", "hw_var")]
print("config: " + "  ".join(names))
print("N: " + "  ".join(str(rows[n]["N"]) for n in names))
print()
print(f"{'event':14s} " + " ".join(f"{n:>10s}" for n in names) + "   max|z| real-vs-others  z(M vs real pooled)")
real = [n for n in names if n != "m_0"]
for k in keys:
    vals = [rows[n][k] for n in names]
    zs = []
    for n in real:
        x = rows[n][k]; others = [rows[o][k] for o in real if o != n]
        mu = sum(others) / len(others)
        sd = math.sqrt(x + mu / len(others)) if x + mu > 0 else 1
        zs.append((x - mu) / sd if sd else 0)
    pooled = sum(rows[n][k] for n in real) / len(real)
    zm = ""
    if "m_0" in rows:
        x = rows["m_0"][k]; sd = math.sqrt(x + pooled / len(real)) or 1
        zm = f"{(x - pooled) / sd:+.2f}"
    print(f"{k:14s} " + " ".join(f"{v:10d}" for v in vals) + f"   {max(abs(z) for z in zs):5.2f}" + f"   {zm}")
print()
for n in names:
    print(f"{n}: weight mean {rows[n]['hw_mean']:.5f} var {rows[n]['hw_var']:.4f}")
