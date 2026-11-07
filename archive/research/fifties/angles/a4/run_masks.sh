#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# run_masks.sh - C3 condition depends only on the XOR masks of the lengths (a_L = s' + (t xor p), s', t free; K drops out).
# Sweep every pair mask {0,p}, p=1..127, and every triple {0,p,q}, 1<=p<q<=127, with no format constraint.
D="${HASHCYBERAXE_WORKSPACE}"/research/fifties/angles/a4
cd "$D" || exit 1
mkdir -p masks/tmp
job() {
  set -- $1
  f=masks/tmp/m_$1_$2.cnf
  if [ "$2" = 0 ]; then python3 c3cnf.py genset 55,$((55 ^ $1)) $f --notop > /dev/null
  else python3 c3cnf.py genset 55,$((55 ^ $1)),$((55 ^ $2)) $f --notop > /dev/null; fi
  r=$(kissat -q --time=60 $f | grep '^s ' | cut -c3-)
  rm -f $f
  echo "$1 $2 ${r:-UNKNOWN}"
}
export -f job
{ for p in $(seq 1 127); do echo "$p 0"; done; } | xargs -P 20 -I{} bash -c 'job "{}"' > masks/pairs.txt
echo "pairs: $(grep -c ' SATISFIABLE' masks/pairs.txt) SAT, $(grep -c UNSAT masks/pairs.txt) UNSAT, $(grep -c UNKNOWN masks/pairs.txt) UNKNOWN"
{ for p in $(seq 1 127); do for q in $(seq $((p+1)) 127); do echo "$p $q"; done; done; } | xargs -P 20 -I{} bash -c 'job "{}"' > masks/triples.txt
echo "triples: $(grep -c ' SATISFIABLE' masks/triples.txt) SAT, $(grep -c UNSAT masks/triples.txt) UNSAT, $(grep -c UNKNOWN masks/triples.txt) UNKNOWN"
grep ' SATISFIABLE' masks/triples.txt | head -20
