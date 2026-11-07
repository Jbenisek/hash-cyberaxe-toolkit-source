#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# check2-1: regenerate the scout's CNFs from its generator (copied here) and compare hashes. Research only.
cd "${HASHCYBERAXE_WORKSPACE}/research/sha256grid/check2-1" || exit 1
S="${HASHCYBERAXE_WORKSPACE}/research/sha256grid/scout2-1"
date
command -v kissat python3; kissat --version; python3 --version; nproc; uptime
echo "--- other kissat processes on the machine (not mine, not touched):"
pgrep -a kissat || echo none
python3 gen_step1.py check
python3 gen_step1.py cnf c_base.cnf
python3 gen_step1.py cnf c_g8.cnf --row16 --gcopies=8
python3 gen_step1.py cnf c_g32.cnf --row16 --gcopies=32
python3 gen_step1.py cnf c_k1r16.cnf --row16 --copies=1
python3 gen_step1.py cnf c_k2.cnf --copies=2
for p in "base step1_base" "g8 step1_g8" "g32 step1_g32" "k1r16 step1_k1r16" "k2 step1_k2"; do
  set -- $p
  a=$(sha256sum c_$1.cnf | cut -c1-16); b=$(sha256sum $S/$2.cnf | cut -c1-16)
  echo "$1: mine $a scout $b $( [ "$a" = "$b" ] && echo SAME || echo DIFFERENT )"
done
