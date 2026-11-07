#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# FIX4 check: compare prev snapshot with present files, verify frozen hashes. Read-only except output in check/.
P="${HASHCYBERAXE_WORKSPACE}/research/pkg7"
V="$P/work/fix4/prev"; O="$P/work/fix4/check/cmp_out.txt"
{
echo "== prev snapshot vs prev FROZEN =="
(cd "$V/blake3-r2" && sha256sum -c "$V/FROZEN_fix.sha256" 2>&1)
echo "prev note: $(sha256sum "$V/submission-note-r2.md" | cut -c1-64) vs $(cut -c1-64 "$V/FROZEN_fix_note.sha256")"
echo "== present vs present FROZEN =="
(cd "$P/blake3-r2" && sha256sum -c "$P/FROZEN_fix.sha256" 2>&1)
echo "present note: $(sha256sum "$P/submission-note-r2.md" | cut -c1-64) vs $(cut -c1-64 "$P/FROZEN_fix_note.sha256")"
echo "== files present in package not listed in FROZEN =="
(cd "$P/blake3-r2" && find . -type f | sort)
echo "== per-file prev vs present =="
(cd "$V" && find . -type f | sort) | while read -r f; do
  a=$(sha256sum "$V/$f" | cut -c1-64)
  if [ -f "$P/$f" ]; then b=$(sha256sum "$P/$f" | cut -c1-64); else b=MISSING; fi
  [ "$a" = "$b" ] && s=SAME || s=DIFF
  echo "$s $f"
done
echo "== present files under src/ blake3-r2/ not in prev =="
for d in src blake3-r2; do (cd "$P" && find "$d" -type f | sort) | while read -r f; do [ -f "$V/$f" ] || echo "NEW $f"; done; done
echo "== CRLF / BOM =="
grep -rlI $'\r' "$P/blake3-r2" "$P/submission-note-r2.md" | wc -l
head -c3 "$P/blake3-r2/proof.md" | od -An -tx1
head -c3 "$P/submission-note-r2.md" | od -An -tx1
echo "== sizes =="
wc -l -c "$P/blake3-r2/proof.md" "$P/blake3-r2/claim.json" "$P/submission-note-r2.md" "$V/blake3-r2/proof.md" "$V/blake3-r2/claim.json" "$V/submission-note-r2.md"
} > "$O" 2>&1
wc -l "$O"
