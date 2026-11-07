#!/usr/bin/env python3
# lens EVERY FIGURE: claim.json and the manifests against the schemas, field lengths, evidence ranges, ASCII, SHA-256 quoted
import json, re, sys, os, hashlib
B = 'historical-sources/~~Projects/~HashSmash/workspace'
PK = B + "/research/pkg5"
P = PK + "/blake3-r2"
out = open(PK + "/review/fig_schema.out", "w")
def say(*a): print(*a, file=out)
claim = json.load(open(P + "/claim.json", encoding="utf-8"))
import jsonschema
for name, sch, doc in (("claim.json", "claim-frontier-v3.schema.json", claim),
                       ("experiments/manifest.json", "experiment-manifest-v1.schema.json", json.load(open(P + "/experiments/manifest.json"))),
                       ("certificates/manifest.json", "certificate-manifest-local-v2.schema.json", json.load(open(P + "/certificates/manifest.json")))):
    schema = json.load(open(B + "/hash-smash/schemas/" + sch, encoding="utf-8"))
    errs = sorted(jsonschema.Draft202012Validator(schema).iter_errors(doc), key=lambda e: list(map(str, e.path)))
    say(name, "against", sch, ": errors", len(errs))
    for e in errs[:6]:
        say("   ", list(e.path), e.message[:160])
for i, r in enumerate(claim["restrictions"]):
    say("restriction", i, "len", len(r), "(max 1024)", "OVER" if len(r) > 1024 else "ok")
for h in claim["heuristics"]:
    for k in ("statement", "scope", "extrapolation", "limitations"):
        n = len(h[k])
        say(h["id"], k, n, "(max 4096)", "OVER" if n > 4096 else "ok")
lines = open(P + "/proof.md", encoding="utf-8").read().split("\n")
say("proof lines:", len(lines), "last empty:", lines[-1] == "")
heads = [(i + 1, l) for i, l in enumerate(lines) if l.startswith("## ") or re.match(r"\*\*6\.\d", l) or l.startswith("**Heuristic") or l.startswith("**Limits of") or l.startswith("**Scope and")]
say("section starts:", "; ".join("%d %s" % (i, l[:34]) for i, l in heads))
for h in claim["heuristics"]:
    for e in h["evidence_ids"]:
        m = re.match(r"proof:(\d+)(?:-(\d+))?$", e)
        if m:
            a = int(m.group(1)); b = int(m.group(2) or a)
            say(h["id"], e, "| before:", repr(lines[a - 2][:30]), "| first:", lines[a - 1][:50], "| last:", lines[b - 1][:50], "| next:", repr(lines[b][:30]) if b < len(lines) else "<EOF>")
        else:
            say(h["id"], e)
man = json.load(open(P + "/experiments/manifest.json"))
say("experiment ids in manifest:", [x.get("id") or x.get("experiment_id") for x in man.get("experiments", [])])
for f in (P + "/proof.md", P + "/claim.json", PK + "/submission-note-r2.md", P + "/experiments/halfsearch.py", P + "/experiments/manifest.json"):
    s = open(f, "rb").read()
    na = [(i, c) for i, c in enumerate(s) if c > 126 or (c < 32 and c not in (10, 13, 9))]
    longest = max(len(l) for l in s.split(b"\n"))
    say(os.path.basename(f), "bytes", len(s), "sha256", hashlib.sha256(s).hexdigest(), "non-ascii/control:", len(na), "CR:", s.count(b"\r"), "tabs:", s.count(b"\t"), "longest line", longest)
# SHA-256 strings quoted anywhere in the package texts and logs, against the files
shas = {}
for root, _, files in os.walk(PK):
    if "/review" in root:
        continue
    for fn in files:
        p = os.path.join(root, fn)
        try:
            t = open(p, encoding="utf-8", errors="replace").read()
        except Exception:
            continue
        for m in re.finditer(r"\b[0-9a-f]{64}\b", t):
            shas.setdefault(m.group(0), set()).add(os.path.relpath(p, PK))
have = {}
for root, _, files in os.walk(PK):
    for fn in files:
        p = os.path.join(root, fn)
        have[hashlib.sha256(open(p, "rb").read()).hexdigest()] = os.path.relpath(p, PK)
home = os.path.expanduser("~/hashsmash/bin/night_pair_calc2")
if os.path.exists(home):
    have[hashlib.sha256(open(home, "rb").read()).hexdigest()] = "~/hashsmash/bin/night_pair_calc2 (read only)"
src = B + "/research/night/main/pair_calc.c"
if os.path.exists(src):
    have[hashlib.sha256(open(src, "rb").read()).hexdigest()] = "research/night/main/pair_calc.c"
for s, where in sorted(shas.items()):
    say("sha", s[:16], "quoted in", sorted(where)[:4], "->", have.get(s, "NO FILE WITH THIS HASH FOUND"))
out.close()
print("written")
