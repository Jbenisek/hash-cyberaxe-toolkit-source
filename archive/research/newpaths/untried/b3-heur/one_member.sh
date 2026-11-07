#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# one_member.sh E1 ETA  (untried/b3-heur; research only): one member of an arbitrary class, full stdout/stderr kept.
set -uo pipefail
D="${HASHCYBERAXE_WORKSPACE}/research/newpaths/untried/b3-heur"
B="$HOME/hashsmash/pkg7_count/bin/pair_calc_sub"
S8="00010000:0,00020000:0,00000001:0,00000002:1,00000404:1,00000808:1,01001008:0,02002040:0"
E1=$1; ETA=$2
OMP_NUM_THREADS=1 nice -n 5 "$B" fdb77cfd 0a08818b fffffff8 8127c181 $ETA "$D/beta_star.lst" 7af77f38 -rule $S8 -cube ffffffff $E1 -mode both > "$D/member_${E1}_${ETA}.out" 2> "$D/member_${E1}_${ETA}.err"
echo "rc $?"
