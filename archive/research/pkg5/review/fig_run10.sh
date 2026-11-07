#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# lens EVERY FIGURE: the package's own self-test and cross-check script (writes nothing), output to a file
P="${HASHCYBERAXE_WORKSPACE}"/research/pkg5
cd "$P" || exit 1
before=$(find "$P" -path "$P/review" -prune -o -type f -print0 | sort -z | xargs -0 sha256sum | sha256sum | cut -c1-16)
PYTHONDONTWRITEBYTECODE=1 nice -n 10 python3 -B tools/selftest_pkg5.py > "$P/review/fig_selftest_pkg5.out" 2> "$P/review/fig_selftest_pkg5.err"
echo "exit $? ; ok lines $(grep -c '\[ok\]' "$P/review/fig_selftest_pkg5.out") ; FAIL lines $(grep -c '\[FAIL\]' "$P/review/fig_selftest_pkg5.out") ; $(tail -1 "$P/review/fig_selftest_pkg5.out" | cut -c1-120)"
after=$(find "$P" -path "$P/review" -prune -o -type f -print0 | sort -z | xargs -0 sha256sum | sha256sum | cut -c1-16)
echo "all pkg5 files outside review unchanged: $([ "$before" = "$after" ] && echo yes || echo NO)"
grep -E "in that loop|night_batch4|batches of|trials against" "$P/review/fig_selftest_pkg5.out" | cut -c1-240 | head -5
