#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# probe_solvers.sh - versions and statistics format of the installed solvers on a 3-variable toy CNF
D="${HASHCYBERAXE_WORKSPACE}"/research/newpaths/untried/ctr_alg
T="$D/toy.cnf"
printf 'p cnf 3 4\n1 2 0\n-1 2 0\n1 -2 3 0\n-2 -3 0\n' > "$T"
echo "== kissat"; kissat --version
kissat --time=10 "$T" | tail -n 40
echo "== cadical"; cadical --version
cadical -t 10 "$T" | tail -n 40
echo "== cms"; cryptominisat5 --version | head -n 5
printf 'p cnf 3 2\nx1 2 3 0\n1 2 0\n' > "$D/toy.xnf"
cryptominisat5 --maxtime 10 --verb 1 "$D/toy.xnf" | tail -n 60
rm -f "$T" "$D/toy.xnf"
