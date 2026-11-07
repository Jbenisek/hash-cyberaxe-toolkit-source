"""Write the job list for one run (A: seedbase block 1, B: block 2). One line per job: fam fixed r w T h S mcap gmax K seedbase outfile.
Algorithm parameters per width from plan_w.py (w >= 24); w = 16, 20 only measure the first-collision law and DP gaps."""
import sys, json, subprocess
run = sys.argv[1]; blk = {"A": 1, "B": 2}[run]
P = {}
for w in (24, 28, 32, 36, 40):
    P[w] = json.loads(subprocess.check_output([sys.executable, "-B", "plan_w.py", str(w)]))
def par(w):
    if w in P:
        p = P[w]; return [p["T"], p["h"], p["S"], p["mcap"], p["gmax"]]
    h = w // 2; return [1 << (h - 4), h, 1 << (h + 2), 100000, 1 << 12]
jobs = []
def add(fam, fixed, w, K, chunks, tag):
    per = K // chunks
    for c in range(chunks):
        sb = blk * 100000 + w * 1000 + (500 if fixed else 0) + c + (300 if fam == "c" else 0)
        jobs.append([fam, fixed, 23, w] + par(w) + [per, sb, f"{tag}_w{w}_c{c}.jsonl"])
ladder = {16: (2000, 1), 20: (2000, 2), 24: (2000, 4), 28: (600, 4), 32: (200, 8), 36: (60, 6), 40: (12, 6)}
for w, (K, ch) in ladder.items():
    add("o", 0, w, K, ch, "orch")
for w, (K, ch) in {24: (200, 2), 28: (200, 4), 32: (100, 5)}.items():
    add("o", 1, w, K, ch, "orch0")          # the rho = 0 map itself (function index 0), many starts
for w, (K, ch) in ladder.items():
    add("c", 0, w, 5 * K, 1, "ctrl")
for f in range(1, 41):                       # control: 40 fixed functions x 200 starts at w = 24, 28 (spread of per-function success)
    for w in (24, 28):
        sb = blk * 100000 + 90000 + f * 10 + (w - 20)
        jobs.append(["c", f + 1000 * blk, 23, w] + par(w) + [200, sb, f"ctrlfix_w{w}_f{f}.jsonl"])
jobs.sort(key=lambda j: -(j[9] * 2 ** (j[3] / 2) * (40 if j[0] == "o" else 1)))   # longest first
for j in jobs:
    print(" ".join(map(str, j)))
