# stats_chk.py - check2-4: summary of my chk38 runs (campX.log, campY.log): per mode the mean of the estimates Z,
# relative sd, one-sided 99% Student bounds (as in the filed rules), stage means, verification failures, and the gain
# factors g = mean(mode) / mean(C) with the conservative ratio (99% lower of the mode / 99% upper of C).
import math, re, statistics, sys
T99 = {3: 4.541, 7: 2.998, 15: 2.602}
pat = re.compile(r"mode (\w) seed (\d+) NP (\d+): log2 q3 = (-?[\d.]+)  stages: ([-\d. ]+?)  \|Gused\| (\d+)  tail successes (\d+) verified (\d+) failed (\d+).*?cellpath (\d+) \(wfrac ([\d.]+)\)  firsttest (\d+) \(wfrac ([\d.]+)\)")
runs = {}
for fn in sys.argv[1:]:
    for line in open(fn):
        m = pat.search(line)
        if m:
            runs.setdefault(m.group(1), []).append(dict(l=float(m.group(4)), st=[float(x) for x in m.group(5).split()],
                succ=int(m.group(7)), ver=int(m.group(8)), fail=int(m.group(9)), cp=int(m.group(10)), wcp=float(m.group(11)),
                ft=int(m.group(12)), wft=float(m.group(13))))
S = {}
print("mode runs  mean log2 q3  rel.sd  99%% lower  99%% upper  successes(verified/failed)  cell-path wfrac  first-test wfrac  stage means")
for md in "CTMH":
    if md not in runs: continue
    rs = runs[md]; z = [2.0 ** r["l"] for r in rs]; n = len(z); mz = sum(z) / n; sd = statistics.stdev(z)
    t = T99[n - 1]; lo, hi = mz - t * sd / math.sqrt(n), mz + t * sd / math.sqrt(n)
    st = [sum(r["st"][k] for r in rs) / n for k in range(len(rs[0]["st"]))]
    S[md] = dict(m=mz, lo=lo, hi=hi)
    print("%s    %4d  %10.4f   %6.4f  %9.4f  %9.4f  %d/%d  %.4f  %.4f   %s" % (md, n, math.log2(mz), sd / mz, math.log2(lo), math.log2(hi),
          sum(r["ver"] for r in rs), sum(r["fail"] for r in rs), sum(r["wcp"] for r in rs) / n, sum(r["wft"] for r in rs) / n,
          " ".join("%.3f" % x for x in st)))
c = S["C"]
print("\ngain factors against my cell runs (C) and against the filed R1 mean 2^-101.0001:")
for md in "TMH":
    if md not in S: continue
    s = S[md]
    print("  %s: g = %.3f (log2 %.3f), conservative %.3f; vs filed R1 mean: %.3f" % (md, s["m"] / c["m"], math.log2(s["m"] / c["m"]),
          s["lo"] / c["hi"], s["m"] / 2.0 ** -101.0001))
