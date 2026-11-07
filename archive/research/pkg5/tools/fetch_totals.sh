#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# Copies of the night's per-beta files for the longer list of betas (all betas with k at most 14), which the
# night's scripts left in the WSL home only (~/hashsmash/night_main/scan/). Nothing is computed here.
# tools/pkg5_data.py reads a per-beta file from evidence/ in place of research/night/main/ when the copy in
# evidence/ holds more betas. The sum of each copy is printed next to the line of the night's own summary
# file (research/night/main/extend_totals.txt), which must agree.
#
#   wsl -d Ubuntu -- bash './research/pkg5/tools/fetch_totals.sh' [eta ...]
set -uo pipefail
PKG="${HASHCYBERAXE_WORKSPACE}/research/pkg5"
W="${HASHCYBERAXE_WORKSPACE}/research/night/main"
S="$HOME/hashsmash/night_main/scan"
mkdir -p "$PKG/evidence"
for eta in "${@:-e7c1815f e74181df}"; do
  for e in $eta; do
    f="$S/pinB_$e.total"
    [ -f "$f" ] || { echo "$e: no file in scan/"; continue; }
    pgrep -f "class_total.sh pinB .* $e " > /dev/null && { echo "$e: still being written, not copied"; continue; }
    sort "$f" > "$PKG/evidence/pinB_$e.total"
    awk -v e="$e" 'NF == 4 {s += $4; if ($4 > 0) n++} END {printf "%s: %d betas, %d with a part, sum %.1f\n", e, NR, n, s}' "$PKG/evidence/pinB_$e.total"
    grep "class $e:" "$W/extend_totals.txt" 2>/dev/null | tail -1 | sed 's/^/   night: /'
  done
done
