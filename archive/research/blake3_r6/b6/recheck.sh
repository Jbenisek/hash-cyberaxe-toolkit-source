
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}"/research/blake3_r6/b6
( ulimit -v 2500000; cd pkg/blake3/experiments; nice -n 10 python3 -B bsrho.py --ledger 2>&1 | grep -v '^{' | tail -14; nice -n 10 python3 -B bsrho.py --selftest 2>&1 | tail -12 )
( ulimit -v 2500000; cd ext; nice -n 10 python3 -B ref_regress.py "${HASHCYBERAXE_WORKSPACE}"/hash-smash ../pkg/blake3/experiments 2>&1 | head -4 )
( ulimit -v 2500000; nice -n 10 python3 -B appA.py | tee appA.out | tail -4 )
bash exp_run.sh
