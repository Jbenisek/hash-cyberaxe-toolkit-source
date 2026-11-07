from pathlib import Path
import hashlib
import re

ROOT = Path(__file__).resolve().parent
PROOF = ROOT / "pkg_check" / "poseidon-orchard-r2" / "proof.md"
SRC = ROOT / "src"
names = [
    "common.h", "common.c", "pallas.h", "pallas.c", "pallas_consts.h",
    "attack.h", "hgcd.h", "budgets.h", "gen_kern.py", "ntt_kern.h",
    "ntt.c", "poly.c", "loop.c", "lean.c", "line.c", "euclid.c",
    "hgcd.c", "lean_attack.c",
]

lines = PROOF.read_text(encoding="utf-8").splitlines(keepends=True)
embedded = {}
for i, line in enumerate(lines):
    m = re.fullmatch(r"### ([A-Za-z0-9_.-]+)\n", line)
    if not m or m.group(1) not in names:
        continue
    name = m.group(1)
    j = i + 1
    while j < len(lines) and lines[j].strip() != "```c" and lines[j].strip() != "```python":
        j += 1
    if j >= len(lines):
        continue
    j += 1
    k = j
    while k < len(lines) and lines[k].strip() != "```":
        k += 1
    if k >= len(lines):
        continue
    embedded[name] = "".join(lines[j:k])

def h(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

print("source_bridge")
print("proof_sha256", h(PROOF.read_bytes()))
print("embedded_count", len(embedded), "of", len(names))
for name in names:
    cur = (SRC / name).read_bytes()
    emb = embedded.get(name)
    if emb is None:
        print(name, "MISSING_IN_PROOF", "current", h(cur))
        continue
    eb = emb.encode("utf-8")
    exact = cur == eb
    norm = cur.replace(b"\r\n", b"\n").rstrip(b"\n") == eb.replace(b"\r\n", b"\n").rstrip(b"\n")
    print(name, "EXACT" if exact else ("LF_TRAILING_ONLY" if norm else "DIFF"),
          "current", h(cur), "embedded", h(eb), "bytes", len(cur), len(eb))

print("run_log_sha256", h((ROOT / "logs" / "full_r2.txt").read_bytes()))
print("run_log_size", (ROOT / "logs" / "full_r2.txt").stat().st_size)
print("progress_sha256", h((ROOT / "PROGRESS.md").read_bytes()))
