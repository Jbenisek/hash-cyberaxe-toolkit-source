'A6: the non-empty rule-A (stage A) tables that repeat: group sizes, pass counts, and how the frame keys differ.'
import struct, sys
from collections import defaultdict, Counter

frames, out = sys.argv[1], sys.argv[2]
fr, rec = open(frames, "rb").read(), open(out, "rb").read()
n = len(rec) // 44
groups = defaultdict(list)
npc = Counter()
for i in range(n):
    r = struct.unpack_from("<4Q3I", rec, 44 * i)
    npc[r[5]] += 1
    if r[5]:
        groups[r[2:4]].append((i, r[5]))
rep = [g for g in groups.values() if len(g) > 1]
print("frames", n, "non-empty rule-A tables", sum(len(g) for g in groups.values()), "distinct", len(groups))
print("repeated groups", len(rep), "duplicates", sum(len(g) - 1 for g in rep), "sizes", Counter(len(g) for g in rep))
print("pass counts of repeated groups", Counter(g[0][1] for g in rep).most_common(12))
print("pass-count distribution, all frames (top 12)", npc.most_common(12))
names = ("Y12", "Q", "w5", "C2.b1", "C2.c1", "e1")
for g in rep[:8]:
    ks = [struct.unpack_from("<6I", fr, 24 * i) for i, _ in g]
    print("np", g[0][1], " ".join("%s^=%08x" % (nm, ks[0][t] ^ ks[1][t]) for t, nm in enumerate(names)))
