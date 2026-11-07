#!/usr/bin/env python3
"""Format checks for the pkg6 files, the line ranges that claim.json cites, and the arithmetic of the claim.

    python -B tools/fmt_pkg6.py [--write-ranges] [--fix-eol]

--write-ranges  first renders the package from src/ and tools/pkg6_data.py (tools/build_pkg6.py); the evidence
                ranges of claim.json are part of that rendering, because claim.json is a rendered file.
--fix-eol       rewrites CRLF as LF in the checked files.
Without options nothing is written: the files on disk are checked as they are, and the tool says whether they
still are what the templates give (a rendered file that was edited by hand shows up as DRIFT).
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
import build_pkg6 as build  # noqa: E402
import pkg6_data as data  # noqa: E402

PKG, CAND = data.PKG, data.CAND
PROOF, CLAIM, NOTE = build.PROOF, build.CLAIM, build.NOTE
FILES = [PROOF, CLAIM, NOTE, build.PROGRAM, build.MANIFEST, CAND / "certificates" / "manifest.json", PKG / "check_pkg6.py",
         PKG / "validate_pkg6.sh", PKG / "src" / "proof_head.md", PKG / "src" / "proof_evidence.md", PKG / "src" / "claim.json",
         PKG / "src" / "manifest.json", PKG / "src" / "note.md"]
wrong = []

if "--write-ranges" in sys.argv:
    done = subprocess.run([sys.executable, "-B", str(TOOLS / "build_pkg6.py")], capture_output=True)
    print(done.stdout.decode("utf-8", "replace").rstrip())
    if done.returncode != 0:
        print(done.stderr.decode("utf-8", "replace").rstrip())
        sys.exit("build failed; nothing below was checked")

fix = "--fix-eol" in sys.argv
for path in FILES:
    if not path.exists():
        print(f"{path.name}: MISSING")
        wrong.append(f"{path.name} missing")
        continue
    raw = path.read_bytes()
    if fix and b"\r" in raw:
        raw = raw.replace(b"\r\n", b"\n")
        path.write_bytes(raw)
    text = raw.decode("utf-8")
    lines = text.split("\n")
    nonascii = [i + 1 for i, l in enumerate(lines) if any(ord(ch) > 127 for ch in l)]
    trailing = [i + 1 for i, l in enumerate(lines) if l != l.rstrip()]
    tabs = [i + 1 for i, l in enumerate(lines) if "\t" in l]
    rel = path.relative_to(PKG)
    print(f"{rel}: {len(raw)} bytes, {text.count(chr(10))} LF, {raw.count(bytes([13]))} CR, ends with LF {text.endswith(chr(10))}, "
          f"non-ASCII lines {nonascii}, trailing-space lines {trailing}, tab lines {tabs}")
    if raw.count(bytes([13])) or nonascii or trailing or tabs or not text.endswith("\n"):
        wrong.append(f"{rel}: format")
    if path.suffix == ".md" and "src" not in path.parts:
        long_lines = [(i + 1, len(l)) for i, l in enumerate(lines) if len(l) > 79]
        print("   lines over 79 characters:", long_lines)
        if path == PROOF and long_lines:
            wrong.append("proof.md: a line over 79 characters")

proof = PROOF.read_text(encoding="ascii")
ranges = build.proof_ranges(proof)
plines = proof.split("\n")
for key, label in (("constr", "Sections 4 and 5, steps S1 and T, Lemmas S, F, Y and the theorem"),
                   ("trials", "6.1, trials and Lemmas Q, T"), ("early", "6.3 with Lemmas E, N and A"),
                   ("algo", "6.4, the algorithm"), ("batch", "6.5, the batch and its count"),
                   ("s7", "Section 7 to 'None of the three heuristics is proved'"),
                   ("h2", "H2 paragraph"), ("h3", "H3 paragraph"), ("s10", "Section 10 to the line before Scope")):
    a, b = [int(x) for x in ranges[key].split(":")[1].split("-")]
    print(f"{label}: {ranges[key]}\n     first: {plines[a - 1][:70]}\n     last:  {plines[b - 1][:70]}")
print("proof line count:", len(plines) - 1)

claim = json.loads(CLAIM.read_text(encoding="ascii"))
used = set()
for h in claim["heuristics"]:
    print(h["id"], h["evidence_ids"], "| extrapolation", len(h["extrapolation"]), "chars | limitations", len(h["limitations"]), "chars")
    used.update(e for e in h["evidence_ids"] if e.startswith("proof:"))
missing = sorted(used - {ranges[k] for k in ("constr", "trials", "early", "algo", "batch", "s7", "h2", "h3", "s10")})
print("claim.json proof ranges that match no range above:", missing if missing else "none")
if missing:
    wrong.append("claim.json cites ranges that the proof does not have: run with --write-ranges")

print("names or placeholders left in the rendered files:")
left = 0
for path in (PROOF, CLAIM, NOTE, build.MANIFEST, build.PROGRAM):
    for i, l in enumerate(path.read_text(encoding="ascii").split("\n")):
        for name in re.findall(r"\[\[[A-Z0-9_]+\]\]|\{\{[A-Za-z0-9_]+\}\}", l):
            print(f"  {path.name}:{i + 1}: {name}")
            left += 1
print("  none" if not left else f"  {left}")
if left:
    wrong.append("a name or placeholder is left")

print("field lengths (limits: restrictions 1024, heuristic fields 4096, manifest scope/hypothesis 2000, note >= 5120 bytes):")
print("  restrictions:", [len(r) for r in claim["restrictions"]])
for h in claim["heuristics"]:
    print(f"  {h['id']}:", {k: len(h[k]) for k in ("statement", "scope", "extrapolation", "limitations")})
man = json.loads(build.MANIFEST.read_text(encoding="ascii"))
print("  manifest:", [(e["id"], len(e["scope"]), len(e["hypothesis"])) for e in man["experiments"]])
print("  note bytes:", len(NOTE.read_bytes()))
print("  claim:", claim["claim"], "| state", claim["submission_state"])

d = data.derive()
print("arithmetic of the claim, recomputed from tools/pkg6_data.py:")
print(f"  pin {' '.join(data.hx(v) for v in data.PIN.values())}; W4' {data.hx(d['W4B'])}; delta {data.hx(d['delta'])}; "
      f"Y3 {data.hx(d['Y3'])} Y3' {data.hx(d['Y3B'])} DY3 {data.hx(d['DY3'])}; Y11 {data.hx(d['Y11'])} Y11' {data.hx(d['Y11B'])} "
      f"DY11 {data.hx(d['DY11'])}")
print(f"  class eta {data.hx(data.ETA)}: x {data.hx(d['x'])} (bit 31 {'set' if d['x'] >> 31 else 'clear'}), DY3 + x {data.hx(d['qsum'])}, "
      f"mask {data.hx(d['qmask'])}, value {data.hx(d['qvalue'])}, {d['fixed']} fixed and {d['free']} free bits, {d['members']:,} members; "
      f"lists of {d['list_words']:,} words ({d['full_batches']:,} full batches and {d['rest']} members in the last)")
print(f"  factor 2^{data.LOG2_FACTOR}; trials 2^{d['T']} = 2^{d['ctx']} pairs (vc any word, vd < 2^{d['d_bits']}) "
      f"* 2^32 values of X14 * 2^{d['free']} members; pass budget 2^{d['pass_budget']}")
print(f"  per X14, budgeted: {d['list_words']:,} * {d['stage_a']} + {d['list_words']:,} * {d['stage_2']} / {2 ** data.STAGE_2_LOG2_SHARE} + {data.PREP_OPS} = "
      f"{float(d['alpha_ops']):,.2f} < {data.CHARGE} * {d['members']:,} = {float(d['alpha_charged']):,.1f} "
      f"({float(d['alpha_ops'] / d['members']):.4f} per trial budgeted, {float(d['alpha_expected'] / d['members']):.4f} expected at 7 * 2^-{d['rule_conditions']})")
print(f"  main term 2^{d['main_exp']:.5f}; terms after the first 2^{d['rest_exp']:.5f} < 2^{d['seventh']:.3f}; total as written "
      f"2^{d['true_total']:.5f} < stated 2^{d['total_exp']:.4f} < 2^{d['total_bound']:.2f} <= time_log2 {d['time_log2']:.1f}")
print(f"  smallest factor for 0.39: {d['f_min']:,} <= {2 ** data.LOG2_FACTOR:,}; success at the assumed factor "
      f"{1 - math.exp(-0.5) - 0.003:.5f}; search memory {d['online_bytes']:,} bytes < 2^{d['online_log2']}")
if claim["claim"]["time_log2"] != d["time_log2"]:
    wrong.append("claim.json time_log2 is not the bound of pkg6_data.py")

check = subprocess.run([sys.executable, "-B", str(TOOLS / "build_pkg6.py"), "--check"], capture_output=True)
drift = [l for l in check.stdout.decode("utf-8", "replace").split("\n") if l.startswith("DRIFT")]
print("rendered files against the templates:", "as rendered" if check.returncode == 0 and not drift else "")
for l in drift:
    print("  " + l)
if check.returncode != 0:
    print("  " + (check.stderr.decode("utf-8", "replace").strip().split("\n") or [""])[-1][:300])
    wrong.append("the rendered files are not what the templates give (python -B tools/build_pkg6.py)")
print("RESULT:", "nothing wrong" if not wrong else "WRONG: " + "; ".join(wrong))
sys.exit(1 if wrong else 0)
