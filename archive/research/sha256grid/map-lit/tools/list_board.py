import json, sys, re
p = sys.argv[1]
mode = sys.argv[2] if len(sys.argv) > 2 else "list"
d = json.load(open(p, encoding="utf-8"))
b = d["benchmark"]
subs = d["submissions"]
if mode == "bench":
    for k in ["trackName", "status", "baselineScore", "currentBestScore", "closesAt", "openedAt", "description"]:
        print(k, "=", repr(b.get(k))[:600])
    print("baselineMetrics", json.dumps(b.get("baselineMetrics"))[:400])
    print("currentBestMetrics", json.dumps(b.get("currentBestMetrics"))[:400])
    s = subs[0]
    print("sample judgment:", json.dumps(s.get("judgment"))[:800])
    print("sample officialMetrics:", json.dumps(s.get("officialMetrics"))[:400])
    print("sample evaluation:", json.dumps(s.get("evaluation"))[:400])
    print("sample rejectionReason:", json.dumps(s.get("rejectionReason"))[:300])
    sys.exit()

def head(note, n=260):
    if not note:
        return ""
    t = note
    t = re.sub(r"^\s*Model:.*?\n", "", t)
    t = re.sub(r"^\s*Harness:.*?\n", "", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t[:n]

def title(note):
    if not note:
        return ""
    for line in note.splitlines():
        if line.strip().startswith("#"):
            return line.strip()[:160]
    return ""

rows = []
for s in subs:
    sc = s.get("officialScore")
    rows.append((sc if isinstance(sc, (int, float)) else 1e9, s))
rows.sort(key=lambda r: (r[0], r[1].get("createdAt") or ""))
for _, s in rows:
    note = s.get("note") or ""
    print("\t".join([
        s["id"][:8], str(s.get("solverUsername")), str(s.get("status")),
        str(s.get("claimedScore")), str(s.get("officialScore")),
        str(s.get("promotionStatus")), (s.get("createdAt") or "")[:16], str(len(note)),
    ]))
    print("    T:", title(note))
    print("    H:", head(note))
