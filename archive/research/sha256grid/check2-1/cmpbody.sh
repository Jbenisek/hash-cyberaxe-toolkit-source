#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# compare CNF bodies (everything after the 'c' comment header line)
cd "${HASHCYBERAXE_WORKSPACE}/research/sha256grid/check2-1" || exit 1
S="${HASHCYBERAXE_WORKSPACE}/research/sha256grid/scout2-1"
for p in "base step1_base" "k1r16 step1_k1r16" "k2 step1_k2" "g8 step1_g8"; do
  set -- $p
  a=$(grep -v '^c' c_$1.cnf | sha256sum | cut -c1-16); b=$(grep -v '^c' $S/$2.cnf | sha256sum | cut -c1-16)
  echo "$1 body: mine $a scout $b $( [ "$a" = "$b" ] && echo SAME || echo DIFFERENT )  header-scout: $(head -1 $S/$2.cnf)"
done
