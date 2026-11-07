#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# lens EVERY FIGURE: sizes of evidence files, and sameness of copies with their sources
P="${HASHCYBERAXE_WORKSPACE}"/research
R="$P/pkg5/review"
O="$R/fig_ev1.out"
{
echo "== evidence files (lines bytes)"
for f in $(cd "$P/pkg5/evidence" && find . -type f | sort); do
  echo "$f $(wc -l < "$P/pkg5/evidence/$f") $(wc -c < "$P/pkg5/evidence/$f")"
done
echo "== followup copies against research/night/cheaper and research/evidence"
for f in $(cd "$P/pkg5/evidence/followup" && ls); do
  a="$P/pkg5/evidence/followup/$f"
  hit=""
  for c in "$P/night/cheaper/$f" "$P/evidence/night_cheaper_fu_$f" "$P/evidence/$f"; do
    if [ -f "$c" ]; then
      if cmp -s "$a" "$c"; then hit="$hit SAME:${c#$P/}"; else hit="$hit DIFF:${c#$P/}"; fi
    fi
  done
  echo "$f ->$hit"
done
echo "== pkg4 evidence against pkg5 evidence"
for f in $(cd "$P/pkg4/evidence" && find . -type f | sort); do
  if [ -f "$P/pkg5/evidence/$f" ]; then
    cmp -s "$P/pkg4/evidence/$f" "$P/pkg5/evidence/$f" && echo "same $f" || echo "DIFF $f"
  else
    echo "MISSING in pkg5: $f"
  fi
done
} > "$O" 2>&1
wc -l "$O"
