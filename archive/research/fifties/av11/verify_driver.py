"""Part (1): verify the 11.2 inverse (Python ref + C twin) against GPU brute force over all 2^32 h.
Writes frames_verify.txt, verify_out.txt (from ./av11 verify) and verify_summary.json."""
import json, random, subprocess, sys, os
from av11_ref import *

DFLAG = int(sys.argv[1]) if len(sys.argv) > 1 else 11
rnd = random.Random(20261009 + DFLAG)
here = os.path.dirname(os.path.abspath(__file__))
frames, kinds = [], []

def rand_in(cl):
    e1 = (rnd.getrandbits(32) & ~cl[0] & M) | cl[1]
    return (e1 - Y3) & M

for q in QS:
    b = b_of_q(q)
    for _ in range(200):   # A: random frame, y uniform in C13
        frames.append((b, rnd.getrandbits(32), rnd.getrandbits(32), rand_in(CL13))); kinds.append(("A", q))
    for _ in range(200):   # B: planted root, arbitrary y
        h, z, f = (rnd.getrandbits(32) for _ in range(3))
        frames.append((b, z, f, y_forward(b, h, z, f, DFLAG))); kinds.append(("B", q))
    n = 0
    while n < 100:         # P: planted root with y in C13 (a landed frame)
        h, z, f = (rnd.getrandbits(32) for _ in range(3))
        y = y_forward(b, h, z, f, DFLAG)
        if in_class(y, CL13):
            frames.append((b, z, f, y)); kinds.append(("P", q)); n += 1
    f0 = f_for_K0(b, DFLAG); z0 = (-f0) & M
    D0, K0, u0 = chart_consts(b, z0, f0, DFLAG); assert K0 == 0 and u0 == 0
    for _ in range(50):    # Z: K=u=0 physical subfamily, planted root
        h = rnd.getrandbits(32)
        frames.append((b, z0, f0, y_forward(b, h, z0, f0, DFLAG))); kinds.append(("Z", q))
    # the 11.2 example target V = 00800080 on the K=u=0 subfamily
    yex = ror(((0x00800080 + D0) & M) ^ z0, 7)
    frames.append((b, z0, f0, yex)); kinds.append(("X", q))

fin = os.path.join(here, f"frames_verify_d{DFLAG}.txt"); fout = os.path.join(here, f"verify_out_d{DFLAG}.txt")
with open(fin, "w") as fh:
    for fr in frames: fh.write("%08x %08x %08x %08x\n" % fr)
r = subprocess.run([os.path.join(here, "av11"), "verify", fin, fout, str(DFLAG)], capture_output=True, text=True)
print(r.stdout.strip(), r.stderr.strip())

stats = {}
py_bad = c_bad = 0; Rs = {}
for line, fr, kd in zip(open(fout), frames, kinds):
    left, right = line.split("|")
    lt = left.split(); idx, nb, ni, ok = map(int, lt[:4]); brute = sorted(int(x, 16) for x in lt[4:])
    cpairs = sorted((int(p.split(":")[0]), int(p.split(":")[1], 16)) for p in right.split())
    b, z, f, y = fr
    D, K, u = chart_consts(b, z, f, DFLAG); V = V_of(y, z, D)
    pyr = sorted(inverse(K, u, V))
    pyh = sorted(h for _, h in pyr)
    if pyh != brute or len(set(pyh)) != len(pyh) or len(pyh) > 64: py_bad += 1
    if not ok or pyr != cpairs: c_bad += 1
    if not all(av_frame(h, K, u, V) for h in brute): py_bad += 1
    s = stats.setdefault(f"{kd[0]}_q{kd[1]:08x}", {"frames": 0, "roots_total": 0, "maxR": 0, "R0": 0})
    s["frames"] += 1; s["roots_total"] += len(brute); s["maxR"] = max(s["maxR"], len(brute)); s["R0"] += len(brute) == 0
summary = {"dflag": DFLAG, "frames": len(frames), "python_ref_mismatches": py_bad,
           "c_twin_mismatches_incl_seed_labels": c_bad, "by_kind": stats,
           "kinds": {"A": "random (z,f), y uniform in C13", "B": "planted h, arbitrary y",
                     "P": "planted h with y in C13", "Z": "K=u=0 subfamily planted", "X": "K=u=0, V=00800080 (11.2 example)"}}
json.dump(summary, open(os.path.join(here, f"verify_summary_d{DFLAG}.json"), "w"), indent=1)
print(json.dumps(summary))
