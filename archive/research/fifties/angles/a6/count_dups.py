'A6: count duplicate frame keys and duplicate tables (word table, rule-A table, both) from the GPU records.'
import struct, sys
from collections import Counter

def dups(items):
    'Number of items minus the number of distinct items, and the largest group.'
    c = Counter(items)
    return len(items) - len(c), max(c.values())

frames, out = sys.argv[1], sys.argv[2]
with open(frames, "rb") as f:
    fr = f.read()
with open(out, "rb") as f:
    rec = f.read()
n = len(rec) // 44
keys = [fr[24 * i:24 * i + 24] for i in range(n)]
recs = [struct.unpack_from("<4Q3I", rec, 44 * i) for i in range(n)]
word = [r[0:2] for r in recs]
rule = [r[2:4] for r in recs]
both = [r[0:4] for r in recs]
ebw = [k[:12] for k in keys]          # (Y12, Q, w5): all the word table reads
print("file", frames, "frames", n)
print("dup frame keys (6 words)", dups(keys))
print("dup (Y12,Q,w5) sub-keys", dups(ebw))
print("dup word tables", dups(word))
print("dup rule-A tables", dups(rule))
print("dup whole tables", dups(both))
nz = sum(r[4] for r in recs); np_ = sum(r[5] for r in recs); nj = sum(r[6] for r in recs)
print("mean per frame: word==0 %.4f, rule A pass %.1f, both %.6f" % (nz / n, np_ / n, nj / n))
print("frames with empty pass set (word==0 and rule A)", sum(r[6] == 0 for r in recs))
