"""Integration of the three fixes into research/pkg10/pkg. Run step by step:

  tools_integrate.py edits   EDITS_FILE TARGET          apply (OLD, NEW) pairs; each OLD must occur exactly once
  tools_integrate.py heur    HEURISTICS.json            append new heuristic entries to claim.json (ids must be new)
  tools_integrate.py splice  HEAD NEXT NEWFILE           replace a proof block by header anchors
  tools_integrate.py repoint                            recompute every proof:<a>-<b> evidence_id from ANCHORS below
  tools_integrate.py nums    OLD=NEW [OLD=NEW ...]      replace figures in proof, claim and note, reporting counts

Edit pairs are read from fenced blocks: a line OLD (or **OLD**, ### OLD, OLD:) followed by a ``` block, then NEW
likewise. Anything that does not match exactly once stops the run before any file is written."""

# Publication path adapter: resolve data paths from the extracted source tree.
def _hca_public_path_text(value):
    if "__HCA_WORKSPACE__/" not in value:
        return value
    import os as _hca_os
    from pathlib import Path as _hca_Path
    root = _hca_os.environ.get("HASHCYBERAXE_WORKSPACE")
    if root is None:
        here = _hca_Path(__file__).resolve().parent
        root = next((str(p) for p in (here, *here.parents) if (p / "research").is_dir()), None)
    if root is None:
        raise FileNotFoundError("Extract the research source tree, or set HASHCYBERAXE_WORKSPACE to its archive directory.")
    return value.replace("__HCA_WORKSPACE__/", str(_hca_Path(root).resolve()).replace("\\", "/") + "/")

import json, re, sys

P = _hca_public_path_text('__HCA_WORKSPACE__/research/pkg10/pkg')
PROOF, CLAIM, NOTE = P + "/blake3-r2/proof.md", P + "/blake3-r2/claim.json", P + "/submission-note-r2.md"

def rd(p): return open(p, encoding="utf-8", newline="\n").read()
def wr(p, t): open(p, "w", encoding="utf-8", newline="\n").write(t)

def parse_pairs(text):
    blocks, label = [], None
    lines = text.split("\n"); i = 0
    while i < len(lines):
        l = lines[i].strip()
        m = re.match(r"^(?:#+\s*|\*\*)?(OLD|NEW)\b", l, re.I)
        if m:
            label = m.group(1).upper()
        if l.startswith("```") and label:
            j = i + 1
            while j < len(lines) and not lines[j].strip().startswith("```"):
                j += 1
            blocks.append((label, "\n".join(lines[i + 1:j])))
            label = None; i = j
        i += 1
    pairs = []
    for k in range(0, len(blocks) - 1, 2):
        (la, a), (lb, b) = blocks[k], blocks[k + 1]
        if (la, lb) != ("OLD", "NEW"):
            sys.exit(f"STOP: block {k} is {la} followed by {lb}")
        pairs.append((a, b))
    return pairs

def cmd_edits(edits_file, target):
    pairs = parse_pairs(rd(edits_file))
    t = rd(target); bad = []
    for n, (a, b) in enumerate(pairs, 1):
        c = t.count(a)
        if c != 1:
            bad.append(f"  pair {n}: OLD found {c} times: {a[:90]!r}")
    if bad:
        print(f"STOP: {len(bad)} of {len(pairs)} pairs do not match exactly once; nothing written"); print("\n".join(bad)); sys.exit(1)
    for a, b in pairs:
        t = t.replace(a, b)
    wr(target, t); print(f"{len(pairs)} pairs applied to {target.split('/')[-1]}")

def cmd_heur(hfile):
    c = json.loads(rd(CLAIM)); new = json.loads(rd(hfile))
    new = new if isinstance(new, list) else new.get("heuristics", [new])
    ids = {h["id"] for h in c["heuristics"]}
    for h in new:
        if h["id"] in ids: sys.exit(f"STOP: {h['id']} already in claim.json")
    c["heuristics"] += new
    wr(CLAIM, json.dumps(c, indent=2, ensure_ascii=False) + "\n"); print("heuristics now:", [h["id"] for h in c["heuristics"]])

def cmd_splice(head, nxt, newfile):
    L = rd(PROOF).split("\n")
    hs = [i for i, l in enumerate(L) if l.startswith(head)]; ns = [i for i, l in enumerate(L) if l.startswith(nxt)]
    if len(hs) != 1 or len(ns) != 1 or ns[0] <= hs[0]: sys.exit(f"STOP: head x{len(hs)}, next x{len(ns)}")
    new = rd(newfile).strip("\n").split("\n")
    if not new[0].startswith(head): sys.exit(f"STOP: new block starts {new[0][:50]!r}")
    out = L[:hs[0]] + new + [""] + L[ns[0]:]
    wr(PROOF, "\n".join(out)); print(f"{head!r}: {ns[0]-hs[0]} -> {len(new)+1} lines")

