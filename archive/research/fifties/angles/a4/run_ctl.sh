#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# run_ctl.sh - controls for the UNSAT result: free-pin positive control {55,63}, pairs, no format constraint, full sweep.
D="${HASHCYBERAXE_WORKSPACE}"/research/fifties/angles/a4
cd "$D" || exit 1
mkdir -p ctl
one() {  # name set [flags]
  python3 c3cnf.py genset "$2" ctl/$1.cnf $3 > /dev/null
  kissat -q --time=600 ctl/$1.cnf > ctl/$1.out
  echo "$1 set=$2 $3 -> $(grep '^s ' ctl/$1.out)"
}
one pos_55_63 55,63
python3 c3cnf.py check 63 ctl/pos_55_63.out ctl/pos_55_63.cnf
for L in 47 59 61 62; do
  one pair_55_$L 55,$L
  one pair_63_$L 63,$L
  one trip_notop_$L 55,63,$L --notop
done
echo "sweep {55,63,L} --notop, L in 1..64:"
sat=""; uns=""; unk=""
for L in $(seq 1 64); do
  [ $L = 55 ] || [ $L = 63 ] && continue
  python3 c3cnf.py genset 55,63,$L ctl/sw.cnf --notop > /dev/null
  r=$(kissat -q --time=60 ctl/sw.cnf | grep '^s ')
  case "$r" in *UNSAT*) uns="$uns $L";; *SATIS*) sat="$sat $L";; *) unk="$unk $L";; esac
done
echo "SAT:$sat"; echo "UNSAT:$uns"; echo "UNKNOWN:$unk"
