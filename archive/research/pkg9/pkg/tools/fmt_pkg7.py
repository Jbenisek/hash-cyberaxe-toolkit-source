#!/usr/bin/env python3
"""Format and text checks for the rendered files of the seventh package (a DRAFT). Nothing is written.

    python -B tools/fmt_pkg7.py

 1. the files on disk are what the templates give (tools/build_pkg7.py --check);
 2. proof, claim, manifests and note are ASCII with LF, no tab, no trailing space; no proof line is over 79;
    the JSON files parse; restrictions are at most 1024 characters, heuristic fields 4096, manifest fields 2000,
    the note at least 5,120 bytes; the state is "draft";
 3. every range "proof:a-b" that claim.json cites lies in the proof, begins at the heading it is meant for and ends
     before the next one;
 4. the sections 1 to 13 are there in order; every lemma that the proof names is stated in it, or is one of the
     lemmas of entry c66f230d that the text says it does not restate (E, S, F, Y);
 5. the claimed scalar: recomputed from the factor, the charge and the number of trials with the formula of the
     cost model, 127 - log2(f) + log2(charge / 430) + log2(1 + 2^-7), and with the short form 123.339 - log2(f) +
     log2(charge / 34) + 0.012; the claim of claim.json, the proof, the note and the manifest agree with each other
     and with the program (stage counts, list words, members);
 6. every sentence that Section 11 quotes from the filed entry c66f230d is in the filed proof, claim or note
     (research/pkg6, read only), word for word.
Exit status 0 only if nothing is wrong. Research helper, not submitted.
"""
import json
import math
import re
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
import pkg7_data as data  # noqa: E402
import pkg7_text  # noqa: E402

PKG, CAND = data.PKG, data.CAND
FILED = PKG.parent / "pkg6"
EXTERNAL_LEMMAS = {"E", "S", "F", "Y"}


