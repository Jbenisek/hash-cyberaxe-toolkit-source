#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# lens EVERY FIGURE: the package's format and drift check, without options (writes nothing), and all tokens of the data module
P="${HASHCYBERAXE_WORKSPACE}"/research/pkg5
cd "$P" || exit 1
before=$(sha256sum blake3-r2/proof.md blake3-r2/claim.json submission-note-r2.md blake3-r2/experiments/halfsearch.py blake3-r2/experiments/manifest.json | sha256sum | cut -c1-16)
PYTHONDONTWRITEBYTECODE=1 nice -n 10 python3 -B tools/fmt_pkg5.py > "$P/review/fig_fmt.out" 2> "$P/review/fig_fmt.err"
echo "fmt exit $? ; $(tail -1 "$P/review/fig_fmt.out" | cut -c1-200)"
PYTHONDONTWRITEBYTECODE=1 nice -n 10 python3 -B tools/pkg5_data.py > "$P/review/fig_tokens.out" 2> "$P/review/fig_tokens.err"
echo "tokens exit $? lines $(wc -l < "$P/review/fig_tokens.out")"
after=$(sha256sum blake3-r2/proof.md blake3-r2/claim.json submission-note-r2.md blake3-r2/experiments/halfsearch.py blake3-r2/experiments/manifest.json | sha256sum | cut -c1-16)
echo "package files unchanged by these runs: $([ "$before" = "$after" ] && echo yes || echo NO)"
grep -E "DRIFT|unchanged|as rendered" "$P/review/fig_fmt.out" | cut -c1-160 | head -6
find "$P" -name __pycache__ | head -3
