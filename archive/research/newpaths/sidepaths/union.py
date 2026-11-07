"""Which words occur in some 0-check basis together with Y4 and w5?  (all_y4_w5_k6.txt from gdx)"""
import sys
from collections import Counter

fn = sys.argv[1] if len(sys.argv) > 1 else "all_y4_w5_k6.txt"
vars_ = open("m_y4_w5.model.vars").read().split()
cnt = Counter()
nsol = 0
for line in open(fn):
    if line.startswith("SOL"):
        nsol += 1
        for i in map(int, line.split()[1:]):
            cnt[vars_[i]] += 1
print("bases:", nsol)
# note: gdx prints class representatives only; words equivalent to a representative (same single-guess
# closure) are interchangeable with it.
for v, c in sorted(cnt.items(), key=lambda t: -t[1]):
    print(f"{v:10s} {c}")
