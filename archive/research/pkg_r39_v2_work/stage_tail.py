# stage_tail.py PKG TAILDIR QDECL : r39tail.py = the pair's replica (r39tail_free.py) with its frozen 14-run EXP table and QDECL
import sys, json
pkg, D, q = sys.argv[1], sys.argv[2], sys.argv[3]
lines = []
for i in range(1, 15):
    d = json.load(open("%s/out_%02d.json" % (D, i)))["trials"]; o0 = d[0]["observations"]
    ks = [o0["k%d" % t] for t in range(18, 24)]; hs = sum(t["observations"]["hits"] for t in d[1:21])
    cls = [sum(t["observations"]["c%s" % c] for t in d[1:21]) for c in ("00", "01", "10", "11")]
    lines.append("%s|%.6f|%d|%s" % (",".join(map(str, ks)), o0["log2_carrier"], hs, ",".join(map(str, cls))))
assert lines == open(D + "/EXP_S.txt").read().strip().splitlines()
t = open(D + "/r39tail_free.py", encoding="utf-8").read()
a = 'EXP_S="""\n"""'; assert t.count(a) == 1 and t.count("QDECL=-75.47\n") == 1
t = t.replace(a, 'EXP_S="""\n' + "\n".join(lines) + '\n"""').replace("QDECL=-75.47\n", "QDECL=%s\n" % q)
open(pkg + "/sha256/experiments/r39tail.py", "w", encoding="utf-8", newline="\n").write(t); print("ok", len(t.encode()))
