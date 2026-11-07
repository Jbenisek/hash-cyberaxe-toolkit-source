"""INIT dig: (1) parse the exhaustive site scans (scan_all.txt), (2) plug the solutions into the Tracer and count the real ops,
(3) combine solutions from different columns (k zero sites), (4) price: gain from the filed ledger shares and the pre-search cost.  Own code."""
import re, json, math, os, random
from b3r3lib import *
from site_check import sites_formula

txt = open(os.path.join(HERE, "scan_all.txt")).read()
blocks = re.split(r"(?=^word v)", txt, flags=re.M)
scan = {}
for b in blocks:
    m = re.match(r"word v(\d+)\s+column (\d) role (\d)", b)
    if not m:
        continue
    i = int(m.group(1))
    hist = {int(a): int(c) for a, c in re.findall(r"\[(\d+)\]=(\d+)", b.split("\n")[1])}
    sites = {}
    for sm in re.finditer(r"site\s+(\d+) \(D(\d) stmt .*?\) values making it 0: (\d+)\s+first:((?: 0x[0-9a-f]{8})+)", b):
        sites[int(sm.group(1))] = dict(count=int(sm.group(3)), first=[int(t, 16) for t in sm.group(4).split()])
    best = re.search(r"best: (\-?\d+) zero sites at v(\d+)=0x([0-9a-f]+)", b)
    scan[i] = dict(hist=hist, sites=sites, best_n=int(best.group(1)), best_v=int(best.group(3), 16), col=int(m.group(2)), role=int(m.group(3)))
assert len(scan) == 12, sorted(scan)

# real op counts with the solution plugged in
SITENAME = ["sum p0+p5 (x-add D0)", "xor p15 (D0)", "add p10 (D0)", "xor p5 (D0)",
            "sum p1+p6 (x-add D1)", "xor p12 (D1)", "add p11 (D1)", "xor p6 (D1)",
            "sum p2+p7 (x-add D2)", "xor p13 (D2)", "add p8 (D2)", "xor p7 (D2)",
            "sum p3+p4 (x-add D3)", "xor p14 (D3)", "add p9 (D3)", "xor p4 (D3)"]
demo = {}
for i, d in sorted(scan.items()):
    rows = []
    for s, info in sorted(d["sites"].items()):
        for val in info["first"]:
            st = init_state()
            st[i] = val
            f = sites_formula(st)
            tr, _ = trace(state=st)
            rows.append(dict(site=s, name=SITENAME[s], value=val, zero_sites=[k for k in range(16) if f[k] == 0], ops=tr.ops))
    demo[i] = rows
    for r in rows:
        pass
# all values with >=1 zero site per word are covered by `first` up to 4 per site; check the count of solutions vs histogram
for i, d in scan.items():
    tot = sum(v for n, v in d["hist"].items() if n >= 1)
    assert tot >= max([x["count"] for x in d["sites"].values()] + [0])

# k zero sites from different columns: exhaustive over the candidate solutions found by the scan (v0..v7 only, up to 4 values per site)
import itertools
save1 = {}
for i, rows in demo.items():
    for r in rows:
        if len(r["zero_sites"]) == 1:
            save1[r["zero_sites"][0]] = 595 - r["ops"]
cands = []
for i, d in scan.items():
    if i >= 8:
        continue   # v8..v11 are IV constants, not selectable
    for s, info in d["sites"].items():
        for val in info["first"]:
            cands.append((i, s, val))
combos = {}
for k in (1, 2, 3, 4):
    best = None
    for pick in itertools.combinations(cands, k):
        if len({p[0] for p in pick}) < k:
            continue          # one word carries only one value
        st = init_state()
        for (i, s, val) in pick:
            st[i] = val
        f = sites_formula(st)
        zs = [x for x in range(16) if f[x] == 0]
        est = 595 - sum(save1[z] for z in zs)
        if best is None or est < best[0]:
            best = (est, pick, zs)
    if best is None:
        combos[k] = None
        continue
    st = init_state()
    for (i, s, val) in best[1]:
        st[i] = val
    tr, _ = trace(state=st)
    combos[k] = dict(ops=tr.ops, additive_estimate=best[0], pick=[(i, s, hex(v)) for i, s, v in best[1]], zero_sites=best[2])
    if k > 1 and combos[k - 1] and combos[k - 1]["ops"] <= combos[k]["ops"]:
        combos[k] = dict(combos[k - 1], note="best of at most k sites (no better k-site set in the found pool)")

# price: filed ledger shares
LOOP_SHARE = 0.9944            # submission-note.md: main loop is 99.44 percent of the total
L = 595 + 4 + 3 / 16           # ops per batch in the main loop: circuit + filter 4 + loop control 3 per 16 batches
gain = {}
TOTAL_LOG2 = 125.1087
for k in range(0, 6):
    saved = (595 - combos[k]["ops"]) if k in combos and combos[k] else k
    dl = math.log2(1 - LOOP_SHARE * saved / L)
    pre = math.log2(1 + 2 ** (32 * k) / 2 ** TOTAL_LOG2)       # one-time search of 2^(32k) first-block compressions at one unit each (upper bound, charged at 1 target compression each)
    gain[k] = dict(ops_saved=saved, delta_time_log2=round(dl, 5), pre_search_log2=32 * k, pre_search_relative_bits=round(pre, 12), net=round(dl + pre, 5))
out = dict(scan={str(i): d for i, d in scan.items()}, demo={str(i): r for i, r in demo.items()}, combos=combos, gain=gain, loop_share=LOOP_SHARE, L=L)
json.dump(out, open(os.path.join(HERE, "lever_demo.json"), "w"), indent=1)
print(json.dumps(dict(combos=combos, gain=gain), indent=1))
for i, d in sorted(scan.items()):
    print("v%d" % i, "hist", d["hist"], "sites", {s: v["count"] for s, v in d["sites"].items()}, "best", d["best_n"], hex(d["best_v"]))
