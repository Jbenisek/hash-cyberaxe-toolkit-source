import re, sys
f, pat = sys.argv[1], sys.argv[2]
w = int(sys.argv[3]) if len(sys.argv) > 3 else 100
for n, l in enumerate(open(f, encoding="utf-8").read().split("\n"), 1):
    for m in re.finditer(pat, l):
        print("%d: ...%s" % (n, l[max(0, m.start() - w):m.end() + w].replace("\n", " ")))
