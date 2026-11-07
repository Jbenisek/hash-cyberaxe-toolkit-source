
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}/research/blake3_r3/pivotv2/pkg/blake3/experiments"
nice -n 10 python3 -B bsrho.py --ledger > ../../../ledger.out 2>&1
nice -n 10 python3 -B bsrho.py --loss > ../../../loss.out 2>&1
nice -n 10 python3 -B bsrho.py --selftest > ../../../selftest.out 2>&1; echo "selftest rc=$?" >> ../../../selftest.out
date > ../../../run_ledger.done