# Each proof range of the claim, by the line that starts it and the line that starts the block after it.
ANCHORS = {
    "S4-5":  ("## 4. ", "## 6. "),
    "S6.1-2": ("**6.1 Trials.**", "**6.3 Two tests"),
    "S6.3":  ("**6.3 Two tests", "**6.4 Algorithm.**"),
    "S6.4":  ("**6.4 Algorithm.**", "**6.5 Seven trials"),
    "S6.5+": ("**6.5 Seven trials", "## 7. "),
    "S7":    ("## 7. ", "## 8. "),
    "H2":    ("**Heuristic H2", "**Heuristic H3"),
    "H3":    ("**Heuristic H3", "**Heuristic H4"),
    "H4":    ("**Heuristic H4", "**Heuristic H5"),
    "S10":   ("## 10. ", "## 11. "),
}

def span(L, a, b):
    bs = b if isinstance(b, tuple) else (b,)
    s = [i for i, l in enumerate(L) if l.startswith(a)]; e = [i for i, l in enumerate(L) if l.startswith(bs)]
    if len(s) != 1 or not e: return None
    e = min(x for x in e if x > s[0]) if any(x > s[0] for x in e) else None
    if e is None: return None
    while e > s[0] and not L[e - 1].strip(): e -= 1
    return s[0] + 1, e

ANCHORS.update({
    "H5": ("**Heuristic H5", ("**Heuristic H6", "*Sensitivity to the factor.*")),
    "H6": ("**Heuristic H6", "*Sensitivity to the factor.*"),
    "S8": ("## 8. ", "## 9. "),
    "S9": ("## 9. ", "## 10. "),
    "S10-clusters": ("**The clusters of 6.7", "**What does not exist."),
})
# What each heuristic cites. Experiments are kept as they are in claim.json.
CITES = {
    "H1-residual-hit-rate": ["S4-5", "S6.1-2", "S6.3", "S6.4", "S6.5+", "S7", "S10"],
    "H2-e1-test-passes":    ["S6.3", "S6.4", "H2", "S10"],
    "H3-stage-2-entries":   ["S6.3", "S6.4", "S6.5+", "H3", "S10"],
    "H4-cluster-yield":     ["S6.5+", "H4", "S8", "S10-clusters"],
    "H5-cluster-mass":      ["S6.5+", "H5", "S10-clusters"],
    "H6-neighbour-budgets": ["S6.4", "H6", "S8", "S10-clusters"],
}

def cmd_repoint(write=True):
    L = rd(PROOF).split("\n")
    spans = {k: span(L, a, b) for k, (a, b) in ANCHORS.items()}
    for k, v in spans.items():
        print(f"  {k:<13} {v}")
    c = json.loads(rd(CLAIM)); missing = []
    for h in c["heuristics"]:
        want = CITES.get(h["id"])
        if not want:
            missing.append(h["id"]); continue
        exp = [r for r in h.get("evidence_ids", []) if r.startswith("experiment:")]
        refs = []
        for k in want:
            s = spans.get(k)
            if s is None:
                missing.append(f"{h['id']}:{k}"); continue
            refs.append(f"proof:{s[0]}-{s[1]}")
        h["evidence_ids"] = exp + refs
        print(f"  {h['id']}: {h['evidence_ids']}")
    if missing:
        print("STOP: no anchor for", missing); sys.exit(1)
    if write:
        wr(CLAIM, json.dumps(c, indent=2, ensure_ascii=False) + "\n"); print("claim.json evidence_ids rewritten")

def cmd_nums(pairs):
    for f in (PROOF, CLAIM, NOTE):
        t = rd(f); rep = []
        for p in pairs:
            a, b = p.split("=", 1); k = t.count(a)
            if k: t = t.replace(a, b); rep.append(f"{a}->{b} x{k}")
        wr(f, t); print(f"{f.split('/')[-1]}: {', '.join(rep) or 'nothing'}")

if __name__ == "__main__":
    c = sys.argv[1]
    if c == "edits": cmd_edits(sys.argv[2], {"proof": PROOF, "claim": CLAIM, "note": NOTE}.get(sys.argv[3], sys.argv[3]))
    elif c == "heur": cmd_heur(sys.argv[2])
    elif c == "splice": cmd_splice(sys.argv[2], sys.argv[3], sys.argv[4])
    elif c == "repoint": cmd_repoint()
    elif c == "nums": cmd_nums(sys.argv[2:])
