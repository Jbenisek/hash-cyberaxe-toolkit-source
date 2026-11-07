"""FIX4 check: recompute the new figures and print the line-range boundaries of the evidence ids. Read-only."""

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

import json, math, re, sys
P = _hca_public_path_text('__HCA_WORKSPACE__/research/pkg7')
out = []
T = 24 * 2**40
out.append(f"trials 24*2^40 = {T:,} log2 {math.log2(T):.4f}")
out.append(f"rule A share log2 {math.log2(103079088429 / T):.6f}")
out.append(f"E1 test passes 9537 -> log2 {math.log2(9537 / T):.3f}  (whole-class layout 9520 of 2^44.58 -> {math.log2(9520 / 2**44.58):.3f})")
out.append(f"entry share {98688658735 / 3769840435200:.6f}; /0.03125 = {98688658735 / 3769840435200 / 0.03125:.4f}; indep 1-(255/256)^7 {1 - (255 / 256)**7:.6f}")
out.append(f"T/(3*2^30) = {T / (3 * 2**30):.1f}; E3 marker ratio rates {2.392729e-10 / 2.022110e-10:.4f}; 268/6314/2^-8 = {268 / 6314 * 256:.2f}")
out.append(f"small: 30*2^34 = {30 * 2**34:,}; z {(121 - 120.23) / 10.96:+.3f}; sd/pred {10.96 / 120.23:.4f}; first stage z {(2013236457 - 2013265920) / 44869.4:+.3f}; expected {515396075520 / 256:,.0f}")
out.append(f"weighted model good/bad: {1.0848 - 1:+.4f} {0.9152 - 1:+.4f}")
c = json.load(open(f'{P}/blake3-r2/claim.json'))
for h in c['heuristics']:
    out.append(f"{h['id']}: lengths " + ", ".join(f"{k} {len(h[k])}" for k in ('statement', 'scope', 'extrapolation', 'limitations')) + f"; ids {h['evidence_ids']}")
out.append("claim top keys: " + ", ".join(sorted(c)))
lines = open(f'{P}/blake3-r2/proof.md').read().split('\n')
ids = sorted({e for h in c['heuristics'] for e in h['evidence_ids'] if e.startswith('proof:')})
for e in ids:
    a, b = map(int, e[6:].split('-'))
    out.append(f"{e}: [{a}] {lines[a - 1][:70]!r} ... [{b}] {lines[b - 1][:50]!r} | next [{b + 1}] {lines[b][:50]!r}")
data = open(f'{P}/blake3-r2/proof.md', 'rb').read() + open(f'{P}/submission-note-r2.md', 'rb').read() + open(f'{P}/blake3-r2/claim.json', 'rb').read()
out.append(f"non-ascii bytes {sum(1 for x in data if x > 127)}; CR {data.count(13)}; tabs {data.count(9)}")
open(f'{P}/work/fix4/check/nums_out.txt', 'w').write('\n'.join(out) + '\n')
print(len(out), 'lines written')
