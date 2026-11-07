#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# usage: stage_r.sh R CLONE   -- puts pkg_stage_r<R>/ into /root/hashsmash/yukon/<CLONE>/pareto/candidates/poseidon, runs the organizer's
# pareto_candidate.py once, writes STAGED.sha256 and copies the submission note.  Nothing is submitted; no yukon command is run.
set -euo pipefail
R=$1; CLONE=$2
SRC="${HASHCYBERAXE_WORKSPACE}/research/poseidon/orchard/lean_r2/pkg_stage_r$R"
ROOT=/root/hashsmash/yukon/$CLONE
[ -d "$ROOT" ] || cp -a /root/hashsmash/yukon/pos_r1_pkg "$ROOT"
CAND="$ROOT/pareto/candidates/poseidon"
rm -rf "$CAND"; mkdir -p "$CAND/certificates"
install -m 0644 "$SRC/claim.json" "$CAND/claim.json"
install -m 0644 "$SRC/proof.md" "$CAND/proof.md"
for f in "$SRC"/certificates/*; do install -m 0644 "$f" "$CAND/certificates/$(basename "$f")"; done
install -m 0644 "$SRC/submission-note.md" "$ROOT/pareto/submission-note.md"
if grep -l $'\r' "$CAND"/proof.md "$CAND"/claim.json "$CAND"/certificates/manifest.json >/dev/null 2>&1; then echo "CRLF found"; exit 1; fi
find "$CAND" -type f -printf '%m %7s %p\n' | sort -k3 | head -50
cd "$ROOT/pareto"
echo "--- pareto_candidate.py --family poseidon --rounds $R"
python3 ../scripts/pareto_candidate.py --family poseidon --rounds $R
(cd candidates/poseidon && find . -type f | LC_ALL=C sort | xargs sha256sum) > STAGED.sha256
wc -c submission-note.md STAGED.sha256 candidates/poseidon/proof.md candidates/poseidon/claim.json