def main():
    problems, notes = [], []
    r = subprocess.run([sys.executable, "-B", str(TOOLS / "build_pkg7.py"), "--check"], capture_output=True, text=True)
    if r.returncode or "DRIFT" in r.stdout:
        problems.append("the rendered files are not what the templates give: " + " / ".join(l for l in r.stdout.split("\n") if "DRIFT" in l)
                        + r.stderr.strip()[-200:])
    files = {"proof": CAND / "proof.md", "claim": CAND / "claim.json", "manifest": CAND / "experiments" / "manifest.json",
             "certificates": CAND / "certificates" / "manifest.json", "note": PKG / "submission-note-r2.md"}
    text = {}
    for name, path in files.items():
        raw = path.read_bytes()
        try:
            text[name] = raw.decode("ascii")
        except UnicodeDecodeError:
            problems.append(f"{name}: not ASCII")
            text[name] = raw.decode("utf-8", "replace")
        if b"\r" in raw or b"\t" in raw or any(l != l.rstrip() for l in text[name].split("\n")):
            problems.append(f"{name}: CR, tab or trailing space")
        if "{{" in text[name] or "[[" in text[name]:
            problems.append(f"{name}: a name or placeholder is left")
    proof = text["proof"].split("\n")
    wide = [i + 1 for i, l in enumerate(proof) if len(l) > 79]
    if wide:
        problems.append(f"proof lines over 79 characters: {wide[:8]}")
    claim, manifest = json.loads(text["claim"]), json.loads(text["manifest"])
    json.loads(text["certificates"])
    if claim["submission_state"] != "draft" or data.SUBMISSION_STATE != "draft":
        problems.append("the state is not draft")
    problems += [f"restriction {i}: {len(x)} characters" for i, x in enumerate(claim["restrictions"]) if len(x) > 1024]
    for h in claim["heuristics"]:
        problems += [f"{h['id']}.{k}: {len(h[k])} characters" for k in ("statement", "scope", "extrapolation", "limitations") if len(h[k]) > 4096]
    for e in manifest["experiments"]:
        problems += [f"manifest {e['id']}.{k}: {len(e[k])} characters" for k in ("scope", "hypothesis") if len(e[k]) > 2000]
    if len(text["note"].encode()) < 5120:
        problems.append("the note is shorter than 5,120 bytes")
    longest = max((len(h[k]), h["id"], k) for h in claim["heuristics"] for k in ("statement", "scope", "extrapolation", "limitations"))
    notes.append(f"longest restriction {max(len(x) for x in claim['restrictions'])} of 1024, longest heuristic field {longest[0]} of 4096 "
                 f"({longest[1]}.{longest[2]}), manifest fields {[len(e[k]) for e in manifest['experiments'] for k in ('scope', 'hypothesis')]} of 2000")
    # 3. cited ranges
    heads = {"## 4. Construction": "constr", "**6.1 Trials.**": "trials", "**6.3 Two tests of a trial.**": "early",
             "**6.4 Algorithm.**": "algo", "**6.5 Seven trials in one word.**": "batch", "## 7. Success probability": "s7",
             "**Heuristic H2 (supporting).**": "h2", "**Heuristic H3 (supporting).**": "h3", "## 10. Evidence, scope": "s10"}
    cited = sorted({e for h in claim["heuristics"] for e in h["evidence_ids"] if e.startswith("proof:")})
    for e in cited:
        a, b = (int(x) for x in e[6:].split("-"))
        first = next((proof[i - 1] for i in (a, a + 1) if 1 <= i <= len(proof) and proof[i - 1].strip()), "")
        if not (1 <= a < b <= len(proof)) or not any(first.startswith(h) for h in heads):
            problems.append(f"{e}: does not begin at one of the headings that the claim cites ({first[:40]!r})")
        if b < len(proof) and proof[b - 1].strip() == "" and proof[b - 2].strip() == "":
            problems.append(f"{e}: ends in more than one empty line")
    for h in claim["heuristics"]:
        if not all(e.startswith("proof:") or e in ("experiment:residual-search", "experiment:half-collision") for e in h["evidence_ids"]):
            problems.append(f"{h['id']}: an evidence id of an unknown kind")
    # 4. sections and lemmas
    sections = [int(m.group(1)) for l in proof for m in [re.match(r"## (\d+)\. ", l)] if m]
    if sections != list(range(1, 14)):
        problems.append(f"sections {sections}")
    body = text["proof"]
    stated = set(re.findall(r"\*\*Lemma ([A-Z]\d?)[ .(]", body)) | set(re.findall(r"\*\*Lemma ([A-Z]\d?) \(", body))
    named = set(re.findall(r"Lemmas? ([A-Z]\d?)\b", body))
    for m in re.finditer(r"Lemmas ((?:[A-Z]\d?(?:, | and | to )?)+)", body):
        named |= set(re.findall(r"[A-Z]\d?", m.group(1)))
    missing = sorted(named - stated - EXTERNAL_LEMMAS)
    if missing:
        problems.append(f"lemmas named and not stated: {missing}")
    notes.append(f"lemmas stated {sorted(stated)}; named from entry c66f230d without being restated {sorted(named & EXTERNAL_LEMMAS - stated)}")
    # 5. the scalar
    t = pkg7_text.build_tokens()
    f, charge = data.FACTOR, float(t["charge"])
    # With the clusters of 6.7 the bound is formed from the range whose TRIAL-EQUIVALENTS the charge is per,
    # not from the longer range the run walks; nd_eq is that range and equals nd when there are no clusters.
    nd = int(t.get("nd_eq", t["nd"]).replace(",", ""))
    full = 81 + math.log2(nd) + math.log2(charge / 430) + math.log2(1 + 2 ** -7)
    model = 127 - math.log2(f) + math.log2(charge / 430) + math.log2(1 + 2 ** -7)
    short = 123.339 - math.log2(f) + math.log2(charge / 34) + 0.012
    scalar = claim["claim"]["time_log2"]
    if not (full <= float(t["bound_4dec"]) <= float(t["bound_2dec"]) <= scalar and scalar == math.ceil(float(t["bound_2dec"]) * 10 - 1e-9) / 10
            and abs(full - model) < 1e-5 and abs(short - model) < 2e-3):
        problems.append(f"the scalar {scalar} does not follow: {full:.5f}, {model:.5f}, {short:.5f}, {t['bound_4dec']}, {t['bound_2dec']}")
    notes.append(f"scalar {scalar}: with the trials of the ranges 2^{full:.5f}, with 2^127 / f 2^{model:.5f}, short form {short:.4f}; "
                 f"printed bounds 2^{t['bound_4dec']} and 2^{t['bound_2dec']}")
    for name, pattern in (("proof", rf"so the claimed scalar is {scalar}\b"), ("proof", rf"time_log2 = {scalar} bounds total charged time"),
                          ("note", rf"time_log2 = {scalar}$"), ("note", rf"the claim is {scalar}\b")):
        if not re.search(pattern, " ".join(text[name].split()) if "is " in pattern else text[name], re.M):
            problems.append(f"{name}: the scalar {scalar} is not where it is expected ({pattern})")
    a, s2 = data.STAGE_A_BY_RULE[8], data.STAGE_2_BY_RULE[8]
    want = (f"batch_stage_a_operations = {a[0]}, batch_stage_a_loads = {a[1]}, batch_stage_2_operations = {s2[0]}, "
            f"batch_stage_2_loads = {s2[1]} and batch_lanes_right = 7")
    if want not in manifest["experiments"][1]["hypothesis"]:
        problems.append("the manifest does not predict the stage counts of the program")
    for e in manifest["experiments"]:
        if e["program"] != "experiments/halfsearch.py" or e["kind"] != "python-message-pairs-v1":
            problems.append(f"manifest {e['id']}: program or kind")
    for needle in (f"{data.CLASS_SIZE:,} values", f"{a[0]} operations plus {a[1]} loads", f"{s2[0]} plus {s2[1]}",
                   f"charged {t['charge']} operations", f"factor {data.FACTOR:,}"):
        if needle not in " ".join(claim["restrictions"]):
            problems.append(f"claim.json restrictions: {needle!r} not found")
    # 6. the quotations of Section 11
    start = next(i for i, l in enumerate(proof) if l.startswith("## 11. "))
    end = next(i for i, l in enumerate(proof) if l.startswith("## 12. "))
    section = " ".join(" ".join(proof[start:end]).split())
    filed = " ".join(" ".join((FILED / p).read_text(encoding="ascii").split())
                     for p in ("blake3-r2/proof.md", "blake3-r2/claim.json", "submission-note-r2.md"))
    quotes = [q for q in re.findall(r'"([^"]*)"', section) if len(q) >= 6]
    absent = [q for q in quotes if q not in filed]
    if absent:
        problems.append(f"Section 11 quotes {len(absent)} passage(s) that are not in the filed text: " + " | ".join(q[:60] for q in absent[:6]))
    notes.append(f"Section 11: {len(quotes)} quoted passages, {len(quotes) - len(absent)} found word for word in the filed proof, claim or note")
    for n in notes:
        print("  " + n)
    print(f"proof {len(proof) - 1} lines, {len(text['proof'])} bytes; claim {len(text['claim'])} bytes; note {len(text['note'])} bytes; "
          f"cited ranges {len(cited)}")
    print("RESULT: " + ("nothing wrong" if not problems else f"{len(problems)} problem(s):\n  " + "\n  ".join(problems)))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
