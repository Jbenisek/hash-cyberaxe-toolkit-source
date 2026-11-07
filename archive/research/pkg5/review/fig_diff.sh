#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# lens EVERY FIGURE: diffs of pkg5 against pkg4 (read only; output in review/)
P="${HASHCYBERAXE_WORKSPACE}"/research
R="$P/pkg5/review"
diff -u "$P/pkg4/blake3-r2/proof.md" "$P/pkg5/blake3-r2/proof.md" > "$R/fig_diff_proof.txt"
diff -u "$P/pkg4/submission-note-r2.md" "$P/pkg5/submission-note-r2.md" > "$R/fig_diff_note.txt"
diff -u "$P/pkg4/blake3-r2/experiments/halfsearch.py" "$P/pkg5/blake3-r2/experiments/halfsearch.py" > "$R/fig_diff_halfsearch.txt"
diff -u "$P/pkg4/blake3-r2/experiments/manifest.json" "$P/pkg5/blake3-r2/experiments/manifest.json" > "$R/fig_diff_manifest.txt"
diff -u "$P/pkg4/tools/pkg4_data.py" "$P/pkg5/tools/pkg5_data.py" > "$R/fig_diff_data.txt"
diff -u "$P/pkg4/tools/build_pkg4.py" "$P/pkg5/tools/build_pkg5.py" > "$R/fig_diff_build.txt"
diff -u "$P/pkg4/tools/fmt_pkg4.py" "$P/pkg5/tools/fmt_pkg5.py" > "$R/fig_diff_fmt.txt"
diff -u "$P/pkg4/check_pkg4.py" "$P/pkg5/check_pkg5.py" > "$R/fig_diff_check.txt"
diff -u "$P/pkg4/tools/selftest_pkg4.py" "$P/pkg5/tools/selftest_pkg5.py" > "$R/fig_diff_selftest.txt"
diff -u "$P/pkg4/validate_pkg4.sh" "$P/pkg5/validate_pkg5.sh" > "$R/fig_diff_validate.txt"
# claim.json: one string per line for a readable diff
python3 - "$P" "$R" <<'EOF'
import json, sys, textwrap
P, R = sys.argv[1], sys.argv[2]
def flat(path):
    c = json.load(open(path))
    out = []
    def walk(o, pre):
        if isinstance(o, dict):
            for k, v in o.items(): walk(v, pre + "." + k)
        elif isinstance(o, list):
            for i, v in enumerate(o): walk(v, pre + f"[{i}]")
        else:
            s = str(o)
            # one sentence per line
            parts = s.replace("; ", ";\n").replace(". ", ".\n").split("\n")
            for p in parts: out.append(f"{pre}: {p}")
    walk(c, "")
    return out
for k in ("pkg4", "pkg5"):
    open(f"{R}/fig_claim_{k}.flat", "w").write("\n".join(flat(f"{P}/{k}/blake3-r2/claim.json")) + "\n")
EOF
diff -u "$R/fig_claim_pkg4.flat" "$R/fig_claim_pkg5.flat" > "$R/fig_diff_claim.txt"
wc -l "$R"/fig_diff_*.txt | tail -12
